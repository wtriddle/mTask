from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox
from datetime import datetime

class RoutineFunctions():
    def __init__(self, mTask):
        self.mTask = mTask

    def newRoutine(self):
        userTasks = self.mTask.loadUserTasks()

        # Form Window ------------------------------------------------------
        self.window = Toplevel(self.mTask.root)
        self.window.geometry("-2450+250")  
        container = ttk.Frame(self.window)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1)

        ttk.Label(container, text = "Enter a new routine").grid(row = 0, column = 0, padx = 10, pady = 10)

        self.routineName = StringVar()
        self.routineEntry = ttk.Entry(container, textvariable = self.routineName)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "Select a task to add").grid(row = 2, column = 0, padx = 10, pady = 10)

        self.addTaskBox = ttk.Combobox(container, values = userTasks, state = "readonly")
        self.addTaskBox.bind("<<ComboboxSelected>>",lambda e: container.focus())
        self.addTaskBox.grid(row = 3, column = 0, padx = 10, pady = 10)
        
        # Rows not in order because routineTaskFrame needs to be intialized before button can be clicked
        self.routineTasksFrame = ttk.LabelFrame(container, text = self.routineName.get())
        self.routineTasksFrame.grid(row = 5, column = 0, padx = 10, pady = 10)

        self.addTaskButton = ttk.Button(container, text = "Add task to Routine", command = self.addTaskToRoutineGUI)
        self.addTaskButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "Describe the Routine").grid(row = 6, column = 0, padx = 10, pady = 10)

        self.descriptionEntry = Text(container, wrap = WORD, width = 30, height = 10)
        self.descriptionEntry.grid(row = 7, column = 0, padx = 10, pady = 10)
        
        self.submitButton = ttk.Button(container, text = "Create Routine", command = self.submitNewRoutine)
        self.submitButton.grid(row = 8, column = 0, padx = 10, pady = 10)

        self.routineEntry.bind("<KeyRelease>", self.updateRoutineAddGUI)
        self.routineEntry.focus()
        # ~ Form Window ------------------------------------------------------
    def addTaskToRoutineGUI(self):
        '''
            Adds task labels into the rouineTasksFrame
        '''
        taskName = self.addTaskBox.get()
        
        # Ensure task is unique inside loading frame
        loadedTasks = [task.cget('text') for task in self.routineTasksFrame.winfo_children()]
        if taskName in loadedTasks:
            mBox.showerror(title = "Task Additon Error", message= "Please select a task that has not been added to the routine list")
            return 

        ttk.Label(self.routineTasksFrame, text = taskName).grid(row = len(self.routineTasksFrame.winfo_children()), column = 0, sticky = W)
    def updateRoutineAddGUI(self, event):
        '''
            Updates widget text in newRoutineWindow to match entered routine name
        '''
        routineName = self.routineName.get()

        self.routineTasksFrame.config(text = routineName + " Tasks")
        self.addTaskButton.config(text = "Add task to " + routineName)
        self.submitButton.config(text = "Create " + routineName + " Routine")
    def submitNewRoutine(self):
        '''
            Asseses user input from newRoutine entry form. If valid, new routine is added to the GUI
        '''

        routineName = self.routineName.get()
        routineDescription = self.descriptionEntry.get("1.0", END)
        userRoutines = self.mTask.loadUserRoutines()

        if routineName in userRoutines:
            mBox.showerror(title = "Routine Creation Error", message= "Please select a routine name that is has not been taken")
            return 

        loadedTasks = [task.cget('text') for task in self.routineTasksFrame.winfo_children()]
        tasksToAdd = []
        for taskName in loadedTasks:
            query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
            rec = dict(self.mTask.mTaskDB.sql_query_row(query))

            taskName = rec['taskName']
            taskTime = rec['taskTime']
            taskDescription = rec['taskDescription']

            query = f'INSERT INTO Tasks (taskName, taskTime, taskDescription, routineName) VALUES (\"{taskName}\",\"{taskTime}\", \"{taskDescription}\", \"{routineName}\")' 
            self.mTask.mTaskDB.sql_do(query)

            query = f'INSERT INTO Routines (routineName, routineDescription) VALUES (\"{routineName}\",\"{routineDescription}\")'
            self.mTask.mTaskDB.sql_do(query)

            tasksToAdd.append({'taskName': taskName, 'taskTime' : taskTime, 'routineName' : routineName})

        self.mTask.addRoutineToGUI(tasks = tasksToAdd, routineName=routineName)

    def loadRoutine(self):
        userRoutines = self.mTask.loadUserRoutines()

        # Form Window ------------------------------------------------------
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")  
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1)

        ttk.Label(container, text = "Select a Routine").grid(row = 0, column = 0, padx = 30, pady = 10)

        self.routineEntry = ttk.Combobox(container, values = userRoutines, state = "readonly")
        self.routineEntry.bind("<<ComboboxSelected>>",lambda e: container.focus())
        self.routineEntry.grid(row = 1, column = 0, padx = 30, pady = 10)

        self.submitButton = ttk.Button(container, text = "Load", command = self.submitLoadRoutine)
        self.submitButton.grid(row = 2, column = 0, padx = 30, pady = 10)
        # ~ Form Window ------------------------------------------------------
    def submitLoadRoutine(self):
        '''
           Evalutes user input and updates the GUI with the loaded routine.
        '''
        routineName = self.routineEntry.get()

        if not routineName:
            mBox.showerror(title="Load Routine Error", message="Please select a routine to load")
            return

        self.mTask.loadSpecificRoutine(routineName=routineName)
    
    def editRoutine(self):
        '''
            Form which allows routine properties to change, as well as to add/remove tasks that are associated with a particular routine
        '''
        userRoutines = self.mTask.loadUserRoutines()

        # Form Window ------------------------------------------------------
        self.window = Toplevel(self.mTask.root)
        self.window.geometry("-2450+250") 
        self.container = ttk.Frame(self.window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1)
        self.container.columnconfigure(1, weight = 1)

        ttk.Label(self.container, text = "Select a Routine").grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.routineEntry = ttk.Combobox(self.container, values = userRoutines, state = "readonly")
        self.routineEntry.bind("<<ComboboxSelected>>", self.fillEntries)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10, columnspan = 2)

        ttk.Label(self.container, text = "Enter a new Routine Name").grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.newRoutineEntry = ttk.Entry(self.container)
        self.newRoutineEntry.grid(row = 3, column = 0, padx = 10, pady = 10, columnspan = 2)

        ttk.Label(self.container, text = "Select a Task Name to Add").grid(row = 4, column = 0, padx = 10, pady = 10)

        ttk.Label(self.container, text = "Select a Task Name to Remove").grid(row = 4, column = 1, padx = 10, pady = 10)

        self.taskToAdd = ttk.Combobox(self.container, state = "readonly")
        self.taskToAdd.bind("<<ComboboxSelected>>",lambda e: self.container.focus())
        self.taskToAdd.grid(row = 5 , column = 0, padx = 10)

        self.taskToRemove = ttk.Combobox(self.container, state = "readonly")
        self.taskToRemove.bind("<<ComboboxSelected>>",lambda e: self.container.focus())
        self.taskToRemove.grid(row = 5 , column = 1, padx = 10)

        self.taskToAddFrame = ttk.LabelFrame(self.container, text = " Tasks to Add ")
        self.taskToAddFrame.grid(row = 7, column = 0)

        self.submitTaskToAdd = ttk.Button(self.container, text = "Add Task", command = self.addTaskToAddFrame)
        self.submitTaskToAdd.grid(row = 6, column = 0, padx = 10, pady = 5 )

        self.taskToRemoveFrame = ttk.LabelFrame(self.container, text = " Tasks to Remove ")
        self.taskToRemoveFrame.grid(row = 7, column = 1)

        self.submitTaskToRemove = ttk.Button(self.container, text = "Add Task", command = self.addTaskToRemoveFrame)
        self.submitTaskToRemove.grid(row = 6, column = 1, padx = 10, pady = 5)

        ttk.Label(self.container, text = "Edit the Routine Description").grid(row = 8, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.newDescriptionEntry = Text(self.container, wrap = WORD, width = 30, height = 10)
        self.newDescriptionEntry.grid(row = 9, column = 0, columnspan = 2, pady = 5, padx = 10)

        self.clearButton = ttk.Button(self.container, text = "Clear Tasks", command = self.clearEditRoutine)
        self.clearButton.grid(row = 10, column = 0, columnspan = 2, pady = 20)

        self.submitButton = ttk.Button(self.container, text = "Edit", command = self.submitEditRoutine)
        self.submitButton.grid(row = 11, column = 0, columnspan = 2, pady = 20)
        # ~ Form Window ------------------------------------------------------
    def fillEntries(self, event):
        '''
            Fills routine edit form widgets with proper values based on the selected routine
        '''
        self.container.focus()
        routineName = self.routineEntry.get()
        userTasks = self.mTask.loadUserTasks()

        if routineName == "Tasks":
            self.taskToRemove.config(values = [])
            return

        query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\"'
        recs = list(self.mTask.mTaskDB.sql_query(query))

        queuedTasks = []
        if recs:
            queuedTasks = [rec['taskName'] for rec in recs]

        for task in queuedTasks:
            userTasks.remove(task)

        query = f'SELECT * FROM Routines WHERE routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))

        self.taskToAdd.config(values = userTasks)
        self.taskToRemove.config(values = queuedTasks)

        self.newRoutineEntry.delete(0, END)
        self.newDescriptionEntry.delete("1.0", END)

        self.newRoutineEntry.insert(0, routineName)
        self.newDescriptionEntry.insert("1.0", rec['routineDescription'])
    def addTaskToRemoveFrame(self):
        '''
            Adds the selected task from the corellating combobox to a labelframe, which specifies the tasks to remove from currently selected routine
        '''
        taskName = self.taskToRemove.get()

        loadedRemoveTasks = [task.cget('text') for task in self.taskToRemoveFrame.winfo_children()]
        if taskName in loadedRemoveTasks:
            mBox.showerror(title = "Task Addition Error", message= "Please choose a task that is not in the list")
            return  

        ttk.Label(self.taskToRemoveFrame, text = taskName).grid(row = len(self.taskToRemoveFrame.winfo_children()), column = 0, sticky = W)

    def addTaskToAddFrame(self):
        '''
            Adds the selected task from the task combobox to a labelframe, which specifies the tasks to add from currently selected routine
        '''
        taskName = self.taskToAdd.get()

        loadedAddTasks = [task.cget('text') for task in self.taskToAddFrame.winfo_children()]
        if taskName in loadedAddTasks:
            mBox.showerror(title = "Task Addition Error", message= "Please choose a task that is not in the list")
            return 

        ttk.Label(self.taskToAddFrame, text = taskName).grid(row = len(self.taskToAddFrame.winfo_children()), column = 0, sticky = W)
    def clearEditRoutine(self):
        '''
            Removes all tasks from the add to and remove from task frames inside of the edit routine form
        '''
        for child in self.taskToAddFrame.winfo_children():
            child.destroy()

        for child in self.taskToRemoveFrame.winfo_children():
            child.destroy()
    def submitEditRoutine(self):
        '''
            Evalutates the edited data and submits the data to the database. Routine is NOT updated in the GUI after this change
        '''
        oldRoutineName = self.routineEntry.get()
        newRoutineName = self.newRoutineEntry.get()
        routineDescription = self.newDescriptionEntry.get("1.0", END)
        
        query = f'UPDATE Routines SET routineDescription = \"{routineDescription}\" WHERE routineName = \"{oldRoutineName}\"'
        self.mTask.mTaskDB.sql_do(query)

        if oldRoutineName != newRoutineName:
            query = f'UPDATE Tasks SET routineName = \"{newRoutineName}\" WHERE routineName = \"{oldRoutineName}\"'
            self.mTask.mTaskDB.sql_do(query)

            query = f'UPDATE Routines SET routineName = \"{newRoutineName}\" WHERE routineName = \"{oldRoutineName}\"'
            self.mTask.mTaskDB.sql_do(query)
        
        tasksToAdd = [task.cget("text") for task in self.taskToAddFrame.winfo_children()]
        tasksToRemove = [task.cget("text") for task in self.taskToRemoveFrame.winfo_children()]
        
        for taskName in tasksToAdd:
            query = f'UPDATE Tasks SET routineName = \"{newRoutineName}\" WHERE taskName = \"{taskName}\"'
            self.mTask.mTaskDB.sql_do(query)

        for taskName in tasksToRemove:
            query = f'UPDATE Tasks SET routineName = \"Tasks\" WHERE taskName = \"{taskName}\"'
            self.mTask.mTaskDB.sql_do(query)
        
        mBox.showinfo(title = "Success!", message="Your routine has been successfully updated!")

    def configRecurringRoutine(self):
        userRoutines = self.mTask.loadUserRoutines()

        # Form window ---------------------------------------------
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1)

        ttk.Label(self.container, text = "Choose a Routine to configure").grid(row = 0, column = 0, padx = 10, pady = 10)

        self.routineEntry = ttk.Combobox(self.container, values = userRoutines)
        self.routineEntry.bind("<<ComboboxSelected>>", self.fillConfigEntries)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(self.container, text = "This routine shall occur: ").grid(row = 2, column = 0, padx = 10, pady = 10)

        self.reccuringDays = [("Every " + str(x) + " days ") for x in range(2,7)]
        self.reccuringDays.insert(0, "Every other day")
        self.reccuringDays.insert(0, "Daily")

        self.daysEntry = ttk.Combobox(self.container, values = self.reccuringDays)
        self.daysEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(self.container, text = "Create Reccurance", command = self.submitReccuringTask)
        self.submitButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        self.removeButton = ttk.Button(self.container, text = "Remove reccurance", command = self.removeReccurance, state = "disabled")
        self.removeButton.grid(row = 5, column = 0, padx = 10, pady = 10)
        # ~ Form window ---------------------------------------------
    def fillConfigEntries(self, event):
        routineName = self.routineEntry.get()
        self.container.focus()

        query = f'SELECT * FROM Routines WHERE routineName = \"{routineName}\"'
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
        routineName = self.routineEntry.get()
        frequency = self.daysEntry.get()

        if frequency == "Daily":
            frequency = 1
        elif frequency == "Every Other Day":
            frequency = 2
        else:
            frequency = int(frequency[6]) + 1 # Retrieve only the number

        refDate = datetime.today().date()
        query = f'UPDATE Routines SET recurFrequency = \"{frequency}\", recurRefDate = \"{refDate}\" WHERE routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)

        if self.submitButton.cget("text") == "Create Reccurance":
            mBox.showinfo(title = "Creation Success!", message= "You have created a routine reccurance")
        elif self.submitButton.cget("text") == "Alter Reccurance":
            mBox.showinfo(title = "Alter Success!", message= "You have altered a routine reccurance")
    def removeReccurance(self):
        routineName = self.routineEntry.get()

        query = f'UPDATE Routines SET recurFrequency = NULL, recurRefDate = NULL WHERE routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)
        
        mBox.showinfo(title = "Success!", message= "You have removed this routine occurance")    
    def getwindowInfo(self, event):
        window = event.widget
        print("x : " + str(window.winfo_width()))
        print("y : " + str(window.winfo_height()))

