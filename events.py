#
#
# vim: ts=4 sw=4 sts=0 expandtab:
from __future__ import with_statement
import os, types, copy, weakref, threading, time
import logging
import wref

import generator

logger = logging.getLogger(__name__)


class EventSupervisor(object):
        processing = False
        triggered = 0
        def __init__(self):
            self.creation_time = time.time()

        def __enter__(self):
            self.processing = True
            self.triggered += 1

        def __exit__(self, typ, value, traceback):
            self.processing = False


class Event(object):
    """
    This is a simple object which represent an event it can be dispatched which
    notifies every observer of this event.  WARNING : The default behavior only 
    keeps weakref so KEEP REFERENCE.
    """
    name = ""
    def __init__(self, supervisor = None, weakref = False):
        """
        Init procedure
        """
        self.observers = {}
        self.supervisor = EventSupervisor() if supervisor is None else supervisor
        self.uid_gen = generator.uid_generator()
        self.wref = weakref

    def addObserver(self, observer, *args, **kwarg):
        """
        This method add an observer for this event. Every argument passed to
        this function will be forwarded to the callback when the event is fired
        """
        if not callable(observer):
            raise RuntimeError("Observer must be callable")

        oid = self.uid_gen.next() if "oid" not in kwarg else kwarg.pop("oid")
        if oid in self.observers:
            if logger.isEnabledFor(logger.WARNING):
                logger.warning("Observer ID collision detected [%s]" % str(oid))

        obj = observer
        if self.wref:
            obj = wref.WeakBoundMethod(obj) if isinstance(obj, types.InstanceType) else weakref.ref(obj)

        self.observers[oid] = (obj, args)
        return oid

    def removeObserver(self, oid):
        """
        This method remove an observer for the event.
        """
        del self.observers[oid]

    def dispatch(self, *args):
        """
        This method dispatch the events with arguments which are forwarded to
        the listener functions.
        """
        o2 = copy.copy(self.observers)
        with self.supervisor:
            for oid, (callback, cargs) in o2.iteritems():
                try:
                    if self.wref:
                        callback = callback()

                        if callback is not None:
                            callback(*(args + cargs))
                        else:
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug("Observer event deleted id [%d]" % oid)
                            del self.observers[oid]
                    else:
                        callback(*(args + cargs))
                except Exception(e):
                    logger.exception(str(e))

    __call__ = dispatch

    def clear(self):
        """
        Clear the observer dictionary.
        """
        self.observers = {}

    def __len__(self):
        return len(self.observers)




class EventDispatcherBase(object):
    """
    This object act as a base object for an aglomerate of events. It provides
    the possibility tp register a single object for every events in the object.
    It is also in charge of initializing events.
    """
    events = []
    event_type = Event
    def __init__(self, **kw):
        """
        Simple Init method which creates the events
        """
        self.uid_gen = generator.uid_generator()
        for evt_name in self.events:
            if hasattr(self, evt_name + "Event"):
                    logger.warning("Event Function Override -- %s --" % evt_name)
            else:
                evt = self.event_type(**kw)
                setattr(self, evt_name + "Event", evt)
                evt.name = evt_name

    def addObserver(self, obj, *args,  **kw):
        """
        Add the right method observer to the contained event
        """
        oid = self.uid_gen.next() if "oid" not in kw else kw.pop("oid")
        for evt in self.events:
            try:
                getattr(self, evt + "Event").addObserver(getattr(obj, evt), *args, oid = oid)
            except AttributeError(err):
                if logger.isEnabledFor(logging.WARNING):
                    logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))
        return oid

    def removeObserver(self, oid):
        """
        Remove the right method observer to the contained event
        """
        for evt in self.events:
            try:
                getattr(self, evt + "Event").removeObserver(oid)
            except AttributeError(err):
                pass

    def clear(self):
        """
        Clear all events of this object
        """
        for evt in self.eents:
            getattr(self, evt + "Event").clear()

    def dispatch(self, evtname, *args):
        if evtname in self.events:
            getattr(self, evtname + "Event")(*args)


class MutexedEvent(Event):
        def __init__(self, mutex = None):
                Event.__init__(self)
                self.mutex = threading.Lock() if mutex is None else mutex

        def dispatch(self, *args):
                with self.mutex:
                        Event.dispatch(self, *args)


class MutexedEventDispatcher(EventDispatcherBase):
        event_type = MutexedEvent
        def __init__(self, *args, **kw):
            """
            Simple Init method which creates the events
            """
            self.mutex = threading.Lock()
            if "mutex" not in kw:
                kw["mutex"] = self.mutex
            EventDispatcherBase.__init__(self, *args, **kw)


class Conduit(object):
    """
    This class is very similar to the Event Class. It provides callback
    registery for asynchronous event processing. It also add the backward
    linkage to the coresponding event when the object is defining the
    __input_event_id__ attribute. This object is interesting to use if you
    have to introspect the incomming event and get some information with it.
    """
    __input_event_id__ = "__input_events__"

    def __init__(self, supervisor = None):
        """
        """
        self.__observers__ = ()
        self.__uid_gen__ = generator.uid_generator()
        self.supervisor = EventSupervisor() if supervisor is None else supervisor


    def __add_backward_reference__(self, callback, obj):
        """
        """
        if not hasattr(obj, self.__input_event_id__):
            return
        cid = hash(callback)
        if cid not in obj.__input_pipes__:
            obj.__input_pipes__[cid] = []

        obj.__input_pipes__[cid].append(self)

    def __del_backward_reference__(self, callback, obj):
        """
        """
        if not hasattr(obj, self.__input_event_id__):
            return
        cid = hash(callback)
        obj.__input_pipes__[cid].remove(self)


    def addObserver(self, callback, *args, **kwarg):
        """
        """
        if not callable(callback):
            raise RuntimeError("Observer must be callable")

        uid = next(self.__uid_gen__)
        if uid in self.__observers__:
            raise RuntimeError("Observer ID collision detected[%s]" & str(uid))

        self.__observers__ = self.__observers__ + ((uid, callback, args), )
        if isinstance(callback, types.MethodType):
            obj = callback.__self__
            self.__add_backward_reference__(callback, obj)

        return uid

    def dispatch(self, *args, **kw):
        """
        """
        with self.supervisor:
            for oid, callback, inargs in self.__observers__:
                try:
                    callback(*(inargs + args), **kw)
                except Exception(e):
                    pass


    def removeObserver(self, roid):
        """
        """
        for i in range(len(self.__observers__)):
            oid, callback, args = self.__observers__[i]
            if roid == oid:
                if isinstance(callback, types.MethodType):
                    obj = callback.__self__
                    self.__del_backward_reference__(callback, obj)
                self.__observers__ = self.__observers__[:i] + self.__observers__[i + 1:]
                return

        raise RuntimeError("Observer does not exists ...")

    def clear(self):
        """
        """
        while len(self.__observers__) is not 0:
            oid, callback, args = self.__observers__[0]
            self.removeObserver(oid)

    def __call__(self, *args, **kw):
        self.dispatch(*args, **kw)

