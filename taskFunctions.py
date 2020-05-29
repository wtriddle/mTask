from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox

class TaskFunctions():
    def __init__(self, mTask):
        self.mTask = mTask
        
    def newTask(self):

        window = Toplevel(self.mTask.root)
        containerFrame = ttk.Frame(window)
        containerFrame.pack(expand = True, fill = "both", padx = 50, pady = 50)

        ttk.Label(containerFrame, text = "New Task Name").grid(row = 0 , column = 0, pady = 5)

        self.taskEntry = ttk.Entry(containerFrame)
        self.taskEntry.grid(row = 1, column = 0, pady = 5)

        ttk.Label(containerFrame, text = "Target Start Time").grid(row = 2, column = 0)

        self.timeEntry = ttk.Entry(containerFrame)
        self.timeEntry.grid(row = 3, column = 0, pady = 5)

        self.submitButton = ttk.Button(containerFrame, text = "Create", command = self.submitNewTaskData)
        self.submitButton.grid(row = 4, column = 0, pady = 20, sticky = NSEW)
    def submitNewTaskData(self):
        taskName = self.taskEntry.get()
        taskTime = self.timeEntry.get()
        if not taskName:
            mBox.showerror(title = "Task Creation Error", message= "Please enter a task name")
            return 
        self.mTask.mTaskDB.set_table(tablename = "Tasks")
        recs = self.mTask.mTaskDB.getrecs()
        if recs:
            for rec in recs:
                if taskName == rec['taskName']:
                    mBox.showerror(title = "Task Creation Error", message= "Please enter a unqiue task name")
                    return 
        self.mTask.addTaskToGUI(**{'taskName': taskName, 'taskTime' : taskTime, 'routineName' : "Tasks"})
        self.mTask.mTaskDB.insert({'taskName': taskName, 'taskTime' : taskTime, 'Routine_id' : 0}) 

    def loadTask(self):
        # Load userTasks from database
        self.mTask.mTaskDB.set_table(tablename = "Tasks")
        recs = list(self.mTask.mTaskDB.getrecs())
        userTasks = [rec['taskName'] for rec in recs]

        # Load userRoutines from database
        self.mTask.mTaskDB.set_table(tablename = "Routines")
        recs = list(self.mTask.mTaskDB.getrecs())
        userRoutines = [rec['routineName'] for rec in recs]

        # Form Window ------------------------------------------------------
        window = Toplevel(self.mTask.root)
        containerFrame = ttk.Frame(window)
        containerFrame.pack(expand = True, fill = "both", padx = 50, pady = 50)

        ttk.Label(containerFrame, text = "Choose a Task").grid(row = 0, column = 0, pady = 10, padx = 10)

        self.taskEntry = ttk.Combobox(containerFrame, state = "readonly")
        self.taskEntry.config(values = userTasks)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Choose a Routine").grid(row = 2, column = 0, pady = 10, padx = 10)

        self.routineEntry = ttk.Combobox(containerFrame, state = "readonly")
        self.routineEntry.config(values = userRoutines)
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(containerFrame, text = "Load", command = self.submitLoadTaskData)
        self.submitButton.grid(row = 4, column = 0, pady = 20, sticky = NSEW)
        # ~ Form Window ------------------------------------------------------

    def submitLoadTaskData(self):
        taskName = str(self.taskEntry.get())
        routineName = str(self.routineEntry.get())
        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        taskTime = rec['taskTime']
        self.mTask.addTaskToGUI(**{'taskName': taskName, 'taskTime' : taskTime, 'routineName' : routineName})
    def editTask(self):
        # Load userTasks from database
        self.mTask.mTaskDB.set_table(tablename = "Tasks")
        recs = list(self.mTask.mTaskDB.getrecs())
        userTasks = [rec['taskName'] for rec in recs]

        # Form Window ------------------------------------------------------
        window = Toplevel(self.mTask.root)
        containerFrame = ttk.Frame(window)
        containerFrame.pack(expand = True, fill = "both", padx = 50, pady = 50)

        ttk.Label(containerFrame, text = "Choose a Task to Change").grid(row = 0, column = 0, pady = 10, padx = 10)

        self.taskEntry = ttk.Combobox(containerFrame, state = "readonly")
        self.taskEntry.bind("<<ComboboxSelected>>", self.fillEntries)
        self.taskEntry.config(values = userTasks)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Enter a new Task Name").grid(row = 2, column = 0, pady = 10, padx = 10)

        self.newTaskEntry = ttk.Entry(containerFrame)
        self.newTaskEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Enter a new Task Start Time").grid(row = 4, column = 0, pady = 10, padx = 10)

        self.newTimeEntry = ttk.Entry(containerFrame)
        self.newTimeEntry.grid(row = 5, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(containerFrame, text = "Edit", command = self.submitEditTaskData)
        self.submitButton.grid(row = 6, column = 0, pady = 20, sticky = NSEW)
        # ~ Form Window ------------------------------------------------------
    def fillEntries(self, event):
        taskName = str(self.taskEntry.get())
        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        self.newTaskEntry.delete(0, END)
        self.newTimeEntry.delete(0, END)
        self.newTaskEntry.insert(0,rec['taskName'])
        self.newTimeEntry.insert(0,rec['taskTime'])
    def submitEditTaskData(self):
        taskName = self.taskEntry.get()
        if not taskName:
            mBox.showerror(title = "Task Edit Error", message= "Please choose task to edit")
            return 
        newTaskName = self.newTaskEntry.get()
        newTime = self.newTimeEntry.get()
        query = f'UPDATE Tasks SET taskName = \"{newTaskName}\", taskTime = \"{newTime}\" WHERE taskName = \"{taskName}\"'
        self.mTask.mTaskDB.sql_do(query)
        mBox.showinfo(title = "Sucess!", message= "Your task had been updated")