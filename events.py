#
#
# vim: ts=4 sw=4 sts=0 expandtab:
from __future__ import with_statement
import os, new, copy, weakref, threading, time
import logging
from codebench import wref

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
    notifies every observer of this event
    """
    name = ""
    types = None
    def __init__(self, *args):
        """
        Init procedure
        """
        self.observers = {}
        self.supervisor = EventSupervisor()
        if len(args) != 0:
            self.types = args

    def addObserver(self, obj, *args, **kwarg):
        """
        This method add an observer for this event. Every argument passed to
        this function will be forwarded to the callback when the event is fired
        """
        if not callable(obj):
            raise RuntimeError("Callback must be callable")

        oid = hash(obj) if isinstance(obj,new.instancemethod) else id(obj)
        oid = kwarg.pop("oid", oid)
        if oid in self.observers:
            if logger.isEnabledFor(logger.WARNING):
                logger.warning("Observer ID collision detected [%s]" % str(oid))

        wobj = wref.WeakBoundMethod(obj) if isinstance(obj,new.instancemethod) else weakref.ref(obj)
        self.observers[oid] = (wobj, args)
        return oid

    def removeObserver(self, obj):
        """
        This method remove an observer for the event.
        """
        oid = hash(obj) if isinstance(obj,new.instancemethod) else id(obj)
        oid = obj if obj in self.observers else oid
        del self.observers[oid]

    def dispatch(self, *args):
        """
        This method dispatch the events with arguments which are forwarded to
        the listener functions.
        """
        o2 = copy.copy(self.observers)
        with self.supervisor:
            for oid, (wcallback, cargs) in o2.iteritems():
                try:
                    callback = wcallback()
                    if callback is not None:
                        callback(*(args + cargs))
                    else:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug("Observer event deleted id [%d]" % oid)
                        del self.observers[oid]
                except Exception, e:
                    logger.exception(str(e))

    def __call__(self, *args):
        self.dispatch(*args)

    def clear(self):
        """
        Clear the observer dictionary.
        """
        self.observers = {}

    def __len__(self):
        return len(self.observers)

class ThreadsafeEvent(Event):
        def __init__(self, mutex = None):
                Event.__init__(self)
                self.mutex = threading.Lock()

        def dispatch(self, *args):
                with self.mutex:
                        Event.dispatch(self, *args)


class EventDispatcherBase(object):
    """
    This object act as a base object for an aglomerate of events. It provides
    the possibility tp register a single object for every events in the object.
    It is also in charge of initializing events.
    """
    events = []
    event_type = Event
    def __init__(self):
        """
        Simple Init method which creates the events
        """
        #self.uid_gen = generator.uid_generator()
        for evt_name in self.events:
            if hasattr(self, evt_name + "Event"):
                    logger.warning("Event Function Override -- %s --" % evt_name)
            else:
                evt = self.event_type()
                setattr(self, evt_name + "Event", evt)
                evt.name = evt_name

    def addObserver(self, obj, *args, **kwarg):
        """
        Add the right method observer to the contained event
        """
        for evt in self.events:
            try:
                getattr(self, evt + "Event").addObserver(getattr(obj, evt), *args, **kwarg)
            except AttributeError, err:
                if logger.isEnabledFor(logging.WARNING):
                    logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))

    def removeObserver(self, obj):
        """
        Remove the right method observer to the contained event
        """
        for evt in self.events:
            try:
                getattr(self, evt + "Event").removeObserver(getattr(obj, evt), *args, **kwarg)
            except AttributeError, err:
                pass

    def clear(self):
        """
        Clear all events of this object
        """
        #for evt in self.eents:
        #    getattr(self, evt + "Event").clear()
        for evt in self.events:
            try:
                getattr(self, evt + "Event").addObserver(getattr(obj, evt), *args, **kwarg)
            except AttributeError, err:
                if logger.isEnabledFor(logging.WARNING):
                    logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))

        for evt, seoid in iddict:
                    getattr(self, evt + "Event").removeObserver(seoid)
        self.observers = {}

    def dispatch(self, evtname, *args):
        if evtname in self.events:
            getattr(self, evtname + "Event")(*args)


class ThreadsafeEventDispatcher(EventDispatcherBase):
        event_type = ThreadsafeEvent
        def __init__(self):
            """
            Simple Init method which creates the events
            """
            #self.uid_gen = generator.uid_generator()
            self.mutex = threading.Lock()
            for evt_name in self.events:
                if hasattr(self, evt_name + "Event"):
                        logger.warning("Event Function Override -- %s --" % evt_name)
                else:
                    evt = self.event_type(mutex = self.mutex)
                    setattr(self, evt_name + "Event", evt)
                    evt.name = evt_name


