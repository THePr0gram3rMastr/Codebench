from __future__ import with_statement
import threading
import sys
import signal
import time
import logging
from codebench.events import ThreadsafeEvent

from codebench import opencv
import scipy

logger = logging.getLogger(__name__)


def cvCreateImageAs(img):
    return cv.cvCreateImage(cv.cvSize(img.width, img.height), img.depth,
                            img.nChannels)

class CVCapture(threading.Thread):
    def __init__(self, id):
        super(CVCapture, self).__init__()
        self.cam = opencv.cvCreateCameraCapture(id)
        self.stop_event = threading.Event()
        self.scFrameGrabbedEvent = ThreadsafeEvent()
        self.cvFrameGrabbedEvent = ThreadsafeEvent()
        self.grabFrame()

    def grabFrame(self):
        opencv.cvGrabFrame(self.cam)
        self.cvframe = opencv.cvRetrieveFrame(self.cam)
        self.scframe = self.cvframe.as_numpy_array()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Frame grabbed ...")

    def run(self):
        while not self.stop_event.isSet():
            self.grabFrame()
            try:
                self.cvFrameGrabbedEvent.dispatch(self.cvframe)
            except RuntimeError, err:
                print err
            try:
                self.scFrameGrabbedEvent.dispatch(self.scframe)
            except RuntimeError, err:
                print err

    def stop(self):
        self.stop_event.set()


class CVWindow(object):
    last_frame = None
    selection = None
    lbutton = False
    def __init__(self, wname = "Empty", poll = True):
        super(CVWindow, self).__init__()
        self.wname = wname
        self.cvMouseSelectionEvent = ThreadsafeEvent()
        self.scMouseSelectionEvent = ThreadsafeEvent()
        self.rlock = threading.Lock()
        self.poll = poll

        opencv.cvNamedWindow(wname)
        def mouse_callback(event, posx, posy, flag, param):
            try:
                self.__mouse_callback__(event, posx, posy, flag, param)
            except RuntimeError, err:
                pass
        self.__cv_mouse_callback__ = mouse_callback

        opencv.cvSetMouseCallback(wname, mouse_callback)

    def __mouse_callback__(self, event, posx, posy, flag, param):
        if event == opencv.CV_EVENT_LBUTTONDOWN:
            self.lbutton = True
            self.mouse_lbutton_pos = (posx, posy)
        elif event == opencv.CV_EVENT_LBUTTONUP:
            self.lbutton = False
            lastposx, lastposy = self.mouse_lbutton_pos
            startx, starty = min(lastposx, posx), min(lastposy, posy)
            lenx, leny = abs(lastposx - posx), abs(lastposy - posy)
            if (lenx != 0) or (leny != 0):
                self.selection = opencv.cvRect(startx, starty, lenx, leny)

        self.mouse_pos = (posx, posy)

    def show(self, frame):
        with self.rlock:
            if self.lbutton:
                opencv.cvDrawRect(frame, opencv.cvPoint(*self.mouse_lbutton_pos), 
                              opencv.cvPoint(*self.mouse_pos), opencv.cvScalar(0.0, 255, 0.0))
            if self.selection is not None:
                cvcrop = opencv.cvGetSubArr(frame, None, self.selection)
                sccrop = cvcrop.as_numpy_array()
                try:
                    self.cvMouseSelectionEvent.dispatch(cvcrop)
                    self.scMouseSelectionEvent.dispatch(sccrop)
                finally:
                    self.selection = None

            opencv.cvShowImage(self.wname, frame)

            if self.poll:
                opencv.cvWaitKey(1)






if __name__ == '__main__':
    # Capture and Win creation
    cap = CVCapture(0)
    win = CVWindow()

    # What to do with the cropped frame
    def crop(frame):
        scipy.misc.imshow(frame)

    cap.cvFrameGrabbedEvent.addObserver(win.show)
    win.scMouseSelectionEvent.addObserver(crop)

    # starting the capture 
    cap.start()

    # for the clean output
    def sig_handler(sig, frame):
        cap.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, sig_handler)

    # infinite loop
    while(True):
        time.sleep(2)


