"""osys.v2x

This module acts as a wrapper around the C++ V2X DLL.  It provides classes
that enable conversion between binary and text representations of V2X messages.

There are two C++ shared libraries that provide access to the V2X functionality.
The first is for SAE J2735 MessageFrame messages, and is named
"v2xasn1_j2735_202007".  The second is for ETSI messages and is named
"v2xasn1_etsi".
This module is designed so that only the library being used is required to be
present.

The conversion functionality is implemented in one class per message type,
in class methods.  The class methods are consistent across all types, see
the documentation for _Message.  The class methods are:
    to_json
    from_json
    to_xml
    from_xml.
The classes are:
    MessageFrame (J2735 202007)
    CAM
    DENM
    SPATEM
    MAPEM
    IVIM
    SREM
    SSEM
"""    

import ctypes

# Load the V2X shared libraries.  If a library fails to load, save the
# exception.  If the user later tries to use that library, then we'll raise
# that same exception.
import platform
import os

if platform.system() == "Windows":
    _j2735_name = "v2xasn1_j2735_202007"
    _etsi_name = "v2xasn1_etsi"
elif platform.system() == "Darwin":
    _j2735_name = "libv2xasn1_j2735_202007.dylib"
    _etsi_name = "libv2xasn1_etsi.dylib"
else:
    _j2735_name = "libv2xasn1_j2735_202007.so"
    _etsi_name = "libv2xasn1_etsi.so"

try:
    v2xdllpath = os.getenv("V2XDLLPATH")
    if v2xdllpath:
        _j2735_name = os.path.join(v2xdllpath, _j2735_name)
        _etsi_name = os.path.join(v2xdllpath, _etsi_name)
except:
    pass

_j2735lib = None
_j2735lib_err = None
_etsilib = None
_etsilib_err = None

try:
    _j2735lib = ctypes.cdll.LoadLibrary(_j2735_name)   
except Exception as err:
    _j2735lib_err = err
    
try:
    _etsilib = ctypes.cdll.LoadLibrary(_etsi_name)
except Exception as err:
    _etsilib_err = err


def _raise_liberr(err):
    """Class decorator for a _Message subclass. If err is not None, this will
    set the conversion methods for the class to a function that will raise err
    when invoked.
    """
    def decorator(cls):
        if err is not None:
            def fn(*args):
                raise err
                
            fn = staticmethod(fn)
            cls._from_json = fn
            cls._to_json = fn
            cls._from_xml = fn
            cls._to_xml = fn
            cls._free = fn
         
        return cls
    return decorator    
    
def _set_fn_attrs(cls):
    """Class decorator for a _Message subclass to set all the function
        return types and argument types, after the class has been created
        and the functions assigned."""
    cls._set_fn_attrs()
    return cls
            

