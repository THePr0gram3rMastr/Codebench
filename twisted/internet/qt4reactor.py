# Copyright (c) 2001-2008 Twisted Matrix Laboratories.
# See LICENSE for details.


"""
<<<<<<< HEAD
This module provides support for Twisted to be driven by the Qt mainloop.

In order to use this support, simply do the following::
    |  app = QApplication(sys.argv) # your code to init Qt
    |  import qt4reactor
    |  qt4reactor.install()
    
alternatively:

    |  from twisted.application import reactors
    |  reactors.installReactor('qt4')
=======
This module provides support for Twisted to interact with the PyQt mainloop.

In order to use this support, simply do the following::

    |  import qt4reactor
    |  qt4reactor.install()
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1

Then use twisted.internet APIs as usual.  The other methods here are not
intended to be called directly.

<<<<<<< HEAD
If you don't instantiate a QApplication or QCoreApplication prior to
installing the reactor, a QCoreApplication will be constructed
by the reactor.  QCoreApplication does not require a GUI so trial testing
can occur normally.

Twisted can be initialized after QApplication.exec_() with a call to
reactor.runReturn().  calling reactor.stop() will unhook twisted but
leave your Qt application running

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

Previous maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Original port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
Subsequent port by therve
=======
API Stability: stable

Maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
"""

__all__ = ['install']


<<<<<<< HEAD
import sys, time

from zope.interface import implements

from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL, QTimer, QCoreApplication
from PyQt4.QtCore import QEventLoop
=======
import sys

from zope.interface import implements

from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL, QTimer
from PyQt4.QtGui import QApplication
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1

from twisted.internet.interfaces import IReactorFDSet
from twisted.python import log
from twisted.internet.posixbase import PosixReactorBase

<<<<<<< HEAD
=======


>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
class TwistedSocketNotifier(QSocketNotifier):
    """
    Connection between an fd event and reader/writer callbacks.
    """

    def __init__(self, reactor, watcher, type):
        QSocketNotifier.__init__(self, watcher.fileno(), type)
        self.reactor = reactor
        self.watcher = watcher
        self.fn = None
        if type == QSocketNotifier.Read:
            self.fn = self.read
        elif type == QSocketNotifier.Write:
            self.fn = self.write
        QObject.connect(self, SIGNAL("activated(int)"), self.fn)


    def shutdown(self):
        QObject.disconnect(self, SIGNAL("activated(int)"), self.fn)
<<<<<<< HEAD
        self.setEnabled(False)
        self.fn = self.watcher = None
        self.deleteLater()
=======
        self.setEnabled(0)
        self.fn = self.watcher = None
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1


    def read(self, sock):
        w = self.watcher
<<<<<<< HEAD
        #self.setEnabled(False)    # ??? do I need this?            
=======
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
        def _read():
            why = None
            try:
                why = w.doRead()
            except:
                log.err()
                why = sys.exc_info()[1]
            if why:
                self.reactor._disconnectSelectable(w, why, True)
<<<<<<< HEAD
            elif self.watcher:
                pass
                #self.setEnabled(True)
        log.callWithLogger(w, _read)
        self.reactor.reactorInvocation()

    def write(self, sock):
        w = self.watcher
        self.setEnabled(False)
        def _write():
            why = None
=======
        log.callWithLogger(w, _read)
        self.reactor.simulate()


    def write(self, sock):
        w = self.watcher
        def _write():
            why = None
            self.setEnabled(0)
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
            try:
                why = w.doWrite()
            except:
                log.err()
<<<<<<< HEAD
                why = sys.exc_info()[1]
            if why:
                self.reactor._disconnectSelectable(w, why, False)
            elif self.watcher:
                self.setEnabled(True)
        log.callWithLogger(w, _write)
        self.reactor.reactorInvocation()

class fakeApplication(QEventLoop):
    def __init__(self):
        QEventLoop.__init__(self)
        
    def exec_(self):
        QEventLoop.exec_(self)
        
=======
                why = sys.exc_value
            if why:
                self.reactor._disconnectSelectable(w, why, False)
            elif self.watcher:
                self.setEnabled(1)
        log.callWithLogger(w, _write)
        self.reactor.simulate()



>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
class QTReactor(PosixReactorBase):
    """
    Qt based reactor.
    """
    implements(IReactorFDSet)

<<<<<<< HEAD
    _timer = None

    def __init__(self):
        self._reads = {}
        self._writes = {}
        self._timer=QTimer()
        self._timer.setSingleShot(True)
        if QCoreApplication.startingUp():
            self.qApp=QCoreApplication([])
            self._ownApp=True
        else:
            self.qApp = QCoreApplication.instance()
            self._ownApp=False
        self._blockApp = None
        self._readWriteQ=[]
        
        """ some debugging instrumentation """
        self._doSomethingCount=0
        
        PosixReactorBase.__init__(self)
