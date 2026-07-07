/*
 * libusb_intercept.c — DYLD interposer that logs POD Go Edit's libusb traffic.
 *
 * Why this exists: POD Go Edit drives the unit through its bundled libusb. Interposing
 * libusb's transfer calls in userspace captures the full, already-de-framed protocol
 * payloads with SIP left on and no second machine (see plans/usb-libusb-intercept/PLAN.md).
 *
 * Step 0 established the app is ASYNC-FIRST: bulk I/O rides libusb_submit_transfer() +
 * completion callbacks; the only sync transfer it uses is libusb_control_transfer(). So the
 * async callback trampoline is the core; the sync control hook doubles as an injection
 * smoke-test (fires on connect but does NOT carry the preset stream).
 *
 * Build (must be x86_64 to co-load into the Rosetta-translated app):
 *   clang -arch x86_64 -dynamiclib -O2 -Wall -Wl,-undefined,dynamic_lookup \
 *         -o libusb_intercept.dylib libusb_intercept.c
 *   codesign --force --sign - libusb_intercept.dylib        # ad-hoc; Apple Silicon needs a sig
 *
 * Use (launch the re-signed copy's executable directly so env vars propagate):
 *   DYLD_INSERT_LIBRARIES=/abs/libusb_intercept.dylib \
 *   PODGO_USB_LOG=/abs/run.log \
 *     "/abs/POD Go Edit (RE).app/Contents/MacOS/POD Go Edit"
 *
 * Log format: one record per line, whitespace-delimited fields, hex payload at the end:
 *   <idx> t=<unixsec> <TAG> ep=0x.. dir=IN|OUT type=CTRL|BULK|INTR|.. len=.. act=.. st=.. \
 *         [bmRT=.. bReq=.. wVal=.. wIdx=..] data=<hex|->
 *   TAGs: INJECTED (load marker), SUBMIT (async submit; OUT payload present, IN pending),
 *         COMPLETE (async completion; IN payload present), CTRL (sync control_transfer).
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <dlfcn.h>
#include <time.h>
#include <unistd.h>

/* ---- minimal libusb 1.0 ABI (x86_64 field offsets verified against libusb.h) ---- */
typedef struct libusb_device_handle libusb_device_handle;
struct libusb_transfer;
typedef void (*libusb_transfer_cb_fn)(struct libusb_transfer *);

struct libusb_iso_packet_descriptor {
    unsigned int length;
    unsigned int actual_length;
    int status;
};

struct libusb_transfer {
    libusb_device_handle *dev_handle;   /* 0  */
    uint8_t flags;                      /* 8  */
    unsigned char endpoint;             /* 9  */
    unsigned char type;                 /* 10 */
    unsigned int timeout;               /* 12 */
    int status;                         /* 16 (enum libusb_transfer_status) */
    int length;                         /* 20 */
    int actual_length;                  /* 24 */
    libusb_transfer_cb_fn callback;     /* 32 */
    void *user_data;                    /* 40 */
    unsigned char *buffer;              /* 48 */
    int num_iso_packets;                /* 56 */
    struct libusb_iso_packet_descriptor iso_packet_desc[]; /* 64 */
};

/* real functions we interpose — declared extern so &sym resolves the genuine address for
 * the __interpose tuple (bound at load via -undefined dynamic_lookup). We never CALL these
 * names directly (that would recurse); we call through dlsym'd pointers instead. */
extern int libusb_submit_transfer(struct libusb_transfer *);
extern int libusb_control_transfer(libusb_device_handle *, uint8_t, uint8_t, uint16_t,
                                   uint16_t, unsigned char *, uint16_t, unsigned int);

static const char *type_name(int t) {
    switch (t) { case 0: return "CTRL"; case 1: return "ISO"; case 2: return "BULK";
                 case 3: return "INTR"; case 4: return "STREAM"; default: return "?"; }
}

#define DYLD_INTERPOSE(_repl, _replee) \
  __attribute__((used)) static struct { const void *r; const void *e; } \
  _interpose_##_replee __attribute__((section("__DATA,__interpose"))) = \
  { (const void *)(unsigned long)&_repl, (const void *)(unsigned long)&_replee };

/* ---------------- logging ---------------- */
static FILE *g_log = NULL;
static pthread_mutex_t g_log_mx = PTHREAD_MUTEX_INITIALIZER;
static pthread_once_t g_log_once = PTHREAD_ONCE_INIT;
static long g_idx = 0;

static void log_open(void) {
    const char *p = getenv("PODGO_USB_LOG");
    if (!p || !*p) p = "/tmp/podgo_usb.log";
    g_log = fopen(p, "a");
    if (g_log) {
        struct timespec ts; clock_gettime(CLOCK_REALTIME, &ts);
        fprintf(g_log, "# podgo_usb_intercept open pid=%d t=%ld.%09ld\n",
                (int)getpid(), (long)ts.tv_sec, (long)ts.tv_nsec);
        fflush(g_log);
    }
}

