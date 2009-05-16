#
#
# vim: ts=4 sw=4 sts=0 noexpandtab:
import os
import copy
import traceback


class Event(object):
    """
    This is a simple object which represent an event it can be dispatched which
    notifies every observer of this event

    """
    name = ""
    __id__ = -1

    def __next_id__(self):
        res = self.__id__ = self.__id__ + 1
        return res

    def __init__(self):
        """
        Init procedure
        """
        self.clear()


    def addObserver(self, obj, *args):
        """
        This method add an observer for this event. Every argument passed to
        this function will be forwarded to the callback when the event is fired
        """
        if not callable(obj):
            raise RuntimeError("Callback must be callable")

        id = self.__next_id__()
        self.observers[id] = (obj, args)
        return id

    def removeObserver(self, obj):
        """
        This method remove an observer for the event.
        """
        del self.observers[obj]

    def dispatch(self, *args):
        """
        This method dispatch the events with arguments which are forwarded to
        the listener functions.
        """
        for callback, cargs in self.observers.itervalues():
            try:
                callback(*(args + cargs))
            except Exception, e:
                traceback.print_exc()

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
        o2 = copy.copy(self.observers)
        for callback, cargs in o2.itervalues():
            try:
                callback(*(args + cargs))
            except Exception, e:
                traceback.print_exc()

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
                if logger.isEnabledFor(logging.WARNING):
                    logger.warning("Event Function Override -- %s --" % evt_name)
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
                if logger.isEnabledFor(logging.WARNING):
                    logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))

    def removeObserver(self, obj):
        """
        Remove the right method observer to the contained event
        """
        for evt in self.events:
            try:
                getattr(self, evt).removeObserver(getattr(obj, evt), evt, *args, **kw)
            except AttributeError, err:
                if logger.isEnabledFor(logging.WARNING):
                    logger.warning("Object : %s do not have attribute -- %s --" % \
                               (repr(obj), evt))

    def clear(self):
        """
        Clear all events of this object
        """
        for evt in self.events:
            getattr(self, evt + "Event").clear()



class ThreadedEventDispatcher(EventDispatcherBase):
    event_type = ThreadedEvent