class _Message:
    """Base class for messages supporting the same set conversion methods.
    
    The four conversion methods for all subclasses are:
        from_json
        to_json
        from_xml
        to_xml

    Subclasses must set 5 attributes, which are used by the implementation of
    the conversion methods to do the conversion.  Each attribute represents the
    C function to invoke to carry out the operation:
        _from_json
        _to_json
        _from_xml
        _to_xml
        _free
    """
    _from_json = None
    _to_json = None
    _from_xml = None
    _to_xml = None
    _free = None
    
    @classmethod
    def _set_err_fn(cls, error_fn):
        """Set the functions all to the given error function, which should
            raise an error whenever called."""
        cls._from_json = error_fn
        cls._to_json = error_fn
        cls._from_xml = error_fn
        cls._to_xml = error_fn
        cls._free = error_fn
        
    @classmethod
    def from_json(cls, json_str, verbose=True):
        """Returns the binary encoding (as a Python buffer) of an input
        JSON document or a tuple consisting of an error code (int) and an
        error message (str))."""
                    
        if type(json_str) == str:
            # Convert to UTF-8 bytes
            json_str = json_str.encode()
            
        CPTR = ctypes.POINTER(ctypes.c_char)
        bindatptr = CPTR()
        datlen = ctypes.c_size_t()
        errmsg = ctypes.c_char_p()
        
        result = cls._from_json(json_str, ctypes.byref(bindatptr),
                                ctypes.byref(datlen), ctypes.byref(errmsg),
                                verbose)
        if result == 0:
            # return copy of bytes and free the data
            dat = bindatptr[0:datlen.value]
            cls._free(bindatptr)
            return dat
        else:
            # Extract error message, free the memory, return the error.
            errmsgstr = errmsg.value.decode()
            cls._free(errmsg)
            return result, errmsgstr
        
    @classmethod
    def from_xml(cls, xml_str, verbose=True):
        """Returns the binary encoding (as a Python buffer) of an input
        XML document or a tuple consisting of an error code (int) and an
        error message (str))."""
        CPTR = ctypes.POINTER(ctypes.c_char)
        bindatptr = CPTR()
        datlen = ctypes.c_size_t()
        errmsg = ctypes.c_char_p()        
        
        if type(xml_str) == str:
            # Convert to UTF-8 bytes
            xml_str = xml_str.encode()        
        
        result = cls._from_xml(xml_str, ctypes.byref(bindatptr),
                               ctypes.byref(datlen), ctypes.byref(errmsg),
                               verbose)
        if result == 0:
            # return copy of bytes and free the data
            dat = bindatptr[0:datlen.value]
            cls._free(bindatptr)
            return dat
        else:
            # Extract error message, free the memory, return the error.
            errmsgstr = errmsg.value.decode()
            cls._free(errmsg)
            return result, errmsgstr
        
    @classmethod
    def to_json(cls, dat, nbytes, verbose=True):
        """Returns a Python buffer containing the JSON representation of
        the input binary MessageFrame or a tuple consisting of an error code
        (int) and an error message (str))."""
        charstr = ctypes.c_char_p()
        errmsg = ctypes.c_char_p()
        
        result = cls._to_json(dat, nbytes, ctypes.byref(charstr),
                        ctypes.byref(errmsg), verbose)
        if result == 0:
            # Get a string representation of the text, using UTF-8 (I guess
            # that's the right encoding to use).  Then free the memory.
            text = charstr.value.decode()
            cls._free(charstr)
            return text
        else:
            # Extract error message, free the memory, return the error.
            errmsgstr = errmsg.value.decode()
            cls._free(errmsg)
            return result, errmsgstr
        
    @classmethod
    def to_xml(cls, dat, nbytes, verbose=True):
        """Returns a Python buffer containing the XML representation of
        the input binary MessageFrame or a tuple consisting of an error code
        (int) and an error message (str))."""
        charstr = ctypes.c_char_p()
        errmsg = ctypes.c_char_p()
        
        result = cls._to_xml(dat, nbytes, ctypes.byref(charstr),
                        ctypes.byref(errmsg), verbose)
        if result == 0:
            # Get a string representation of the text, using UTF-8 (I guess
            # that's the right encoding to use).  Then free the memory.
            text = charstr.value.decode()
            cls._free(charstr)
            return text
        else:
            # Extract error message, free the memory, return the error.
            errmsgstr = errmsg.value.decode()
            cls._free(errmsg)
            return result, errmsgstr
            
    @classmethod
    def _set_fn_attrs(cls):
        """This can be used to set the function attributes (parameter and return
        types) for the conversion functions.  Call it after setting _to_json,
        etc., in the class.  If the functions have been set to None (because
        the shared library was not loaded), this will do nothing.
        """
        
        def set_totext(fn):
            """Set attrs for "to text" fn's"""
            
            if fn is None:
                return
                
            fn.restype = ctypes.c_int
            fn.argtypes=[ctypes.POINTER(ctypes.c_char),
                                ctypes.c_size_t,
                                ctypes.POINTER(ctypes.c_char_p),
                                ctypes.POINTER(ctypes.c_char_p),
                                ctypes.c_bool]
            
        def set_tobin(fn):
            """Set attrs for "to binary" fn's"""
            
            if fn is None:                
                return
            fn.restype = ctypes.c_int
            fn.argtypes=[ctypes.c_char_p,
                        ctypes.POINTER(ctypes.POINTER(ctypes.c_char)),
                        ctypes.POINTER(ctypes.c_size_t),
                        ctypes.POINTER(ctypes.c_char_p),
                        ctypes.c_bool]
                        
        set_totext(cls._to_json)
        set_tobin(cls._from_json)
        set_totext(cls._to_xml)
        set_tobin(cls._from_xml)

            