static double now_s(void) {
    struct timespec ts; clock_gettime(CLOCK_REALTIME, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static void emit(const char *tag, int ep, int type, int length, int actual, int status,
                 const unsigned char *data, int datalen, const char *extra) {
    pthread_once(&g_log_once, log_open);
    if (!g_log) return;
    pthread_mutex_lock(&g_log_mx);
    int dir_in = (ep & 0x80) ? 1 : 0;
    fprintf(g_log, "%ld t=%.6f %s ep=0x%02x dir=%s type=%s len=%d act=%d st=%d",
            g_idx++, now_s(), tag, ep & 0xff, dir_in ? "IN" : "OUT",
            type_name(type), length, actual, status);
    if (extra && *extra) fprintf(g_log, " %s", extra);
    fputs(" data=", g_log);
    if (data && datalen > 0) {
        static const char hx[] = "0123456789abcdef";
        for (int i = 0; i < datalen; i++) {
            fputc(hx[data[i] >> 4], g_log);
            fputc(hx[data[i] & 0xf], g_log);
        }
    } else {
        fputc('-', g_log);
    }
    fputc('\n', g_log);
    fflush(g_log);
    pthread_mutex_unlock(&g_log_mx);
}

/* ------------- transfer* -> original callback map (thread-safe) ------------- */
#define NBUCKETS 1024
struct node { struct libusb_transfer *key; libusb_transfer_cb_fn cb; struct node *next; };
static struct node *g_map[NBUCKETS];
static pthread_mutex_t g_map_mx = PTHREAD_MUTEX_INITIALIZER;

static inline unsigned bucket(struct libusb_transfer *t) {
    return (unsigned)(((uintptr_t)t >> 4) & (NBUCKETS - 1));
}
static void map_put(struct libusb_transfer *t, libusb_transfer_cb_fn cb) {
    unsigned b = bucket(t);
    pthread_mutex_lock(&g_map_mx);
    for (struct node *n = g_map[b]; n; n = n->next)
        if (n->key == t) { n->cb = cb; pthread_mutex_unlock(&g_map_mx); return; }
    struct node *n = (struct node *)malloc(sizeof(*n));
    if (n) { n->key = t; n->cb = cb; n->next = g_map[b]; g_map[b] = n; }
    pthread_mutex_unlock(&g_map_mx);
}
static libusb_transfer_cb_fn map_take(struct libusb_transfer *t) {
    unsigned b = bucket(t);
    libusb_transfer_cb_fn cb = NULL;
    pthread_mutex_lock(&g_map_mx);
    for (struct node **pp = &g_map[b]; *pp; pp = &(*pp)->next)
        if ((*pp)->key == t) { struct node *d = *pp; cb = d->cb; *pp = d->next; free(d); break; }
    pthread_mutex_unlock(&g_map_mx);
    return cb;
}

/* How we call the originals: dyld interposition exempts references from THIS image, so a
 * direct call to libusb_submit_transfer()/libusb_control_transfer() by name reaches the real
 * function (verified via DYLD_PRINT_INTERPOSING: "replaced <real> with <real> in this dylib").
 * NOTE: do NOT use dlsym(RTLD_NEXT/DEFAULT) to find the originals — dyld interposes dlsym
 * results too, so dlsym would hand back OUR hook and recurse infinitely. */

/* ------------- completion trampoline ------------- */
static void my_transfer_callback(struct libusb_transfer *t) {
    libusb_transfer_cb_fn orig = map_take(t);
    if (t)
        emit("COMPLETE", t->endpoint, t->type, t->length, t->actual_length,
             t->status, t->buffer, t->actual_length, NULL);
    if (orig) {
        t->callback = orig;   /* restore BEFORE calling, in case orig re-submits t */
        orig(t);
    }
}

/* ------------- interposed entry points ------------- */
static int my_libusb_submit_transfer(struct libusb_transfer *t) {
    if (t && t->callback && t->callback != my_transfer_callback) {
        int dir_in = (t->endpoint & 0x80) ? 1 : 0;
        map_put(t, t->callback);
        emit("SUBMIT", t->endpoint, t->type, t->length, 0, 0,
             dir_in ? NULL : t->buffer, dir_in ? 0 : t->length, NULL);
        t->callback = my_transfer_callback;
    }
    return libusb_submit_transfer(t);   /* direct name = the real one (see note above) */
}
DYLD_INTERPOSE(my_libusb_submit_transfer, libusb_submit_transfer)

static int my_libusb_control_transfer(libusb_device_handle *h, uint8_t bmRequestType,
        uint8_t bRequest, uint16_t wValue, uint16_t wIndex,
        unsigned char *data, uint16_t wLength, unsigned int timeout) {
    int ret = libusb_control_transfer(h, bmRequestType, bRequest, wValue, wIndex,
                                      data, wLength, timeout);
    int dir_in = (bmRequestType & 0x80) ? 1 : 0;
    int nbytes = dir_in ? (ret > 0 ? ret : 0) : wLength;
    char extra[96];
    snprintf(extra, sizeof(extra), "bmRT=0x%02x bReq=0x%02x wVal=0x%04x wIdx=0x%04x",
             bmRequestType, bRequest, wValue, wIndex);
    emit("CTRL", dir_in ? 0x80 : 0x00, 0 /*CTRL*/, wLength, nbytes, ret, data, nbytes, extra);
    return ret;
}
DYLD_INTERPOSE(my_libusb_control_transfer, libusb_control_transfer)

/* ------------- prove injection even before any libusb call ------------- */
__attribute__((constructor))
static void on_load(void) {
    emit("INJECTED", 0, -1, 0, 0, 0, NULL, 0, "libusb_intercept loaded");
    /* PODGO_USB_DIAG=1: confirm the direct-call binding is the REAL function, not our hook
     * (if &libusb_submit_transfer == &my_libusb_submit_transfer we'd recurse — must differ). */
    if (getenv("PODGO_USB_DIAG")) {
        void *mine = (void *)&my_libusb_submit_transfer;
        void *byname = (void *)&libusb_submit_transfer;      /* what our direct call reaches */
        void *viadlsym = dlsym(RTLD_DEFAULT, "libusb_submit_transfer");
        fprintf(stderr, "DIAG submit: mine=%p byname=%p dlsym=%p  %s\n", mine, byname, viadlsym,
                (byname != mine) ? "OK(byname!=mine, no recursion)" : "BAD(byname==mine!)");
    }
}
