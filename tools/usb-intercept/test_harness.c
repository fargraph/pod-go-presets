/*
 * test_harness.c — GUI-free smoke test for libusb_intercept.
 * Links against a real libusb so the interposer's replacee symbols resolve at load,
 * proving the dylib loads under DYLD_INSERT_LIBRARIES, the constructor fires, and the
 * log path works. libusb_init/exit do not touch a device (no hardware needed).
 * See plans/usb-libusb-intercept/PLAN.md (Step 2 verification).
 */
#include <stdio.h>
extern int  libusb_init(void **ctx);   /* real sig: int libusb_init(libusb_context**) */
extern void libusb_exit(void *ctx);
int main(void) {
    void *ctx = NULL;
    int r = libusb_init(&ctx);
    printf("harness: libusb_init=%d ctx=%p\n", r, ctx);
    if (ctx) libusb_exit(ctx);
    return 0;
}
