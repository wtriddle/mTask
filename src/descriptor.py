from tkinter import *

class Descriptor(object):
    def __init__(self, widget):
        self.widget = widget
        self.descriptorwindow = None
        self.id = None
        self.x = self.y = 0
    
    def showDescriptor(self,text):
        "Display text in descriptor window"
        self.text = text
        if self.descriptorwindow or not self.text:
            return
        x,y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.descriptorwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x,y))

        label = Label(tw, text = self.text, justify = LEFT,
                        background = '#ffffe0', relief = SOLID, borderwidth = 1,
                        font = ("tahoma", '8', "normal"), wraplength = 400)
        label.pack(ipadx = 1)

    def hideDescriptor(self):
        tw = self.descriptorwindow
        self.descriptorwindow = None
        if tw:
            tw.destroy()
    
#=====================================================================
def createDescriptor(widget, text):
    descriptor = Descriptor(widget)
    def enter(event):
        descriptor.showDescriptor(text)
    def leave(event):
        descriptor.hideDescriptor()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

