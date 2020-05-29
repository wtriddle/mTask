from tkinter import *
from tkinter import ttk

class RoutineFunctions():
    def __init__(self, mTask):
        self.mTask = mTask
    def newRoutine(self):
        print("Creating new routine...")
    def loadRoutine(self):
        print("Loading Routine...")
    def editRoutine(self):
        print("Editng Routine...")
    def saveRoutine(self):
        print("Saving routine...") 
    def addTask(self):
        print("Adding task to routine...")