@_raise_liberr(_j2735lib_err)
@_set_fn_attrs
class MessageFrame (_Message):
    """The MessageFrame class. SAE J2735 202007.
    
    The MessageFrame class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""
    
    if _j2735lib is not None:
        _from_json = _j2735lib.j2735_MessageFrame_from_json
        _to_json = _j2735lib.j2735_MessageFrame_to_json
        _from_xml = _j2735lib.j2735_MessageFrame_from_xml
        _to_xml = _j2735lib.j2735_MessageFrame_to_xml
        
        _free = _j2735lib.j2735_delete_array
        _free.restype = None

   
@_raise_liberr(_etsilib_err)
@_set_fn_attrs
class CAM (_Message):
    """The CAM class. ETSI EN 302 637-2.
    
    The CAM class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""

    if _etsilib is not None:
        _from_json = _etsilib.etsi_CAM_from_json
        _to_json = _etsilib.etsi_CAM_to_json
        _from_xml = _etsilib.etsi_CAM_from_xml
        _to_xml = _etsilib.etsi_CAM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None
    
 
@_raise_liberr(_etsilib_err)
@_set_fn_attrs
class DENM (_Message):
    """The DENM class. ETSI EN 302 637-3.
    
    The DENM class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""

    if _etsilib is not None:
        _from_json = _etsilib.etsi_DENM_from_json
        _to_json = _etsilib.etsi_DENM_to_json
        _from_xml = _etsilib.etsi_DENM_from_xml
        _to_xml = _etsilib.etsi_DENM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None

    
@_raise_liberr(_etsilib_err)
@_set_fn_attrs
class SPATEM (_Message):
    """The SPATEM class. ETSI TS 103 301.
    
    The SPATEM class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""

    if _etsilib is not None:
        _from_json = _etsilib.etsi_SPATEM_from_json
        _to_json = _etsilib.etsi_SPATEM_to_json
        _from_xml = _etsilib.etsi_SPATEM_from_xml
        _to_xml = _etsilib.etsi_SPATEM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None

   
@_raise_liberr(_etsilib_err)
@_set_fn_attrs
class MAPEM (_Message):
    """The MAPEM class. ETSI TS 103 301.

     The MAPEM class has no constructor: rather it offers four functions
     for converting messages from JSON or XML to a binary buffer and
     vice versa."""

    if _etsilib is not None:
        _from_json = _etsilib.etsi_MAPEM_from_json
        _to_json = _etsilib.etsi_MAPEM_to_json
        _from_xml = _etsilib.etsi_MAPEM_from_xml
        _to_xml = _etsilib.etsi_MAPEM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None

    
@_raise_liberr(_etsilib_err)
@_set_fn_attrs
class IVIM (_Message):
    """The IVIM class. ETSI TS 103 301.

    The IVIM class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""
    
    if _etsilib is not None:
        _from_json = _etsilib.etsi_IVIM_from_json
        _to_json = _etsilib.etsi_IVIM_to_json
        _from_xml = _etsilib.etsi_IVIM_from_xml
        _to_xml = _etsilib.etsi_IVIM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None

    
@_raise_liberr(_etsilib_err)
@_set_fn_attrs
class SREM (_Message):
    """The SREM class. ETSI TS 103 301.
    
    The SREM class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""
    
    if _etsilib is not None:
        _from_json = _etsilib.etsi_SREM_from_json
        _to_json = _etsilib.etsi_SREM_to_json
        _from_xml = _etsilib.etsi_SREM_from_xml
        _to_xml = _etsilib.etsi_SREM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None

@_raise_liberr(_etsilib_err)    
@_set_fn_attrs
class SSEM (_Message):
    """The SSEM class. ETSI TS 103 301.
    
    The SSEM class has no constructor: rather it offers four functions
    for converting messages from JSON or XML to a binary buffer and
    vice versa."""
    
    if _etsilib is not None:
        _from_json = _etsilib.etsi_SSEM_from_json
        _to_json = _etsilib.etsi_SSEM_to_json
        _from_xml = _etsilib.etsi_SSEM_from_xml
        _to_xml = _etsilib.etsi_SSEM_to_xml
        
        _free = _etsilib.etsi_delete_array
        _free.restype = None
