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
	for ((t, c, k), u), fp, ier, msg  in splines:
		tlst.append(t)
		clst.append(c)
		klst.append(k)
		ulst.append(u)
		fplst.append(fp)
		ierlst.append(ier)
		msglst.append(msg + '\n')
	tarr = np.array(tlst)
	carr = np.array(clst)
	karr = np.array(klst)
	uarr = np.array(ulst)
	fparr = np.array(fplst)
	ierarr = np.array(ierlst)
	
	np.save(os.path.join(directory, T_FILE), tarr)
	np.save(os.path.join(directory, C_FILE), carr)
	np.save(os.path.join(directory, K_FILE), karr)
	np.save(os.path.join(directory, U_FILE), uarr)
	np.save(os.path.join(directory, FP_FILE), fparr)
	np.save(os.path.join(directory, IER_FILE), ierarr)
	
	with open(os.path.join(directory, MSG_FILE), 'w') as f:
		f.writelines(msglst)


def loadSplines(directory):
	tarr = np.load(os.path.join(directory, T_FILE))
	carr = np.load(os.path.join(directory, C_FILE))
	karr = np.load(os.path.join(directory, K_FILE))
	uarr = np.load(os.path.join(directory, U_FILE))
	fparr = np.load(os.path.join(directory, FP_FILE))
	ierarr = np.load(os.path.join(directory, IER_FILE))
	with open(os.path.join(directory, MSG_FILE)) as f:
		msglst = f.readlines()

	return [(([t, c, k], u), fp, ier, msg) for t, c, k, u, fp, ier, msg in  izip(tarr, carr, karr, uarr, fparr, ierarr, msglst)]




