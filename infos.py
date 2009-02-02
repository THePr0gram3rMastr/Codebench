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

    def __call__(self, update = 1):
        self.update(update = update)

    def update(self, update = 1):
        uvalue = self.value + update
        self.value = min(uvalue, self.max)
        self.draw()

    def set_value(self, value):
        self.value = min(value, sefl.max)
        self.draw()


if __name__ == "__main__":
    a = ProgressBar()
    for i in range(100):
        time.sleep(0.02)
        a()
