#!/usr/bin/python
import argparse

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("PangoCairo", "1.0")
gi.require_version("Pango", "1.0")
gi.require_version("WebKit2", "4.0")

import cairo
from gi.repository import Gdk, GObject, Gtk, GtkLayerShell, WebKit2

parser = argparse.ArgumentParser()
parser.add_argument("url", type=str)

args = parser.parse_args()

HTML = """
<html>
    <head>
        <style>
            #draggable {
                position: absolute;
                width: 25%;
                aspect-ratio: 16/9;
                object-fit: cover;
                resize: horizontal;
                overflow: auto;
                opacity: 1.0;
            }

        </style>
        <script>
            window.onload = function(){
                function dragElement(elmnt) {
                    let opacity = 1.0;
                    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
                    
                    document.onmousedown = dragMouseDown;
                    
                    function dragMouseDown(e) {
                        e = e || window.event;
                        e.preventDefault();
                        // get the mouse cursor position at startup:
                        pos3 = e.clientX;
                        pos4 = e.clientY;
                        document.onmouseup = closeDragElement;
                        document.onkeyup = (e) => {
                            if (e.code == "Escape") {
                                closeDragElement();
                            }
                        };
                        // call a function whenever the cursor moves:
                        document.onmousemove = elementDrag;
                    }

                    function elementDrag(e) {
                        e = e || window.event;
                        e.preventDefault();
                        // calculate the new cursor position:
                        pos1 = pos3 - e.clientX;
                        pos2 = pos4 - e.clientY;
                        pos3 = e.clientX;
                        pos4 = e.clientY;
                        // set the element's new position:
                        let newTop = (elmnt.offsetTop - pos2);
                        let newLeft = (elmnt.offsetLeft - pos1);

                        if (newTop > (elmnt.parentElement.clientHeight - elmnt.offsetHeight)) {
                            newTop = (elmnt.parentElement.clientHeight - elmnt.offsetHeight);
                        }
                        else if (newLeft > (elmnt.parentElement.clientWidth - elmnt.offsetWidth)) {
                            newLeft = (elmnt.parentElement.clientWidth - elmnt.offsetWidth);
                        }

                        if (newTop < 0) {
                            newTop = 0;
                        }
                        else if (newLeft < 0) {
                            newLeft = 0;
                        }

                        elmnt.style.top = newTop + "px";
                        elmnt.style.left = newLeft + "px";
                    }

                    function closeDragElement() {
                        // stop moving when mouse button is released:
                        document.onmouseup = null;
                        document.onmousemove = null;
                    }

                    document.onwheel = (e) => {
                        e.preventDefault();
                        opacity += e.deltaY * -0.00001;

                        // Restrict scale
                        opacity = Math.min(Math.max(0.0, opacity), 1.0);

                        // Apply scale transform
                        elmnt.style.opacity = opacity;
                    };
                }

                let draggable = document.querySelector("#draggable");

                dragElement(draggable);
            }
        </script>
    </head>
    <body>
        <iframe 
            id="draggable"
            allow="autoplay"
            frameborder="0"
            src="${}">
        </iframe>
    </body>
</html>
"""


class Overlay(Gtk.Window):
    def __init__(self, touchable):
        Gtk.Window.__init__(self)

        transparent_window_style_provider = Gtk.CssProvider()
        transparent_window_style_provider.load_from_data(
            b"""
            GtkWindow {
                background-color: rgba(0,0,0,0);
            }"""
        )
        self.get_style_context().add_provider(
            transparent_window_style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.set_app_paintable(True)

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_keyboard_interactivity(self, touchable)

        self.screen = self.get_screen()

        self._touchable = touchable
        if not touchable:
            self.set_input_shape()

        self.connect("key-release-event", self.on_key_release_event)

    def set_input_shape(self):
        """
        Create a custom input shape and tell it that all of the window is a cut-out
        This allows us to have a window above everything but that never gets clicked on
        """
        monitor = self.get_display().get_primary_monitor()
        if monitor is None:
            monitor = self.get_display().get_monitor(
                self.screen.get_display().get_n_monitors() - 1
            )

        width, height = monitor.get_workarea().width, monitor.get_workarea().height

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        surface_ctx = cairo.Context(surface)
        surface_ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        surface_ctx.set_operator(cairo.OPERATOR_SOURCE)
        surface_ctx.paint()

        reg = Gdk.cairo_region_create_from_surface(surface)

        self.input_shape_combine_region(reg)

    @property
    def touchable(self):
        return self._touchable

    @touchable.setter
    def set_touchable(self, touchable):
        self._touchable = touchable
        if not touchable:
            self.set_input_shape()

    def on_key_release_event(self, widget, event):
        pass


class PositionSelectionOverlay(Overlay):
    def on_key_release_event(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            Gtk.main_quit()


class VideoOverlay(Overlay):
    def on_key_release_event(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()


class AllowAutoplayPolicies(WebKit2.WebsitePolicies):
    def __init__(self):
        WebKit2.WebsitePolicies.__init__(self)

    @GObject.Property(type=WebKit2.AutoplayPolicy, default=WebKit2.AutoplayPolicy.ALLOW)
    def autoplay():
        return WebKit2.AutoplayPolicy.ALLOW


def on_decide_policy(webview, decision, decision_type):
    if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
        website_policies = AllowAutoplayPolicies()
        decision.use_with_policies(website_policies)
        return True
    return False


def main():
    # Create webview with transparent background
    webview = WebKit2.WebView()
    webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))

    # Allow for autoplay with sound
    webview.connect("decide-policy", on_decide_policy)

    # Load html with position and size selection and url interpolated to iframe src
    webview.load_html(HTML.replace("${}", args.url), None)

    # Create a window that can be clicked
    position_selection_window = PositionSelectionOverlay(touchable=True)
    video_window = Overlay(touchable=False)

    # Add webkit to the window so user can select where do they want iframe to be
    position_selection_window.add(webview)
    position_selection_window.show_all()
    Gtk.main()  # Blocking until Gtk.main_quit() is called

    # Gtk.main_quit() was called
    # Remove webview from window so it isn't destroyed with it
    position_selection_window.remove(webview)
    position_selection_window.destroy()

    # Create a clickthrought window with the same web page so the selected position doesn't change
    video_window.add(webview)
    video_window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
