/*
 * Copyright (c) 2019-2022 Objective Systems, Inc.
 *
 * This software is furnished under a license and may be used and copied
 * only in accordance with the terms of such license and with the
 * inclusion of the above copyright notice. This software or any other
 * copies thereof may not be provided or otherwise made available to any
 * other person. No title to and ownership of the software is hereby
 * transferred.
 *
 * The information in this software is subject to change without notice
 * and should not be construed as a commitment by Objective Systems, Inc.
 *
 * PROPRIETARY NOTICE
 *
 * This software is an unpublished work subject to a confidentiality agreement
 * and is protected by copyright and trade secret law.  Unauthorized copying,
 * redistribution or other use of this work is prohibited.
 *
 * The above notice of copyright on this source code product does not indicate
 * any actual or intended publication of such source code.
 *
 *****************************************************************************/
/**
 * @file rtJsonExternDefs.h
 * JSON external definitions macro.  This is used for Windows to properly
 * declare function scope within DLL's.
 */
#ifndef _RTJSONEXTERNDEFS_H_
#define _RTJSONEXTERNDEFS_H_

#ifdef _MSC_VER
#ifdef BUILDJSONDLL
#define EXTERNJSON   __declspec(dllexport)
#define EXTJSONCLASS __declspec(dllexport)
#elif defined (USEJSONLDLL)
#define EXTERNJSON   __declspec(dllimport)
#define EXTJSONCLASS __declspec(dllimport)
#endif /* BUILDJSONDLL */
#endif /* WIN32 */

#ifndef EXTERNJSON
#define EXTERNJSON
#define EXTJSONCLASS
#endif
#define EXTJSONMETHOD

#endif
