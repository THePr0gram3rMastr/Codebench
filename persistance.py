from __future__ import with_statement
import numpy as np
import os

from itertools import izip


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




