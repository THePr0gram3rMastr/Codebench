#
#
# vim: ts=4 sw=4 sts=0 noexpandtab:
#
import time 
import sys

class ProgressBar(object):
    def __init__(self, max = 100, size = 50, char = "#", caption = "Progress"):
        self.max = max
        self.value = 0
        self.caption = caption
        self.size = size
        self.start_time = time.time()
        self.char = char
        
        if self.max == 0:
            self.draw = self.__emptydraw__
        
        self.draw()

    def draw(self):

        now = time.time()
        if self.value != 0:
            remaining = ((now - self.start_time) / self.value) * (self.max - self.value)
        else:
            remaining = 0
        pos = self.size * self.value / self.max
        eta = "%3.1fs (%2.0f%%)" % (remaining, 100 * self.value / self.max)
        progress = self.char * pos + (self.size - pos) * " "
        progress_string = "[%s]" % (progress)
        eta_string = "ETA %s" % (eta)
        caption_string = " " +  self.caption
        sys.stderr.write("%s : %s %s\r" % (caption_string, progress_string, eta_string))
        if self.value >= self.max:
            sys.stderr.write("\n -- TOTAL TIME  : %2.4fs -- \n" % (now - self.start_time))

    def __emptydraw__(self):
        pass

    def __call__(self, update = 1):
        self.update(update = update)

    def update(self, update = 1):
        uvalue = self.value + update
        self.value = min(uvalue, self.max)
        self.draw()

    def set_value(self, value):
        self.value = min(value, sefl.max)
        self.draw()

class Timer(object):
        total = 0
        t = None
        n = 0
        def __enter__(self):
            self.start()

        def __exit__(self, typ, value, traceback):
            self.stop()

        def start(self):
            if self.t is None:
                self.t = time.time()
                self.n += 1
            else:
                raise RuntimeError("Timer already started")

        def stop(self):
            if self.t is not None:
                self.total = time.time() - self.t
                self.t = None
            else:
                raise RuntimeError("Timer not started")

        def mean(self):
            return self.total / self.n

        def reset(self):
            self.n = self.total = 0

if __name__ == "__main__":
    a = ProgressBar()
    for i in range(100):
        time.sleep(0.02)
        a()
