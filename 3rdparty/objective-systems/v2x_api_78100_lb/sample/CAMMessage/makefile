# makefile to build generated files

include ../../platform.mk

OSROOTDIR = ../..
LIBDIR = $(OSROOTDIR)/debug/lib
RTSRCDIR = $(OSROOTDIR)/rtsrc
RTXSRCDIR = $(OSROOTDIR)/rtxsrc
BERSRCDIR = $(OSROOTDIR)/rtbersrc
PERSRCDIR = $(OSROOTDIR)/rtpersrc

COMFLAGS = -D_TRACE $(CBLDTYPE_) $(CVARSMTD_) $(MCFLAGS) -DCPP -D_V2X
CFLAGS	= $(COMFLAGS) $(CFLAGS_)
CCFLAGS = $(COMFLAGS) $(CCFLAGS_)
IPATHS = -I. -I $(OSROOTDIR)/debug/src/etsi -I$(OSROOTDIR) $(IPATHS_)
LINKOPT	= $(LINKOPTDYN_)
LPATHS = $(LPPFX)$(LIBDIR)

all : reader$(EXE) writer$(EXE)

reader$(EXE) : reader$(OBJ) $(LIBDIR)/$(LIBPFX)v2xasn1_etsi$(IMP)
	$(LINK) reader$(OBJ) $(LINKOPT) $(LPATHS) $(LLPFX)v2xasn1_etsi$(LLEXT)

writer$(EXE) : writer$(OBJ) $(LIBDIR)/$(LIBPFX)v2xasn1_etsi$(IMP)
	$(LINK) writer$(OBJ) $(LINKOPT) $(LPATHS) $(LLPFX)v2xasn1_etsi$(LLEXT)

reader$(OBJ): reader.cpp ../../debug/src/etsi/CAM-PDU-Descriptions.h \
 ../../rtpersrc/asn1PerCppTypes.h ../../rtpersrc/asn1per.h \
 ../../rtsrc/asn1type.h ../../rtxsrc/rtxExternDefs.h \
 ../../rtxsrc/rtxSList.h ../../rtxsrc/rtxContext.h \
 ../../rtxsrc/rtxDList.h ../../rtxsrc/osSysTypes.h \
 ../../rtxsrc/rtxCommonDefs.h ../../rtxsrc/osMacros.h \
 ../../rtxsrc/rtxStack.h ../../rtxsrc/rtxUTF8.h ../../rtsrc/asn1tag.h \
 ../../rtsrc/asn1ErrCodes.h ../../rtsrc/asn1version.h \
 ../../rtsrc/rtExternDefs.h ../../rtxsrc/rtxBitString.h \
 ../../rtsrc/rtContext.h ../../rtsrc/asn1CEvtHndlr.h \
 ../../rtxsrc/rtxError.h ../../rtxsrc/rtxErrCodes.h \
 ../../rtxsrc/rtxMemory.h ../../rtsrc/asn1CharSet.h \
 ../../rtxsrc/rtxBitEncode.h ../../rtxsrc/rtxBitDecode.h \
 ../../rtxsrc/rtxBuffer.h ../../rtxsrc/rtxDiagBitTrace.h \
 ../../rtxsrc/rtxMemBuf.h ../../rtxsrc/rtxPrintToStream.h \
 ../../rtsrc/asn1CppTypes.h ../../rtxsrc/rtxDiag.h \
 ../../rtsrc/asn1CppEvtHndlr64.h ../../rtsrc/asn1CppEvtHndlr.h \
 ../../rtsrc/ASN1Context.h ../../rtxsrc/OSRTContext.h \
 ../../rtxsrc/OSRTMsgBuf.h ../../rtxsrc/OSRTCtxtHolder.h \
 ../../rtxsrc/OSRTCtxtHolderIF.h ../../rtxsrc/OSRTMsgBufIF.h \
 ../../rtsrc/ASN1TOctStr.h ../../rtsrc/ASN1TOctStr64.h \
 ../../rtsrc/ASN1TObjId.h ../../debug/src/etsi/ITS-Container.h \
 ../../rtsrc/ASN1CBitStr.h ../../rtsrc/ASN1CSeqOfList.h

writer$(OBJ): writer.cpp ../../debug/src/etsi/CAM-PDU-Descriptions.h \
 ../../rtpersrc/asn1PerCppTypes.h ../../rtpersrc/asn1per.h \
 ../../rtsrc/asn1type.h ../../rtxsrc/rtxExternDefs.h \
 ../../rtxsrc/rtxSList.h ../../rtxsrc/rtxContext.h \
 ../../rtxsrc/rtxDList.h ../../rtxsrc/osSysTypes.h \
 ../../rtxsrc/rtxCommonDefs.h ../../rtxsrc/osMacros.h \
 ../../rtxsrc/rtxStack.h ../../rtxsrc/rtxUTF8.h ../../rtsrc/asn1tag.h \
 ../../rtsrc/asn1ErrCodes.h ../../rtsrc/asn1version.h \
 ../../rtsrc/rtExternDefs.h ../../rtxsrc/rtxBitString.h \
 ../../rtsrc/rtContext.h ../../rtsrc/asn1CEvtHndlr.h \
 ../../rtxsrc/rtxError.h ../../rtxsrc/rtxErrCodes.h \
 ../../rtxsrc/rtxMemory.h ../../rtsrc/asn1CharSet.h \
 ../../rtxsrc/rtxBitEncode.h ../../rtxsrc/rtxBitDecode.h \
 ../../rtxsrc/rtxBuffer.h ../../rtxsrc/rtxDiagBitTrace.h \
 ../../rtxsrc/rtxMemBuf.h ../../rtxsrc/rtxPrintToStream.h \
 ../../rtsrc/asn1CppTypes.h ../../rtxsrc/rtxDiag.h \
 ../../rtsrc/asn1CppEvtHndlr64.h ../../rtsrc/asn1CppEvtHndlr.h \
 ../../rtsrc/ASN1Context.h ../../rtxsrc/OSRTContext.h \
 ../../rtxsrc/OSRTMsgBuf.h ../../rtxsrc/OSRTCtxtHolder.h \
 ../../rtxsrc/OSRTCtxtHolderIF.h ../../rtxsrc/OSRTMsgBufIF.h \
 ../../rtsrc/ASN1TOctStr.h ../../rtsrc/ASN1TOctStr64.h \
 ../../rtsrc/ASN1TObjId.h ../../debug/src/etsi/ITS-Container.h \
 ../../rtsrc/ASN1CBitStr.h ../../rtsrc/ASN1CSeqOfList.h \
 ../../rtxsrc/rtxFile.h ../../rtxsrc/rtxPrint.h ../../rtxsrc/rtxHexDump.h

depends:
	g++ -MM -E $(IPATHS) reader.cpp
	g++ -MM -E $(IPATHS) writer.cpp

clean:
	$(RM) *$(OBJ)
	$(RM) *.exe
	$(RM) *.exp
	$(RM) *.pdb
	$(RM) *.map
	$(RM) *.lib
	$(RM) *.ilk
	$(RM) *~
	$(RM) writer$(EXE)
	$(RM) reader$(EXE)
	$(RM) message.dat
