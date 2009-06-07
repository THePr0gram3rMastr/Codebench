import codebench.aleatory
import mmap
import os
import ctypes

from lxml import etree

try:
    import scipy
except ImportError, err:
    scipy = None

try:
    import simplejson as json
except:
    json = None

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

    @classmethod
    def fromxml(cls, xmlstring):
        el = etree.fromstring(xmlstring)
        size = int(el.attrib.pop('size'))
        return cls(size, **el.attrib)

    if json is not None:
        @classmethod
        def fromjson(cls, jsonstring):
            dict = json.loads(jsonstring)
            size = dict.pop('size')
            cls(size, **dict)


    def __del__(self):
        if self.owner:
            os.remove(self.filename)

    def as_carray(self, ctype = ctypes.c_uint8):
        arr_type = ctype * len(self.buffer)
        return arr_type.from_buffer(self.buffer)

    if scipy is not None:
        def as_array(self, dtype = scipy.uint8):
            return scipy.frombuffer(self.buffer, dtype = dtype)




