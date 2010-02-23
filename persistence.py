from __future__ import with_statement
import numpy as np
import scipy as sc
import os

from itertools import izip

import cPickle as pickle
import weakref


class DirectoryDB(object):
        def __init__(self, root, protocol = pickle.HIGHEST_PROTOCOL):
                self.root = os.path.expanduser(root)
                if not os.path.exists(self.root):
                        os.makedirs(self.root)
                self.protocol = protocol
                self.cache = {}

        def __iter__(self):
                return self.keys().__iter__()

        def __getitem__(self, key):
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


        def __setitem__(self, key, value):
                splitPath = os.path.split(key)
                dirpath = os.path.join(self.root, *splitPath[:-1])
                keypath = os.path.join(self.root, *splitPath)
                if not os.path.exists(dirpath):
                        os.makedirs(dirpath)
                with open(keypath, 'w') as f:
                        pickle.dump(value, f, protocol = self.protocol)
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


T_FILE = "t.npy"
C_FILE = "c.npy"
K_FILE = "k.npy"
U_FILE = "u.npy"
FP_FILE = "fp.npy"
IER_FILE = "ier.npy"
MSG_FILE = "msg.txt"


def saveSplines(directory, splines):
	((t, c, k), u), fp, ier, msg = splines[0]
	tlst = []
	clst = []
	klst = []
	ulst = []
	fplst = []
	ierlst = []
	msglst = []
	for i, (((t, c, k), u), fp, ier, msg)  in enumerate(splines):
		if ier < 0:
			continue
		os.mkdir(os.path.join(directory, str(i)))
		np.save(os.path.join(directory, str(i), T_FILE), t)
		np.save(os.path.join(directory, str(i), C_FILE), c)
		np.save(os.path.join(directory, str(i), K_FILE), k)
		np.save(os.path.join(directory, str(i), U_FILE), u)
		np.save(os.path.join(directory, str(i), FP_FILE), fp)
		np.save(os.path.join(directory, str(i), IER_FILE), ier)
		with open(os.path.join(directory, str(i), MSG_FILE), 'w') as f:
			f.write(msg)


                #np.save(os.path.join(directory, str(i), IER_FILE), ier)
		#tlst.append(t)
		#clst.append(c)
		#klst.append(k)
		#ulst.append(u)
		#fplst.append(fp)
		#ierlst.append(ier)
		#msglst.append(msg + '\n')
	#tarr = np.array(tlst)
	#carr = np.array(clst)
	#karr = np.array(klst)
	#uarr = np.array(ulst)
	#fparr = np.array(fplst)
	#ierarr = np.array(ierlst)
	
	#np.save(os.path.join(directory, T_FILE), tarr)
	#np.save(os.path.join(directory, C_FILE), carr)
	#np.save(os.path.join(directory, K_FILE), karr)
	#np.save(os.path.join(directory, U_FILE), uarr)
	#np.save(os.path.join(directory, FP_FILE), fparr)
	#np.save(os.path.join(directory, IER_FILE), ierarr)
	
	#with open(os.path.join(directory, MSG_FILE), 'w') as f:
	#	f.writelines(msglst)


def loadSplines(directory):
	return_value = []
	for subdir in os.listdir(directory):
		
		t = np.load(os.path.join(directory, subdir, T_FILE))
		c = np.load(os.path.join(directory, subdir, C_FILE))
		k = np.load(os.path.join(directory, subdir, K_FILE))
		u = np.load(os.path.join(directory, subdir, U_FILE))
		fp = np.load(os.path.join(directory, subdir, FP_FILE))
		ier = np.load(os.path.join(directory, subdir, IER_FILE))
		msg = open(os.path.join(directory, subdir, MSG_FILE)).read()
		return_value.append((([t, c, k], u), fp, ier, msg))

	return return_value

	#return [(([t, c, k], None), fp, ier, msg) for t, c, k,  fp, ier, msg in  izip(tarr, carr, karr, fparr, ierarr, msglst)]

def imread_path(path, first = 0, last = -1):
    """
      This method read a complete list of image(video) contained inside a directory. It sort the image and then read sequentially all the images in the directory. This script assume all images are the same size.
      Inputs:
        path - Path to the image directory
    """
    img_files = os.listdir(path)
    img_files.sort()
    img_list = [sc.misc.imread(os.path.join(path, imfile)) for imfile in img_files]
    return sc.array(img_list)


