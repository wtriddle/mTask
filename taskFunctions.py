from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox
from datetime import datetime

class TaskFunctions():
    '''
        Contains menu functions for the tasks sub-menu 
    '''
    def __init__(self, mTask):
        self.mTask = mTask # Instance of mTask class
        
    def newTask(self):
        '''
            Form for new task creation
        '''
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1)

        ttk.Label(container, text = "New Task Name").grid(row = 0 , column = 0, pady = 5)

        self.taskEntry = ttk.Entry(container)
        self.taskEntry.grid(row = 1, column = 0, pady = 5)

        ttk.Label(container, text = "Target Start Time").grid(row = 2, column = 0)

        self.timeEntry = ttk.Entry(container)
        self.timeEntry.grid(row = 3, column = 0, pady = 5)

        ttk.Label(container, text = "Task Description").grid(row = 4, column = 0)

        self.descriptionEntry = Text(container, wrap = WORD, width = 30, height = 10)
        self.descriptionEntry.grid(row = 5, column = 0, pady = 5, padx = 10)

        self.submitButton = ttk.Button(container, text = "Create", command = self.submitNewTaskData)
        self.submitButton.grid(row = 6, column = 0, pady = 20, padx = 10)

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
            Loads a task from the database, only from routines that are currently loaded into the GUI
        '''
        userTasks = self.mTask.loadUserTasks()
        userRoutines = [str(self.mTask.tabControl.tab(i, option = "text")) for i in range(len(self.mTask.tabControl.winfo_children()))]

        # Form Window ------------------------------------------------------
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250") 
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1)

        ttk.Label(container, text = "Choose a Task").grid(row = 0, column = 0, pady = 10, padx = 10)

        self.taskEntry = ttk.Combobox(container, state = "readonly", values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>",lambda e: container.focus())
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "Choose a Routine").grid(row = 2, column = 0, pady = 10, padx = 10)

        self.routineEntry = ttk.Combobox(container, state = "readonly",values = userRoutines)
        self.routineEntry.bind("<<ComboboxSelected>>",lambda e: container.focus())
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(container, text = "Load", command = self.submitLoadTaskData)
        self.submitButton.grid(row = 4, column = 0, pady = 20, padx = 10)
        # ~ Form Window ------------------------------------------------------
    def submitLoadTaskData(self):
        '''
            Evalutes user input in database and appends task to proper routine tab
        '''
        taskName = str(self.taskEntry.get())
        routineName = str(self.routineEntry.get())
        if not taskName or not routineName:
            mBox.showerror(title="Task Load Error", message="Please select a routine or a task to load from")

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
        window.geometry("-2450+250")  
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1)

        ttk.Label(self.container, text = "Choose a Task to Change").grid(row = 0, column = 0, pady = 10, padx = 10)

        self.taskEntry = ttk.Combobox(self.container, state = "readonly", font = 40)
        self.taskEntry.bind("<<ComboboxSelected>>", self.fillRoutinesBox)
        self.taskEntry.config(values = userTasks)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(self.container, text = "Choose the routine to alter it from").grid(row = 2, column = 0, pady = 10, padx = 10)

        self.routineEntry = ttk.Combobox(self.container, state = "disabled")
        self.routineEntry.bind("<<ComboboxSelected>>", self.fillPropertyEntries)
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        ttk.Label(self.container, text = "Enter a new Task Name").grid(row = 4, column = 0, pady = 10, padx = 10)

        self.newTaskEntry = ttk.Entry(self.container, state = "disabled")
        self.newTaskEntry.grid(row = 5, column = 0, padx = 10, pady = 10)

        ttk.Label(self.container, text = "Enter a new Task Start Time").grid(row = 6, column = 0, pady = 10, padx = 10)

        self.newTimeEntry = ttk.Entry(self.container, state = "disabled")
        self.newTimeEntry.grid(row = 7, column = 0, padx = 10, pady = 10)

        ttk.Label(self.container, text = "Change the Description").grid(row = 8, column = 0, pady = 10, padx = 10)

        self.newDescriptionEntry = Text(self.container, wrap = WORD, state = "disabled", height = 10, width = 30)
        self.newDescriptionEntry.grid(row = 9, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(self.container, text = "Edit", command = self.submitEditTaskData)
        self.submitButton.grid(row = 10, column = 0, pady = 20, padx = 10)
        # ~ Form Window ------------------------------------------------------
    def fillRoutinesBox(self, event):
        '''
            Updates the routine Combobox selection to show only the routines from which the task is apart of
        '''
        self.container.focus()
        taskName = str(self.taskEntry.get())

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\"'
        recs = list(self.mTask.mTaskDB.sql_query(query))
        userRoutines = [rec['routineName'] for rec in recs]

        self.routineEntry.config(values = userRoutines, state = "readonly")
    def fillPropertyEntries(self,event):
        '''
            Fills the editing fields with the current data from the database about the selected task-routine pair
        '''
        self.container.focus()
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
            Evaluted edited task-routine data, then submits it to the database. Task is NOT updated in GUI after this method.
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
        window.geometry("-2450+250")
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1)

        ttk.Label(container, text = "Choose a task to configure").grid(row = 0, column = 0, padx = 10, pady = 10)

        self.taskEntry = ttk.Combobox(container, values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.fillConfigEntries)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "This task shall occur: ").grid(row = 2, column = 0, padx = 10, pady = 10)

        self.reccuringDays = [("Every " + str(x) + " days ") for x in range(2,7)]
        self.reccuringDays.insert(0, "Every other day")
        self.reccuringDays.insert(0, "Daily")

        self.daysEntry = ttk.Combobox(container, values = self.reccuringDays)
        self.daysEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(container, text = "Create Reccurance", command = self.submitReccuringTask)
        self.submitButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        self.removeButton = ttk.Button(container, text = "Remove reccurance", command = self.removeReccurance, state = "disabled")
        self.removeButton.grid(row = 5, column = 0, padx = 10, pady = 10)
        # ~ Form Window -----------------------------------------------
    def fillConfigEntries(self, event):
        taskName = self.taskEntry.get()

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        recurFrequency = rec['recurFrequency']

        if recurFrequency:
            self.daysEntry.current(self.reccuringDays.index(recurFrequency))
            self.submitButton.config(text = "Alter Reccurance")
            self.removeButton.config(state = "enabled")
        else:
            self.daysEntry.current(0)
            self.submitButton.config(text = "Create Reccurance")
            self.removeButton.config(state = "disabled")
    def submitReccuringTask(self):
        taskName = self.taskEntry.get()
        frequency = self.daysEntry.get()

        if frequency == "Daily":
            frequency = 1
        elif frequency == "Every Other Day":
            frequency = 2
        else:
            frequency = int(frequency[6]) + 1 # Retrieve only the number

        refDate = datetime.today().date()
        query = f'UPDATE Tasks SET recurFrequency = \"{frequency}\", recurRefDate = \"{refDate}\" WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        self.mTask.mTaskDB.sql_do(query)

        if self.submitButton.cget("text") == "Create Reccurance":
            mBox.showinfo(title = "Creation Success!", message= "You have created a task reccurance")
        elif self.submitButton.cget("text") == "Alter Reccurance":
            mBox.showinfo(title = "Alter Success!", message= "You have altered a task reccurance")
    def removeReccurance(self):
        taskName = self.taskEntry.get()

        query = f'UPDATE Tasks SET recurFrequency = NULL, recurRefDate = NULL WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        self.mTask.mTaskDB.sql_do(query)

        mBox.showinfo(title = "Success!", message= "You have removed this task occurance")
    def getwindowInfo(self, event):
        window = event.widget
        print("x : " + str(window.winfo_width()))
        print("y : " + str(window.winfo_height()))