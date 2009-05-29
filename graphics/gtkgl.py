#
#
# vim: ts=4 sw=4 sts=0 expandtab:
import logging

import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import gobject

import scipy

logger = logging.getLogger(__name__)


class Actor(object):
    def __init__(self):
        self.visible = True
        self.p = scipy.eye(4)

    def display(self):
        if self.visible:
            glPushMatrix()
            glMultMatrixf(self.p)
            self.draw()
            glPopMatrix()

    def draw(self):
        pass

class GridActor(Actor):
    color = (1.0, 1.0, 1.0)
    def __init__(self, scalex = 1, scaley = 1, n = 10):
        Actor.__init__(self)
        self.p = scipy.diag([scalex, scaley, 1, 1])
        self.ran = scipy.arange(0, 1.0 + 1.0 / n, 1.0 / n)

    def draw(self):
        glColor3fv(self.color)
        glBegin(GL_LINES)
        for i in self.ran:
            glVertex3f(i, 0, 0)
            glVertex3f(i, 1.0, 0)
            glVertex3f(1.0, i, 0)
            glVertex3f(0, i, 0)
        glEnd()


class Polyline:
        def __init__(self, vertices, closed = False):
            self.vertices = vertices
            self.closed = closed

        def display(self):
            if self.closed:
                glBegin( GL_LINE_LOOP )
            else:
                glBegin( GL_LINE_STRIP )
            glColor3f(1,1,0)

            for vertex in self.vertices:
                glVertex3f( vertex[0], vertex[1], 0 )

            glEnd()


class GLDrawingArea(gtk.DrawingArea, gtk.gtkgl.Widget):
    """
    Simple Drawing area
    """
    def __init__(self):
        gtk.DrawingArea.__init__(self)

class GLRenderer(object):
    zoom    = 3000
    rx    = 0
    ry    = 0.001
    tx      = 0
    ty      = 0
    lastx   = 0
    lasty   = 0

    FRUSTDIM = 500

    ROTATION_SPEED = 0.5
    TRANSLATION_SPEED = 0.5
    ZOOM_SPEED = 0.5

    FRUSTDIM = 500

    ROTATION_SPEED = 0.5
    TRANSLATION_SPEED = 0.5
    ZOOM_SPEED = 5

    FPS = 15

    def __init__(self, stop = True):
        self.bstate = [False] * 10
        self.actors = []
        self.key_handlers = {}
        if stop:
            self.key_handlers['q'] = self.stop

        self.toggle_types = []
        area = GLDrawingArea()
        self.set_drawing_area(area)

        main = gtk.Window()
        main.connect( "delete_event", self.stop )
        main.connect("key_press_event", self.keypress_event)
        main.add(area)

        main.set_title("OpenGL Gtk Renderer")
        main.show_all()
        self.background = (0.0, 0.0, 0.0, 0.0)


    def toggle_actor(self, type):
        """
        Change the visibility of a type of actors
        """
        for actor in self.actors:
            if isinstance(actor, type):
                actor.visible = not actor.visible

    def set_drawing_area(self, area):
        """
        Connecting to the events and masking interesting event. Initializing
        display mode 
        """
        area.add_events(gtk.gdk.BUTTON_MOTION_MASK | gtk.gdk.POINTER_MOTION_MASK | 
                        gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_PRESS_MASK)
        display_mode = (gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DOUBLE)
        glconfig = gtk.gdkgl.Config(mode=display_mode)
        area.set_gl_capability(glconfig)

        area.connect("expose_event", self.expose_event )
        area.connect("configure_event", self.configure_event )
        area.connect("motion_notify_event", self.motion_event)
        area.connect("button_press_event", self.mouse_event)
        area.connect("button_release_event", self.mouse_event)
        area.connect("realize", self.realize_event)

        gobject.timeout_add(1000 / self.FPS, self.timed_redraw, area)

    def timed_redraw(self, area):
        """
        This method is called by the timer
        """
        self.expose_event(area, None)
        return True

    def keypress_event(self, area, evt):
        """
        Called on a key press event. Dispatch the event to the right function
        """
        try:
            ival = int(chr(evt.keyval))
            if ival < len(self.toggle_types):
                self.toggle_actor(self.toggle_types[ival])
                area.queue_draw()
                return
        except ValueError, e:
            pass

        try:
            cval = chr(evt.keyval)
            if cval in self.key_handlers:
                self.key_handlers[cval]()
                area.queue_draw()
                return
        except ValueError, e:
            pass

    def configure_event(self, area, evt):
        """
        This is called when the window is resized. We reinitialize the
        projection
        """
        gldrawable = area.get_gl_drawable()
        glcontext = area.get_gl_context()
        gldrawable.gl_begin(glcontext)

        glViewport(0, 0, evt.width, evt.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, evt.width/float(evt.height), 0.1, 10000)
        glMatrixMode(GL_MODELVIEW)

        gldrawable.gl_end()

    def mouse_event(self, area, evt):
        """
        Mouse event, this is called when the button changed
        """
        self.lastx = evt.x
        self.lasty = evt.y
        self.bstate[evt.button - 1] = not self.bstate[evt.button - 1]

    def motion_event(self, area, evt):
        """
        This method is called when we have a mouse motion event.
        """
        dx = evt.x - self.lastx
        dy = evt.y - self.lasty
        self.lastx = evt.x
        self.lasty = evt.y
        redraw = False
        if  self.bstate[0]:
            self.tx += dx * self.TRANSLATION_SPEED
            self.ty += dy * self.TRANSLATION_SPEED
            redraw = True
        if self.bstate[2]:
            self.rx += dy * self.ROTATION_SPEED
            self.ry += dx * self.ROTATION_SPEED
            redraw = True
        if self.bstate[1]:
            self.zoom -= self.ZOOM_SPEED * dx
            redraw = True
        if redraw:
            area.queue_draw()

    def realize_event(self, area):
        """
        Initializing depth test
        """
        gldrawable = area.get_gl_drawable()
        glcontext = area.get_gl_context()
        gldrawable.gl_begin(glcontext)

        glEnable(GL_DEPTH_TEST)
        glutInit([])

        gldrawable.gl_end()

    def expose_event(self, area, evt):
        """
        This is call on redraw. This method set the identity matrix and call the
        render function
        """
        gldrawable = area.get_gl_drawable()
        glcontext  = area.get_gl_context()
        gldrawable.gl_begin(glcontext)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(0,0, -self.zoom)
        glTranslatef(self.tx, self.ty, 0)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glClearColor(*self.background)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.render()

        gldrawable.swap_buffers()
        gldrawable.gl_end()

    def render(self):
        """
        Called to render the scene
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for a in self.actors:
            try:
                a.display()
            except Exception, e:
                print e

    def start(self):
        gtk.main()

    def stop(self):
        gtk.main_quit()


Renderer = GLRenderer

if __name__ == '__main__':
    renderer = Renderer()

    actor = Polyline( [ ( -10, -10 ), ( 10, -10 ), ( 10, 10 ), ( -10, 10 ) ], closed = True )
    renderer.actors.append(actor)

    renderer.start()

