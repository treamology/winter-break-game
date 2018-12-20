from panda3d.core import WindowProperties
import sys

this = sys.modules[__name__]

this.mouse_captured = False

def capture_mouse():
    print("Capture mouse")
    this.mouse_captured = True
    props = WindowProperties()
    props.set_mouse_mode(WindowProperties.M_relative)
    props.set_cursor_hidden(True)
    base.win.request_properties(props)

def relinquish_mouse():
    print("Reliniquish mouse")
    this.mouse_captured = False
    props = WindowProperties()
    props.set_mouse_mode(WindowProperties.M_absolute)
    props.set_cursor_hidden(False)
    base.win.request_properties(props)

def toggle_mouse():
    relinquish_mouse() if this.mouse_captured else capture_mouse()
