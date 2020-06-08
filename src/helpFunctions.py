from tkinter import *
from tkinter import ttk
import os

class HelpFunctions():
    def __init__(self, mTask):
        self.mTask = mTask
    
    def showGuide(self):
        os.startfile("Guide.txt")
    
    def showInfo(self):
        print("Showing Info")