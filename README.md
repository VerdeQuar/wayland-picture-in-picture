# Picture-in-picture Overlay that works on wayland
Play youtube or open any other website on an unclickable window that will stay always on top (yes, even on fullscreen windows) and will not steal your focus!

## Requirements
```sh
pip install PyGObject
```

## Getting started

Run the script with url of your choice
```sh
python main.py https://www.youtube.com/embed/dQw4w9WgXcQ&autoplay=1
```

This will open a transparent window with your website in a rectangle (by default it will take 1/16 of your screen)
That window will cover your whole screen (even fullscreen windows) and prevent you from clicking on anything

You can now:

Change position by dragging on empty space 
*It will glitch if you let go of the button when your cursor is on top of the rectangle due to the way iframe handles events
you can fix it by pressing Escape*

Change size with a handle in bottom right corner of a rectangle
Change opacity with scroll wheel


**When you're done, press Enter**
This will make a window clickthrough so you can do whatever you want and the overlay will stay on top of everything

**To close the overlay just kill python process**

###  Protip
You can make this more user friendly by binding it to a hotkey, passing url from the clipboard and saving process ID to kill it later
