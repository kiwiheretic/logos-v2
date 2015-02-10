# utils.py
# This is to deal with unicode errors
# based on http://www.gossamer-threads.com/lists/python/python/780610
import codecs
import pdb

def replace_spc_error_handler(error): 
    # error is an UnicodeEncodeError/UnicodeDecodeError instance 
    # with these attributes: 
    # object = unicode object being encoded 
    # start:end = slice of object with error 
    # reason = error message 
    # Must return a tuple (replacement unicode object, 
    # index into object to continue encoding) 
    # or raise the same or another exception 
    return (u' ' * (error.end-error.start), error.end) 

codecs.register_error("replace_spc", replace_spc_error_handler) 