import ctypes
import ctypes.util
import string
from random import choice
import time
import calendar
import threading


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

mod.mmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
mod.mmap.restype = ctypes.c_void_p
mod.munmap.argtypes = [ctypes.c_void_p, ctypes.c_int]

mod.write.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]


sem_open = mod.sem_open
sem_close = mod.sem_close
sem_trywait = mod.sem_trywait
sem_timedwait = mod.sem_timedwait
sem_wait = mod.sem_wait
sem_post = mod.sem_post
sem_unlink = mod.sem_unlink
sem_init = mod.sem_init

shm_open = mod.shm_open
shm_unlink = mod.shm_unlink
mmap = mod.mmap
munmap = mod.munmap
close = mod.close
write = mod.write
ftell = mod.ftell
fseek = mod.fseek
rewind = mod.rewind


typecode_to_type = {
	'c': ctypes.c_char,  'u': ctypes.c_wchar,
	'b': ctypes.c_byte,  'B': ctypes.c_ubyte,
	'h': ctypes.c_short, 'H': ctypes.c_ushort,
	'i': ctypes.c_int,   'I': ctypes.c_uint,
	'l': ctypes.c_long,  'L': ctypes.c_ulong,
	'f': ctypes.c_float, 'd': ctypes.c_double
	}

def gen_random_name(size):
	return ''.join([choice(string.letters + string.digits) for i in range(1, size)])


class NamedSemaphore(object):
	def __init__(self, name = None, create = False):
		if name is None:
			name = 'py' + gen_random_name(10)
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
	
	def timedwait(self, sec, nsec = 0):
		abssec = calendar.timegm(time.gmtime()) + sec
		return sem_timedwait(self.sem_p, ctypes.pointer(timespec(abssec, 0))) == 0


class NamedBuffer(object):
	owner = False
	__size__ = 0
	__address__ = -1
	def __init__(self, size, name = None,  create = False, perms = 00662, offset = 0):
		if name is None:
			name = name = 'py' + gen_random_name(10)
		self.name = name
		self.owner = create
		self.__size__ = size
		if create:
		    cflag, perms, mflag = O_RDWR | O_CREAT | O_EXCL, S_IROTH | S_IWUSR | S_IRUSR, PROT_READ | PROT_WRITE
		else:
		    cflag, perms, mflag = O_RDONLY, 0, PROT_READ 
		
		shm_f = shm_open(name, cflag, perms)
		if shm_f == -1:
		    raise RuntimeError()
		
		if create:
			write(shm_f, ctypes.cast(ctypes.c_char_p("\x00" * size),
											ctypes.c_void_p), size)
		
		self.__address__ = mmap(None, size, mflag, MAP_SHARED, shm_f, offset)
		close(shm_f)
		if self.__address__ == None:
			if self.shm_f != -1:
			    shm_unlink(self.name)
			raise RuntimeError()
		self.owner = create
	
	def buffer_info(self):
		return (self.__address__, self.__size__)
	
	def __del__(self):
		if self.owner:
		    shm_unlink(self.name)
		munmap(self.__address__, self.__size__)


class NamedArray(object):
	class Headers(ctypes.Structure):
		_fields_ = [('data_type', ctypes.c_char),
					('data_size', ctypes.c_long)]
	def __init__(self, data_type, data_size, name = None):
		self.__data_type__ = typecode_to_type[data_type]
		raw_size = ctypes.sizeof(self.__data_type__) * data_size
		full_size = ctypes.sizeof(self.Headers) + raw_size
		if name is None:
			self.__buffer__ = NamedBuffer(full_size, create = True)
		else:
			self.__buffer__ = NamedBuffer(full_size, name = name, create = False)
		
		self.name = self.__buffer__.name
		address, buffer_size = self.__buffer__.buffer_info()
		
		array_type = self.__data_type__ * data_size
		self.data = array_type.from_address(address + ctypes.sizeof(self.Headers))
		
		if name is None:
			self.__headers__ = self.Headers.from_address(address)
			self.__headers__.data_type = data_type
			self.__headers__.data_size = raw_size / ctypes.sizeof(self.__data_type__)
	
	def __len__(self):
		return len(self.data)
	
	@classmethod
	def from_name(cls, name):
		buffer = NamedBuffer(ctypes.sizeof(cls.Headers), create = False, name = name)
		address, buffer_size = buffer.buffer_info()
		hdr = cls.Headers.from_address(address)
		return cls(hdr.data_type, hdr.data_size, name = name)


class SemaphoreThread(threading.Thread):
	def __init__(self, sem, wait = 2):
		super(SemaphoreThread, self).__init__()
		self.sem = sem
		self.wtime = wait
		self.stopevent = threading.Event()
		self.semEvent = events.ThreadedEvent()
	
	def run(self):
		while not self.stopevent.isSet():
			if self.sem.timedwait(self.wtime):
				self.semEvent()
	
	def stop(self):
		self.stopevent.set()

