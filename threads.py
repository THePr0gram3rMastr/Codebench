import threading
import Queue
import traceback
from functools import wraps

class Worker(threading.Thread):
	stopevent = False
	def __init__(self, *args, **kw):
		threading.Thread.__init__(self, *args, **kw)
		self.q = Queue.Queue()
		self.start()

	def run(self):
		o = self.q.get()
		while not self.stopevent:
			fct, args, kw, evt = o
			try:
				fct(*args, **kw)
			except:
				traceback.print_exc()
			finally:
				if evt is not None:
					evt.set()
			o = self.q.get()
		q = self.q
		self.q = None
		fct, args, kw, evt = o
		if evt is not None:
			evt.set()
		while not q.empty():
			fct, args, kw, evt = q.get()
			if evt is not None:
				evt.set()
			
	
	def __callInThread__(self, fct, args, kw, evt):
		if not callable(fct):
			raise RuntimeError("first argument must be callable")
		if self.q is None:
		    return
		self.q.put((fct, args, kw, evt))

	def __call__(self, fct, *args, **kw):
		self.__callInThread__(fct, args, kw, None)
	
	def blockingCall(self, fct, *args, **kw):
		evt = threading.Event()
		self.__callInThread__(fct, args, kw, evt)
		evt.wait()
	
	def stop(self, join = True):
		self.stopevent = True
		if self.q is not None and self.q.empty():
			self.q.put((None, None, None, None))
		self.join()

class inworker(object):
	"""
	If your application have "inworker" thread you should 
	clean the worker threads by calling the cleanup function
	"""
	workers = {}
	worker = None
	def __init__(self, name, worker_type = Worker):
		self.name = name
		self.worker_type = worker_type

	def __call__(self, fct):
		@wraps(fct)
		def wrapper(*args, **kw):
			if self.worker is None:
				self.worker = self.worker_type()
				self.workers[self.name] = self.worker
			self.worker(fct, *args, **kw)
                return wrapper

	@classmethod
	def cleanup(cls):
		while len(cls.workers) != 0:
			n, w = cls.workers.popitem()
			w.stop()


try:
	import pycuda.driver as drv
	import pycuda.tools
	drv.init()
	class CudaWorker(Worker):
                def __init__(self, deviceId = None):
                        self.deviceId = deviceId
		def run(self):
                        if deviceId is None:
			        dev = pycuda.tools.get_default_device()
                        else:
                                pass
			ctx = dev.make_context()
			Worker.run(self)
			ctx.pop()
	incuda = inworker("cuda", worker_type = CudaWorker)                
except:
	traceback.print_exc()
