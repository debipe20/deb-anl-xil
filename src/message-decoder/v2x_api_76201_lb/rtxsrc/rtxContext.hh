#ifndef _RTXCONTEXT_HH_
#define _RTXCONTEXT_HH_

#include "rtxsrc/rtxBuffer.h"

#define OSCTXTINIT 0x1aa2a34a

/* bits of rtxCheckLicense */
#define LIC_RT     0x00
#define LIC_XER    0x01
#define LIC_PRO    0x02
#define LIC_BER    0x04
#define LIC_PER    0x08
#define LIC_CPP    0x10
#define LIC_NAS    0x20
#define LIC_INIT   0x80

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Finish with current license and free internal resources.
 * To avoid crashing your application:
 *    - Do not call this during an exit handler function registered with
 *       atexit().
 *    - Do not call this when another thread might concurrently trigger a 
 *       license check by invoking methods in the asn1c runtime.
 */
EXTERNRT void rtxLC();
EXTERNRT int rtxCL (OSCTXT* pctxt, int bits);
EXTERNRT int rtlci (OSCTXT* pctxt);
EXTERNRT int rtlps (OSCTXT* pctxt);
EXTERNRT char* rtlgsm (OSCTXT* pctxt);
EXTERNRT time_t rtlgextm (OSCTXT* pctxt);

#ifndef _NO_LICENSE_CHECK

#define LCHECK(pctxt,bits) \
{ int lcret = rtxCL(pctxt, bits); if (0 != lcret) return lcret; }

#define LCHECKBER(pctxt) \
{ int lcret = rtxCL(pctxt, LIC_BER); if (0 != lcret) return lcret; }

#define LCHECKPER(pctxt) \
{ int lcret = rtxCL(pctxt, LIC_PER); if (0 != lcret) return lcret; }

#define LCHECKXER(pctxt) \
{ int lcret = rtxCL(pctxt, LIC_XER); if (0 != lcret) return lcret; }

#define LCHECKNAS(pctxt) \
{ int lcret = rtxCL(pctxt, LIC_NAS); if (0 != lcret) return lcret; }

#define LCHECKCPP(pctxt) LCHECK(pctxt,LIC_CPP)

#define LCHECKIN(pctxt) rtlci(pctxt)

#define LCHECKX(pctxt) \
   { int lcret = rtxCL (pctxt, 0); if (0 != lcret) return lcret; }

#define LCHECKX2(pctxt) \
   { if (0 != rtxCL (pctxt, 0)) return NULL; }

#define LPRINTSTAT(pctxt) rtlps(pctxt)
#define LGETSTATMSG(pctxt) rtlgsm(pctxt)
#define LGETEXPTIME(pctxt) rtlgextm(pctxt)
#define LCLOSE() rtxLC()

#else /* if _NO_LICENSE_CHECK is defined */

#define LCHECK(pctxt,bits)
#define LCHECKBER(pctxt)
#define LCHECKPER(pctxt)
#define LCHECKXER(pctxt)
#define LCHECKNAS(pctxt)
#define LCHECKCPP(pctxt)
#define LCHECKIN(pctxt)
#define LCHECKX(pctxt)
#define LCHECKX2(pctxt)
#define LPRINTSTAT(pctxt)
#define LGETSTATMSG(pctxt) 0
#define LGETEXPTIME(pctxt) 0
#define LCLOSE()

#endif

#ifdef __cplusplus
}
#endif

#endif
