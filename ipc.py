import ctypes
import ctypes.util
import time
import calendar
import threading

import codebench.events
import codebench.aleatory

class timespec(ctypes.Structure):
    _fields_ = [('secs', ctypes.c_long),
                ('nsecs', ctypes.c_long),
               ]

O_CREAT = 0100
O_EXCL = 0200

S_IRUSR = 00400
S_IWUSR = 00200
S_IROTH = 00004

O_RDONLY = 00
O_RDWR = 02

PROT_READ = 0x1
PROT_WRITE = 0x2
PROT_EXEC = 0x4

MAP_SHARED = 0x01
MAP_PRIVATE = 0x02

SEEK_END = 2
SEEK_SET = 0

mod = ctypes.CDLL(ctypes.util.find_library('rt'))
mod.sem_open.restype = ctypes.c_void_p
mod.sem_wait.argtypes = [ctypes.c_void_p]
mod.sem_trywait.argtypes = [ctypes.c_void_p]
mod.sem_close.argtypes = [ctypes.c_void_p]
mod.sem_post.argtypes = [ctypes.c_void_p]

mod.sem_timedwait.argtypes = [ctypes.c_void_p, ctypes.POINTER(timespec)]

sem_open = mod.sem_open
sem_close = mod.sem_close
sem_trywait = mod.sem_trywait
sem_timedwait = mod.sem_timedwait
sem_wait = mod.sem_wait
sem_post = mod.sem_post
sem_unlink = mod.sem_unlink
sem_init = mod.sem_init


class NamedSemaphore(object):
	def __init__(self, name = None, create = False):
		if name is None:
			name = 'py' + codebench.aleatory.random_string(10)
		self.owner = create
		self.name = name
		if create:
			self.sem_p = sem_open(name, O_CREAT | O_EXCL, S_IROTH | S_IWUSR | S_IRUSR , 0)
		else:
			self.sem_p = sem_open(name, 0)
		if self.sem_p is None:
			raise RuntimeError()
	
	def __del__(self):
		sem_close(self.sem_p)
		if self.owner:
			sem_unlink(self.name)
	
	def wait(self):
		if 0 != sem_wait(self.sem_p):
			raise RuntimeError()
	
	def post(self):
		if 0 != sem_post(self.sem_p):
			raise RuntimeError()
	
	def trywait(self):
		return sem_trywait(self.sem_p) == 0
	
	def timedwait(self, sec):
		abssec = calendar.timegm(time.gmtime()) + sec
		return sem_timedwait(self.sem_p, ctypes.pointer(timespec(abssec, 0))) == 0



class SemaphoreThread(threading.Thread):
	def __init__(self, sem, wait = 2):
		super(SemaphoreThread, self).__init__()
		self.sem = sem
		self.wtime = wait
		self.stopevent = threading.Event()
		self.semEvent = codebench.events.ThreadedEvent()
	
	def run(self):
		while not self.stopevent.isSet():
			if self.sem.timedwait(self.wtime):
				self.semEvent()
	
	def stop(self):
		self.stopevent.set()

