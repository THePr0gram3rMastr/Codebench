import os
import copy

import logging
DEBUG = os.environ.get('DEBUG', False) in ["True","true","1", "TRUE"]
logger = logging.getLogger(__name__) if DEBUG else None

class Event(object):
    """
    This is a simple object which represent an event it can be dispatched which
    notifies every observer of this event

    """
    name = ""
    def __init__(self):
        """
        Init procedure
        """
        self.clear()

    def addObserver(self, obj, *args, **kw):
        """
        This method add an observer for this event. Every argument passed to
        this function will be forwarded to the callback when the event is fired
        """
        DEBUG and logger.debug('Add an observer to : %s' % self.name)
        if callable(obj):
            self.observers[obj] = [args, kw]
        else:
            raise RuntimeError("Callback must be callable")

    def removeObserver(self, obj):
        """
        This method remove an observer for the event.
        """
        DEBUG and logger.info("Removing event observer : %s" % self.name)
        del self.observers[obj]

    def dispatch(self, *args):
        """
        This method dispatch the events with arguments which are forwarded to
        the listener functions.
        """
        DEBUG and logger.info("Dispatching event : %s" % self.name)
        for callback, (cargs, ckw) in self.observers.iteritems():
            callback(*(args + cargs), **ckw)

    def __call__(self, *args):
        self.dispatch(*args)

    def clear(self):
        """
        Clear the observer dictionary.
        """
        self.observers = {}

    def __len__(self):
        return len(self.observers)

class ThreadedEvent(Event):
    def dispatch(self, *args):
        DEBUG and logger.info("Dispatching event : %s" % self.name)
        o2 = copy.copy(self.observers)
        for callback, (cargs, ckw) in o2.iteritems():
            callback(*(args + cargs), **ckw)


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
        for evt_name in self.events:
            if hasattr(self, evt_name + "Event"):
                DEBUG and logger.warning("Event Function Override -- %s --" % evt_name)
            else:
                evt = self.event_type()
                setattr(self, evt_name + "Event", evt)
                evt.name = evt_name


    def addObserver(self, obj, *args, **kw):
        """
        Add the right method observer to the contained event
        """
        for evt in self.events:
            try:
                getattr(self, evt + "Event").addObserver(getattr(obj, evt), *args, **kw)
            except AttributeError, err:
                DEBUG and logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))

    def removeObserver(self, obj):
        """
        Remove the right method observer to the contained event
        """
        for evt in self.events:
            try:
                getattr(self, evt).removeObserver(getattr(obj, evt), evt, *args, **kw)
            except AttributeError, err:
                DEBUG and logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))

    def clear(self):
        """
        Clear all events of this object
        """
        for evt in self.events:
            getattr(self, evt + "Event").clear()



class ThreadedEventDispatcher(EventDispatcherBase):
    event_type = ThreadedEvent




class EventDispatcher(EventDispatcherBase):
    events = ['connected', 'disconnected']

