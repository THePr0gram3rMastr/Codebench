from __future__ import with_statement

import os, \
       mmap

import aleatory
import ctypes


np = None
try:
    import numpy as np
except ImportError, err: pass

json = None
try:
    import json
except:
    try:
        import simplejson as json
    except ImportError, err: pass

etree = None
try:
    import lxml.etree as etree
except ImportError, err: pass


class SharedMemory(object):
    owner = False
    xml_tag = "shmem"
    xml_childs = []
    xml_attributes = ["filename", "size"]
    def __init__(self, size, filename = None):
        if filename is None:
            filename = os.path.join("/tmp", 'py' +  codebench.aleatory.random_string(10))
            self.owner = True
        self.filename = filename
        self.size = size
        with open(self.filename, 'a+') as file:
            if self.owner:
                file.write('\x00' * size)
                file.flush()
            self.buffer = mmap.mmap(file.fileno(), size)

    if etree is not None:
        @classmethod
        def fromxml(cls, xmlstring):
            el = etree.fromstring(xmlstring)
            size = int(el.attrib.pop('size'))
            filename = el.attrib.pop('filename')
            return cls(size, filename = filename)

    if json is not None:
        @classmethod
        def fromjson(cls, jsonstring):
            dct = json.loads(jsonstring)
            size = dct.pop('size')
            filename = str(dct.pop('filename'))
            return cls(size, filename = filename)


    def __del__(self):
        if self.owner:
            os.remove(self.filename)

    def ascarray(self, ctype = ctypes.c_uint8):
        arr_type = ctype * len(self.buffer)
        return arr_type.from_buffer(self.buffer)

    if np is not None:
        def asarray(self, dtype = scipy.uint8, shape = None):
            ary = scipy.frombuffer(self.buffer, dtype = dtype)
            if shape != None:
                ary.shape = shape
            return ary




