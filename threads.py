import threading
import Queue
import traceback

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
				if evt is not None:
					evt.set()
			except Exception, err:
			    traceback.print_exc()
			o = self.q.get()
	
	def __callInThread__(self, fct, args, kw, evt):
		if not callable(fct):
			raise RuntimeError("first argument must be callable")
		self.q.put((fct, args, kw, evt))

	def __call__(self, fct, *args, **kw):
		self.__callInThread__(fct, args, kw, None)
	
	def blockingCall(self, fct, *args, **kw):
		evt = threading.Event()
		self.__callInThread__(fct, args, kw, evt)
		evt.wait()
	
	def stop(self, join = True):
		self.stopevent = True
		if self.q.empty():
			self.q.put(None)
		self.join()
