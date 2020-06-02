from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox

class RoutineFunctions():
    def __init__(self, mTask):
        self.mTask = mTask
    def newRoutine(self):
        userTasks = self.mTask.loadUserTasks()

        window = Toplevel(self.mTask.root)
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both", padx = 10, pady = 10)

        ttk.Label(container, text = "Enter a new routine").grid(row = 0, column = 0, padx = 10, pady = 10)

        self.routineName = StringVar()
        self.routineEntry = Entry(container, textvariable = self.routineName)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "Select a task to add").grid(row = 2, column = 0, padx = 10, pady = 10)

        self.addTaskBox = ttk.Combobox(container, values = userTasks, state = "readonly")
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
        self.submitButton.grid(row = 8, column = 0, padx = 10, pady =10, sticky = NSEW)

        self.routineEntry.bind("<KeyRelease>", self.updateRoutineAddGUI)
    def addTaskToRoutineGUI(self):
        '''
            Adds task labels into the rouineTasksFrame
        '''
        taskName = self.addTaskBox.get()
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
            query = f'INSERT INTO Routines VALUES (\"{routineName}\",\"{routineDescription}\")'
            self.mTask.mTaskDB.sql_do(query)
            tasksToAdd.append({'taskName': taskName, 'taskTime' : taskTime, 'routineName' : routineName})

        self.mTask.addRoutineToGUI(tasks = tasksToAdd, routineName=routineName)

    def loadRoutine(self):
        userRoutines = self.mTask.loadUserRoutines()

        window = Toplevel(self.mTask.root)
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both", padx = 10, pady = 10)

        ttk.Label(container, text = "Select a Routine").grid(row = 0, column = 0, padx = 10, pady = 10)

        self.routineEntry = ttk.Combobox(container, values = userRoutines, state = "readonly")
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        self.submitButton = ttk.Button(container, text = "Load", command = self.submitLoadRoutine)
        self.submitButton.grid(row = 2, column = 0, padx = 10, pady = 10)
    def submitLoadRoutine(self):
        routineName = self.routineEntry.get()
        if not routineName:
            mBox.showerror(title="Load Routine Error", message="Please select a routine to load")
            return
        query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\"'
        recs = list(self.mTask.mTaskDB.sql_query(query))
        tasksToAdd = []
        for rec in recs:
            tasksToAdd.append({'taskName': rec['taskName'], 'taskTime' : rec['taskTime'], 'routineName' : routineName})
        self.mTask.addRoutineToGUI(tasks=tasksToAdd, routineName= routineName)
    
    def editRoutine(self):
        userRoutines = self.mTask.loadUserRoutines()
        
        window = Toplevel(self.mTask.root)
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both", padx = 10, pady = 10)

        ttk.Label(container, text = "Select a Routine").grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.routineEntry = ttk.Combobox(container, values = userRoutines, state = "readonly")
        self.routineEntry.bind("<<ComboboxSelected>>", self.fillEntries)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10, columnspan = 2)

        ttk.Label(container, text = "Enter a new Routine Name").grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.newRoutineEntry = ttk.Entry(container)
        self.newRoutineEntry.grid(row = 3, column = 0, padx = 10, pady = 10, columnspan = 2)

        ttk.Label(container, text = "Select a Task Name to Add").grid(row = 4, column = 0, padx = 10, pady = 10)

        ttk.Label(container, text = "Select a Task Name to Remove").grid(row = 4, column = 1, padx = 10, pady = 10)

        self.taskToAdd = ttk.Combobox(container, state = "readonly")
        self.taskToAdd.grid(row = 5 , column = 0, padx = 10)

        self.taskToRemove = ttk.Combobox(container, state = "readonly")
        self.taskToRemove.grid(row = 5 , column = 1, padx = 10)

        self.taskToAddFrame = ttk.LabelFrame(container, text = "Tasks to Add")
        self.taskToAddFrame.grid(row = 7, column = 0)

        self.submitTaskToAdd = ttk.Button(container, text = "Add Task", command = self.addTaskToAddFrame)
        self.submitTaskToAdd.grid(row = 6, column = 0, padx = 10, pady = 5 )

        self.taskToRemoveFrame = ttk.LabelFrame(container, text = "Tasks to Remove")
        self.taskToRemoveFrame.grid(row = 7, column = 1)

        self.submitTaskToRemove = ttk.Button(container, text = "Add Task", command = self.addTaskToRemoveFrame)
        self.submitTaskToRemove.grid(row = 6, column = 1, padx = 10, pady = 5)

        ttk.Label(container, text = "Edit the Routine Description").grid(row = 8, column = 0, columnspan = 2, padx = 10, pady = 10)

        self.newDescriptionEntry = Text(container, wrap = WORD, width = 30, height = 10)
        self.newDescriptionEntry.grid(row = 9, column = 0, columnspan = 2, pady = 5, padx = 10)

        self.clearButton = ttk.Button(container, text = "Clear Tasks", command = self.clearEditRoutine)
        self.clearButton.grid(row = 10, column = 0, columnspan = 2, pady = 20)

        self.submitButton = ttk.Button(container, text = "Edit", command = self.submitEditRoutine)
        self.submitButton.grid(row = 11, column = 0, columnspan = 2, pady = 20)
    def fillEntries(self, event):
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
        self.taskToRemove.config(values = queuedTasks)
        for task in queuedTasks:
            userTasks.remove(task)
        self.taskToAdd.config(values = userTasks)
        query = f'SELECT * FROM Routines WHERE routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        self.newRoutineEntry.delete(0, END)
        self.newRoutineEntry.insert(0, routineName)
        self.newDescriptionEntry.delete("1.0", END)
        self.newDescriptionEntry.insert("1.0", rec['routineDescription'])
    def addTaskToRemoveFrame(self):
        taskName = self.taskToRemove.get()
        loadedRemoveTasks = [task.cget('text') for task in self.taskToRemoveFrame.winfo_children()]
        if taskName in loadedRemoveTasks:
            mBox.showerror(title = "Task Addition Error", message= "Please choose a task that is not in the list")
            return  
        ttk.Label(self.taskToRemoveFrame, text = taskName).grid(row = len(self.taskToRemoveFrame.winfo_children()), column = 0, sticky = W)
    def addTaskToAddFrame(self):
        taskName = self.taskToAdd.get()
        loadedAddTasks = [task.cget('text') for task in self.taskToAddFrame.winfo_children()]
        if taskName in loadedAddTasks:
            mBox.showerror(title = "Task Addition Error", message= "Please choose a task that is not in the list")
            return 
        ttk.Label(self.taskToAddFrame, text = taskName).grid(row = len(self.taskToAddFrame.winfo_children()), column = 0, sticky = W)
    def clearEditRoutine(self):
        for child in self.taskToAddFrame.winfo_children():
            child.destroy()
        for child in self.taskToRemoveFrame.winfo_children():
            child.destroy()
    def submitEditRoutine(self):
        
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

        

