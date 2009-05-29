import ctypes

O_CREAT = 0100
O_EXCL = 0200

S_IRUSR = 00400
S_IWUSR = 00200
S_IROTH = 00004

PROT_READ = 0x1
PROT_WRITE = 0x2
PROT_EXEC = 0x4

MAP_SHARED = 0x01
MAP_PRIVATE = 0x02

mod = ctypes.CDLL('librt.so')
mod.sem_open.restype = ctypes.c_void_p
mod.sem_wait.argtypes = [ctypes.c_void_p]
mod.sem_trywait.argtypes = [ctypes.c_void_p]
mod.sem_close.argtypes = [ctypes.c_void_p]
mod.sem_post.argtypes = [ctypes.c_void_p]

mod.mmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
mod.mmap.restype = ctypes.c_void_p
mod.munmap.argtypes = [ctypes.c_void_p, ctypes.c_int]

mod.write.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

sem_open = mod.sem_open
sem_close = mod.sem_close
sem_trywait = mod.sem_trywait
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

class PosixSemaphore(object):
	def __init__(self, name, init = False, value = 0, perm = 00662):
		self.init = init
		self.name = name
		if self.init:
			self.sem_p = sem_open(name, O_CREAT | O_EXCL, S_IROTH | S_IWUSR | S_IRUSR , value)
		else:
			self.sem_p = sem_open(name, 0)
				
		if self.sem_p is None:
			raise RuntimeError()

	def __del__(self):
		sem_close(self.sem_p)
		if self.init:
			sem_unlink(self.name)

	def wait(self):
		if 0 != sem_wait(self.sem_p):
			raise RuntimeError()

	def post(self):
		if 0 != sem_post(self.sem_p):
			raise RuntimeError()

	def trywait(self):
		return sem_trywait(self.sem_p)



class SharedMemory(object):
	def __init__(self, name, size, init = False, perms = 00662):
		self.init = init
		self.name = name
		self.size = size
		if self.init:
			self.shm_f = shm_open(name, O_CREAT | O_EXCL,  S_IROTH | S_IWUSR | S_IRUSR)
		else:
			self.shm_f = shm_open(name, 0, 0)


		if self.shm_f == -1:
			shm_unlink(name)
			raise RuntimeError()

		empty_buf = (ctypes.c_byte * size)()
		ptr = ctypes.cast(empty_buf, ctypes.c_void_p)

		print write(self.shm_f, ptr, size, 0), ptr, size

		self.shm_void = mmap(None, size, PROT_READ | PROT_WRITE, MAP_SHARED, self.shm_f, 0)
		if self.shm_void != None:
			raise RuntimeError()


	def __del__(self):
		shm_unlink(self.name)
