from __future__ import with_statement

import  os, \
        weakref

import cPickle as pickle

import scipy as sc

from itertools import izip



class DirectoryDB(object):
        @staticmethod
        def join_keys(args):
                if hasattr(args, "__iter__"):
                        key = ""
                        for k in args:
                                key = "%s/%s" % (key, k)
                        key = key[1:]
                else:
                        key = args
                return key

        
        def __init__(self, root, protocol = pickle.HIGHEST_PROTOCOL):
                self.root = os.path.expanduser(root)
                if not os.path.exists(self.root):
                        os.makedirs(self.root)
                self.protocol = protocol
                self.cache = {}

        def __len__(self):
                return len(self.keys())

        def __iter__(self):
                return self.keys().__iter__()

        def __getitem__(self, keys):
                key = self.join_keys(keys)
                if (key in self.cache):
                        item = self.cache[key]()
                        if item is not None:
                                return item

                keypath = os.path.join(self.root, key)
                if not os.path.exists(keypath):
                        raise KeyError(key)

                if os.path.isdir(keypath):
                        return DirectoryDB(keypath)

                with open(keypath) as f:
                        value = pickle.load(f)

                try:
                        self.cache[key] = weakref.ref(value)
                except TypeError, e:
                        pass
                return value


        def keys(self):
                return os.listdir(self.root)


        def __setitem__(self, keys, value):
                self.set(keys, value)

        def set(self, keys, value, protocol = None):
                key = self.join_keys(keys)
                if protocol is None:
                        protocol = self.protocol
                splitPath = os.path.split(key)
                dirpath = os.path.join(self.root, *splitPath[:-1])
                keypath = os.path.join(self.root, *splitPath)
                if not os.path.exists(dirpath):
                        os.makedirs(dirpath)
                with open(keypath, 'w') as f:
                        pickle.dump(value, f, protocol = protocol)
                try:
                        self.cache[key] = weakref.ref(value)
                except TypeError, e:
                    pass




        def __delitem__(self, key):
                if key in self.cache:
                        del self.cache[key]
                keypath = os.path.join(self.root, key)
                if not os.path.exists(keypath):
                        raise KeyError(key)
                os.remove(keypath)


def imread_path(path, first = 0, last = -1):
    """
      This method read a complete list of image(video) contained inside a directory. It sort the images and then read sequentially read all the images in the directory. This script assume all images are the same size.
      Inputs:
        path - Path to the image directory
    """
    img_files = os.listdir(path)
    img_files.sort()
    img_list = [sc.misc.imread(os.path.join(path, imfile)) for imfile in img_files]
    return sc.array(img_list)


