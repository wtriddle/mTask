from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox

class TaskFunctions():
    '''
        Contains menu functions for the tasks sub-menu 
    '''
    def __init__(self, mTask):
        self.mTask = mTask # Instance of mTask class
        
    def newTask(self):
        '''
            Form for new task
        '''
        window = Toplevel(self.mTask.root)
        window.geometry("270x380-2450+250")
        window.resizable(False, False)
        containerFrame = ttk.Frame(window)
        containerFrame.pack(expand = True, fill = "both")

        ttk.Label(containerFrame, text = "New Task Name").grid(row = 0 , column = 0, pady = 5)

        self.taskEntry = ttk.Entry(containerFrame)
        self.taskEntry.grid(row = 1, column = 0, pady = 5)

        ttk.Label(containerFrame, text = "Target Start Time").grid(row = 2, column = 0)

        self.timeEntry = ttk.Entry(containerFrame)
        self.timeEntry.grid(row = 3, column = 0, pady = 5)

        ttk.Label(containerFrame, text = "Task Description").grid(row = 4, column = 0)

        self.descriptionEntry = Text(containerFrame, wrap = WORD, width = 30, height = 10)
        self.descriptionEntry.grid(row = 5, column = 0, pady = 5, padx = 10)

        self.submitButton = ttk.Button(containerFrame, text = "Create", command = self.submitNewTaskData)
        self.submitButton.grid(row = 6, column = 0, pady = 20, padx = 10, sticky = NSEW)

        self.taskEntry.focus()
    def submitNewTaskData(self):
        '''
            Evaluates user input, places valid data into database, and appends task to the default Tasks tab
        '''
        taskName = self.taskEntry.get()
        taskTime = self.timeEntry.get()
        taskDescription = self.descriptionEntry.get("1.0", END)

        if not taskName:
            mBox.showerror(title = "Task Creation Error", message= "Please enter a task name")
            return 

        userTasks = self.mTask.loadUserTasks()
        if taskName in userTasks:
            mBox.showerror(title = "Task Creation Error", message= "Please enter a unqiue task name")
            return 

        query = f'INSERT INTO Tasks (taskName, taskTime, taskDescription) VALUES (\"{taskName}\",\"{taskTime}\", \"{taskDescription}\")' 
        self.mTask.mTaskDB.sql_do(query)
        
        self.mTask.addTaskToGUI(**{'taskName': taskName, 'taskTime' : taskTime, 'routineName' : "Tasks"})
        

    def loadTask(self):
        '''
            Loads a task from the database, only for routines that have already been loaded previously
        '''
        userTasks = self.mTask.loadUserTasks()
        userRoutines = [str(self.mTask.tabControl.tab(i, option = "text")) for i in range(len(self.mTask.tabControl.winfo_children()))]

        # Form Window ------------------------------------------------------
        window = Toplevel(self.mTask.root)
        window.geometry("160x230-2450+250") 
        window.resizable(False, False)
        containerFrame = ttk.Frame(window)
        containerFrame.pack(expand = True, fill = "both")

        ttk.Label(containerFrame, text = "Choose a Task").grid(row = 0, column = 0, pady = 10, padx = 10)

        self.taskEntry = ttk.Combobox(containerFrame, state = "readonly")
        self.taskEntry.config(values = userTasks)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Choose a Routine").grid(row = 2, column = 0, pady = 10, padx = 10)

        self.routineEntry = ttk.Combobox(containerFrame, state = "readonly")
        self.routineEntry.config(values = userRoutines)
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(containerFrame, text = "Load", command = self.submitLoadTaskData)
        self.submitButton.grid(row = 4, column = 0, pady = 20, padx = 10, sticky = NSEW)
        # ~ Form Window ------------------------------------------------------
    def submitLoadTaskData(self):
        '''
            Evalutes user input in database and appends task to proper routine tab
        '''
        taskName = str(self.taskEntry.get())
        routineName = str(self.routineEntry.get())

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        taskTime = rec['taskTime']
        self.mTask.addTaskToGUI(**{'taskName': taskName, 'taskTime' : taskTime, 'routineName' : routineName})

    def editTask(self):
        '''
            Form to edit a pre-created task. Allows only for taskName, taskTime, and taskDescription changes, not the routine it is apart of.
        '''
        userTasks = self.mTask.loadUserTasks()

        # Form Window ------------------------------------------------------
        window = Toplevel(self.mTask.root)
        window.geometry("270x620-2450+250")  
        window.resizable(False, False)
        containerFrame = ttk.Frame(window)
        containerFrame.pack(expand = True, fill = "both")

        ttk.Label(containerFrame, text = "Choose a Task to Change").grid(row = 0, column = 0, pady = 10, padx = 10)

        self.taskEntry = ttk.Combobox(containerFrame, state = "readonly")
        self.taskEntry.bind("<<ComboboxSelected>>", self.setUpEntries)
        self.taskEntry.config(values = userTasks)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Choose the routine to alter it from").grid(row = 2, column = 0, pady = 10, padx = 10)

        self.routineEntry = ttk.Combobox(containerFrame, state = "disabled")
        self.routineEntry.bind("<<ComboboxSelected>>", self.fillEntries)
        self.routineEntry.config()
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Enter a new Task Name").grid(row = 4, column = 0, pady = 10, padx = 10)

        self.newTaskEntry = ttk.Entry(containerFrame, state = "disabled")
        self.newTaskEntry.grid(row = 5, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Enter a new Task Start Time").grid(row = 6, column = 0, pady = 10, padx = 10)

        self.newTimeEntry = ttk.Entry(containerFrame, state = "disabled")
        self.newTimeEntry.grid(row = 7, column = 0, padx = 10, pady = 10)

        ttk.Label(containerFrame, text = "Change the Description").grid(row = 8, column = 0, pady = 10, padx = 10)

        self.newDescriptionEntry = Text(containerFrame, wrap = WORD, state = "disabled", height = 10, width = 30)
        self.newDescriptionEntry.grid(row = 9, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(containerFrame, text = "Edit", command = self.submitEditTaskData)
        self.submitButton.grid(row = 10, column = 0, pady = 20, padx = 10, sticky = NSEW)
        # ~ Form Window ------------------------------------------------------
    def setUpEntries(self, event):
        '''
            Updates the routine selection to show only the routines for which the task is apart of
        '''
        taskName = str(self.taskEntry.get())

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\"'
        recs = list(self.mTask.mTaskDB.sql_query(query))
        userRoutines = [rec['routineName'] for rec in recs]

        self.routineEntry.config(values = userRoutines, state = "readonly")
    def fillEntries(self,event):
        '''
            Fills the editing fields with the current data from the database for interactive UI experinece.
        '''
        taskName = str(self.taskEntry.get())
        routineName = str(self.routineEntry.get())

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))

        self.newTaskEntry.config(state = "enabled")
        self.newTimeEntry.config(state = "enabled")
        self.newDescriptionEntry.config(state = "normal")

        self.newTaskEntry.delete(0, END)
        self.newTimeEntry.delete(0, END)
        self.newDescriptionEntry.delete("1.0", END)

        self.newTaskEntry.insert(0,rec['taskName'])
        self.newTimeEntry.insert(0,rec['taskTime'])
        self.newDescriptionEntry.insert("1.0",rec['taskDescription'])
    def submitEditTaskData(self):
        ''' 
            Evaluted edited data, then submits it to the database. Task is NOT updated in GUI after this method.
        '''
        taskName = self.taskEntry.get()
        routineName = str(self.routineEntry.get())

        if not taskName:
            mBox.showerror(title = "Task Edit Error", message= "Please choose task to edit")
            return 
        elif not routineName:
            mBox.showerror(title = "Task Edit Error", message= "Please choose a routine the the task is under to edit")
            return

        newTaskName = self.newTaskEntry.get()
        newTime = self.newTimeEntry.get()
        newDescription = self.newDescriptionEntry.get("1.0", END)
        
        query = f'UPDATE Tasks SET taskName = \"{newTaskName}\", taskTime = \"{newTime}\", taskDescription = \"{newDescription}\" WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)
        mBox.showinfo(title = "Sucess!", message= "Your task had been updated")
    
    def configRecurringTask(self):
        userTasks = self.mTask.loadUserTasks(routineName="Tasks")

        # Form Window -----------------------------------------------
        window = Toplevel(self.mTask.root)
        window.geometry("640x480-2450+250")
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both")

        ttk.Label(container, text = "Choose a task to configure").grid(row = 0, column = 0, padx = 10, pady = 10)

        self.taskEntry = ttk.Combobox(container, values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.fillConfigEntries)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "This task shall occur: ").grid(row = 2, column = 0, padx = 10, pady = 10)

        recurringDays = [("Every " + str(x) + " days ") for x in range(2,7)]
        recurringDays.insert(0, "Every other day")
        recurringDays.insert(0, "Daily")

        self.daysEntry = ttk.Combobox(container, values = recurringDays)
        self.daysEntry.grid(row = 3, column = 0, padx = 10, pady = 10)
        # ~ Form Window -----------------------------------------------
    def fillConfigEntries(self, event):
        print("Filling entires with proper data")

    def getwindowInfo(self, event):
        window = event.widget
        print("x : " + str(window.winfo_width()))
        print("y : " + str(window.winfo_height()))