=======
    # Reference to a DelayedCall for self.crash() when the reactor is
    # entered through .iterate()
    _crashCall = None

    _timer = None

    def __init__(self, app=None):
        self._reads = {}
        self._writes = {}
        if app is None:
            app = QApplication([])
        self.qApp = app
        PosixReactorBase.__init__(self)
        self.addSystemEventTrigger('after', 'shutdown', self.cleanup)

>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1

    def addReader(self, reader):
        if not reader in self._reads:
            self._reads[reader] = TwistedSocketNotifier(self, reader,
                                                       QSocketNotifier.Read)


    def addWriter(self, writer):
        if not writer in self._writes:
            self._writes[writer] = TwistedSocketNotifier(self, writer,
                                                        QSocketNotifier.Write)


    def removeReader(self, reader):
        if reader in self._reads:
<<<<<<< HEAD
            #self._reads[reader].shutdown()
            #del self._reads[reader]
            self._reads.pop(reader).shutdown()
=======
            self._reads[reader].shutdown()
            del self._reads[reader]

>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1

    def removeWriter(self, writer):
        if writer in self._writes:
            self._writes[writer].shutdown()
<<<<<<< HEAD
            #del self._writes[writer]
            self._writes.pop(writer)
=======
            del self._writes[writer]
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1


    def removeAll(self):
        return self._removeAll(self._reads, self._writes)


    def getReaders(self):
        return self._reads.keys()


    def getWriters(self):
        return self._writes.keys()
<<<<<<< HEAD
    
    def callLater(self,howlong, *args, **kargs):
        rval = super(QTReactor,self).callLater(howlong, *args, **kargs)
        self.reactorInvocation()
        return rval
    
    def crash(self):
        super(QTReactor,self).crash()
        
    def iterate(self,delay=0.0):
        t=self.running # not sure I entirely get the state of running
        self.running=True
        self._timer.stop() # in case its not (rare?)
        try:
            if delay == 0.0:
                self.reactorInvokePrivate()
                self._timer.stop() # supports multiple invocations
            else:
                endTime = delay + time.time()
                self.reactorInvokePrivate()
                while True:
                    t = endTime - time.time()
                    if t <= 0.0: return
                    self.qApp.processEvents(QEventLoop.AllEvents | 
                                      QEventLoop.WaitForMoreEvents,t*1010)
        finally:
            self.running=t
            
    def addReadWrite(self,t):
        self._readWriteQ.append(t)
        
    def runReturn(self, installSignalHandlers=True):
        QObject.connect(self._timer, SIGNAL("timeout()"), 
                        self.reactorInvokePrivate)
        self.startRunning(installSignalHandlers=installSignalHandlers)
        self._timer.start(0)
        
    def run(self, installSignalHandlers=True):
        try:
            if self._ownApp:
                self._blockApp=self.qApp
            else:
                self._blockApp = fakeApplication()
            self.runReturn(installSignalHandlers)
            self._blockApp.exec_()
        finally:
            self._timer.stop() # should already be stopped

    def reactorInvocation(self):
        self._timer.setInterval(0)
        
    def reactorInvokePrivate(self):
        if not self.running:
            self._blockApp.quit()
        self._doSomethingCount += 1
        self.runUntilCurrent()
        t = self.timeout()
        if t is None: t=0.1
        else: t = min(t,0.1)
        self._timer.setInterval(t*1010)
        self.qApp.processEvents() # could change interval
        self._timer.start()
                
    def doIteration(self):
        assert False, "doiteration is invalid call"
            
def install():
=======


    def simulate(self):
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

        if not self.running:
            self.qApp.exit()
            return
        self.runUntilCurrent()

        if self._crashCall is not None:
            self._crashCall.reset(0)

        timeout = self.timeout()
        if timeout is None:
            timeout = 1.0
        timeout = min(timeout, 0.001) * 1010

        if self._timer is None:
            self._timer = QTimer()
            QObject.connect(self._timer, SIGNAL("timeout()"), self.simulate)
        self._timer.start(timeout)


    def cleanup(self):
        if self._timer is not None:
            self._timer.stop()
            self._timer = None


    def iterate(self, delay=0.0):
        self._crashCall = self.callLater(delay, self._crash)
        self.run()


    def mainLoop(self):
        self.simulate()
        self.qApp.exec_()


    def _crash(self):
        if self._crashCall is not None:
            if self._crashCall.active():
                self._crashCall.cancel()
            self._crashCall = None
        self.running = False



def install(app=None):
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
    """
    Configure the twisted mainloop to be run inside the qt mainloop.
    """
    from twisted.internet import main
<<<<<<< HEAD
    reactor = QTReactor()
=======
    reactor = QTReactor(app=app)
>>>>>>> fcefe012dc247ab7355a2032f79564c49fe30fc1
    main.installReactor(reactor)
