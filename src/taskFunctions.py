from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox
from datetime import datetime

class TaskFunctions():
    '''
        Contains menu functions for the tasks sub-menu. Includes the functionality for each pop-up form.
    '''
    def __init__(self, mTask):
        self.mTask = mTask # Instance of mTask class

    def newTask(self):
        '''
            Pop-up form for new task creation
        '''
        # New pop-up window creation
        window = Toplevel(self.mTask.root)
        window.title('Create a New Task')
        window.geometry("-2450+250")
        window.bind("<KeyRelease>", self.refreshNewTask) # Refresh GUI for UI/UX 

        # Main container to hold form widgets
        container = ttk.Frame(window)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # New task input area
        ttk.Label(container, text = "New Task Name").grid(row = 0 , column = 0, pady = 5)
        self.taskEntry = ttk.Entry(container)
        self.taskEntry.grid(row = 1, column = 0, pady = 5)

        # Start time for task input area
        ttk.Label(container, text = "Target Start Time").grid(row = 2, column = 0)
        self.timeEntry = ttk.Entry(container)
        self.timeEntry.grid(row = 3, column = 0, pady = 5)

        # Description for task input area
        ttk.Label(container, text = "Task Description").grid(row = 4, column = 0)
        self.descriptionEntry = Text(container, wrap = WORD, width = 30, height = 10)
        self.descriptionEntry.grid(row = 5, column = 0, pady = 5, padx = 10)

        # Submission of content action
        self.submitButton = ttk.Button(container, text = "Create", command = self.submitNewTaskData, state = "disabled")
        self.submitButton.grid(row = 6, column = 0, pady = 20, padx = 10)

        # Allow instant typing into new task name input field when window is created
        self.taskEntry.focus()
    def refreshNewTask(self, event):
        '''
            Checks the new task form for changes to the input fields every key release.
            Refreshes the GUI based on the values of the input fields.
        '''
        taskName = self.taskEntry.get()
        taskTime = self.timeEntry.get()

        # Submission can only occur when a task name and time are specified
        if taskName and taskTime:
            self.submitButton.config(state = "enabled")
        else:
            self.submitButton.config(state = "disabled")
    def submitNewTaskData(self):
        '''
            Evaluates user input from the new task pop-up form 
            Places the task data into the defualt Tasks table if the task name is unique
            Updates the GUI Tasks routine tab to include newly created task
        '''
        taskName = self.taskEntry.get()
        taskTime = self.timeEntry.get()
        taskDescription = self.descriptionEntry.get("1.0", END)
        
        userTasks = self.mTask.loadUserTasks()
        if taskName in userTasks:
            mBox.showerror(title = "Task Creation Error", message= "Please enter a unqiue task name")
            return 

        query = f'INSERT INTO Tasks (taskName, taskTime, taskDescription) VALUES (\"{taskName}\",\"{taskTime}\", \"{taskDescription}\")' 
        self.mTask.mTaskDB.sql_do(query)
        
        self.mTask.addTaskToGUI(**{
            'taskName': taskName, 
            'taskTime' : taskTime,
            'taskDescription' : taskDescription, 
            'routineName' : "Tasks"})
        

    def loadTask(self):
        '''
            Pop-up form for loading a task into a specific routine tab currently in the GUI.
        '''
        userTasks = self.mTask.loadUserTasks()
        userRoutines = [str(self.mTask.nb.tab(i, option = "text")) for i in range(len(self.mTask.nb.winfo_children()))]

        # Form Window ------------------------------------------------------
        
        # New pop-up window creation
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")

        # Main container frame for all form widgets
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Selection of a task input area
        ttk.Label(self.container, text = "Choose a Task").grid(row = 0, column = 0, pady = 10, padx = 10)
        self.taskEntry = ttk.Combobox(self.container, state = "readonly", values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.refreshLoadTask) # Refresh GUI for UI/UX 
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Selection of a routine tab input area
        ttk.Label(self.container, text = "Choose a Routine").grid(row = 2, column = 0, pady = 10, padx = 10)
        self.routineEntry = ttk.Combobox(self.container, state = "readonly",values = userRoutines)
        self.routineEntry.bind("<<ComboboxSelected>>", self.refreshLoadTask) # Refresh GUI for UI/UX 
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Action button for loading a task
        self.submitButton = ttk.Button(self.container, text = "Load", command = self.submitLoadTaskData, state = "disabled")
        self.submitButton.grid(row = 4, column = 0, pady = 20, padx = 10)
        # ~ Form Window ------------------------------------------------------
    def refreshLoadTask(self, event):
        '''
            Checks the load task form input fields every combo box selection.
            Refreshes the submission button based on current state of input fields.
        '''
        taskName = self.taskEntry.get()
        routineName = self.routineEntry.get()

        # Task can only be loaded if both a task name and routine tab are specified
        if taskName and routineName:
            self.submitButton.config(state = "enabled")
        else:
            self.submitButton.config(state = "disabled")

        self.container.focus() # Remove blue background for comobox when selected
    def submitLoadTaskData(self):
        '''
            Reads comobox inputs and loads the specific task into the desired routine tab
            If the task is not apart of the routine, default Tasks data will be loaded instead of routine-task specific data
        '''
        taskName = self.taskEntry.get()
        routineName = self.routineEntry.get()

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        rec = self.mTask.mTaskDB.sql_query_row(query)

        # Load default Tasks rec if routine-task specific rec doesn't exist
        if not rec:
            query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
            rec = self.mTask.mTaskDB.sql_query_row(query)

        rec = dict(rec)
        taskTime = rec['taskTime']
        taskDescription = rec['taskDescription']
        self.mTask.addTaskToGUI(**{
            'taskName': taskName, 
            'taskTime' : taskTime,
            'taskDescription' : taskDescription, 
            'routineName' : routineName})


    def editTask(self):
        '''
            Form to edit a pre-created task. 
            Editing allowed for taskName, taskTime, and taskDescription, for a specific task-routine relation.
            Does not edit which routine the task is apart of.
        '''
        userTasks = self.mTask.loadUserTasks()

        # Form Window ------------------------------------------------------

        # Popup window creation
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")
        
        # Main container for form widgets
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Selection of task input area
        ttk.Label(self.container, text = "Choose a Task to Change").grid(row = 0, column = 0, pady = 10, padx = 10)
        self.taskEntry = ttk.Combobox(self.container, state = "readonly", values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.showEditableRoutines)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Selection of routine input area
        ttk.Label(self.container, text = "Choose the routine to alter it from").grid(row = 2, column = 0, pady = 10, padx = 10)
        self.routineEntry = ttk.Combobox(self.container, state = "disabled")
        self.routineEntry.bind("<<ComboboxSelected>>", self.showEditableData)
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Edit task name input area
        ttk.Label(self.container, text = "Enter a new Task Name").grid(row = 4, column = 0, pady = 10, padx = 10)
        self.newTaskEntry = ttk.Entry(self.container, state = "disabled")
        self.newTaskEntry.grid(row = 5, column = 0, padx = 10, pady = 10)

        # Edit task time input area
        ttk.Label(self.container, text = "Enter a new Task Start Time").grid(row = 6, column = 0, pady = 10, padx = 10)
        self.newTimeEntry = ttk.Entry(self.container, state = "disabled")
        self.newTimeEntry.grid(row = 7, column = 0, padx = 10, pady = 10)

        # Edit task description area
        ttk.Label(self.container, text = "Change the Description").grid(row = 8, column = 0, pady = 10, padx = 10)
        self.newDescriptionEntry = Text(self.container, wrap = WORD, state = "disabled", height = 10, width = 30)
        self.newDescriptionEntry.grid(row = 9, column = 0, padx = 10, pady = 10)

        # Submission of edited content action
        self.submitButton = ttk.Button(self.container, text = "Edit", command = self.submitEditTaskData)
        self.submitButton.grid(row = 10, column = 0, pady = 20, padx = 10)
        # ~ Form Window ------------------------------------------------------
    def showEditableRoutines(self, event):
        '''
            Updates the routine Combobox selection to show only the routines from which the task is apart of
        '''
        taskName = self.taskEntry.get()

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\"'
        recs = list(self.mTask.mTaskDB.sql_query(query))
        userRoutines = [rec['routineName'] for rec in recs]

        self.routineEntry.config(values = userRoutines, state = "readonly")

        self.container.focus() # Remove blue background for task comobox when selected
    def showEditableData(self,event):
        '''
            Fills the task editing fields with the current data from the database about the selected task-routine relation
        '''
        taskName = self.taskEntry.get()
        routineName = self.routineEntry.get()

        # Query the task-routine specific data
        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))

        # Enable editing fields
        self.newTaskEntry.config(state = "enabled")
        self.newTimeEntry.config(state = "enabled")
        self.newDescriptionEntry.config(state = "normal")

        # Delete any content in editing fields
        self.newTaskEntry.delete(0, END)
        self.newTimeEntry.delete(0, END)
        self.newDescriptionEntry.delete("1.0", END)
        
        # Replace editing fields with current data
        self.newTaskEntry.insert(0,rec['taskName'])
        self.newTimeEntry.insert(0,rec['taskTime'])
        self.newDescriptionEntry.insert("1.0",rec['taskDescription'])

        self.container.focus() # Remove blue background for task comobox when selected
    def submitEditTaskData(self):
        ''' 
            Submits the entry field data about the task-routine relation into the database
            Currently does NOT update the task in the GUI with this edited data. Must be loaded afterwards
        '''
        taskName = self.taskEntry.get()
        routineName = self.routineEntry.get()

        newTaskName = self.newTaskEntry.get()
        newTime = self.newTimeEntry.get()
        newDescription = self.newDescriptionEntry.get("1.0", END)
        
        query = f'UPDATE Tasks SET taskName = \"{newTaskName}\", taskTime = \"{newTime}\", taskDescription = \"{newDescription}\" WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)
        mBox.showinfo(title = "Sucess!", message= "Your task had been updated")
    

    def configRecurringTask(self):
        '''
            Form to configure a recurring task based on a 1-6 day repeateing schedule
        '''
        userTasks = self.mTask.loadUserTasks(routineName="Tasks")

        # Form Window -----------------------------------------------

        # Popup form window
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")

        # Main container to hold form widgets
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Task selection area
        ttk.Label(self.container, text = "Choose a task to configure").grid(row = 0, column = 0, padx = 10, pady = 10)
        self.taskEntry = ttk.Combobox(self.container, values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.refreshConfigRecurrence) # Update GUI for UI/UX
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Selectable frequency of recurance list creation
        self.recurFrequencies = [("Every " + str(x) + " days ") for x in range(2,7)]
        self.recurFrequencies.insert(0, "Every other day")
        self.recurFrequencies.insert(0, "Daily")

        # Frequency of recurance selection area
        ttk.Label(self.container, text = "This task shall occur: ").grid(row = 2, column = 0, padx = 10, pady = 10)
        self.daysEntry = ttk.Combobox(self.container, values = self.recurFrequencies)
        self.daysEntry.bind("<<ComboboxSelected>>", lambda e: self.container.focus()) # Remove blue background for comobox when selected
        self.daysEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Submission of recurrance action
        self.createButton = ttk.Button(self.container, text = "Create Recurrance", command = self.createRecurringTask, state = "disabled")
        self.createButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        # Removal of exsisting recurance action
        self.removeButton = ttk.Button(self.container, text = "Remove Recurrance", command = self.removeRecurrance, state = "disabled")
        self.removeButton.grid(row = 5, column = 0, padx = 10, pady = 10)
        # ~ Form Window -----------------------------------------------
    def refreshConfigRecurrence(self, event):
        '''
            Refreshes the configure recurrence form window based on the task data from the database
        '''
        taskName = self.taskEntry.get()
        self.container.focus() # Remove blue background for comobox when selected

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        recurFrequency = rec['recurFrequency']

        # Translate numerical representation back to user representation
        if recurFrequency == 1:
            recurFrequency = "Daily"
        elif recurFrequency == 2:
            recurFrequency = "Every other day"
        elif recurFrequency in [3,4,5,6]:
            recurFrequency = "Every " + str(recurFrequency) + " days "

        # If the recurance property is set in the database, then display the current value and allow removal of the action
        if recurFrequency:
            self.daysEntry.current(self.recurFrequencies.index(recurFrequency))
            self.createButton.config(text = "Alter Recurrance")
            self.removeButton.config(state = "enabled")
        # If the recurance property is not set, only allow its creation action and populate the comobox with an inital "daily" option
        else:
            self.daysEntry.current(0)
            self.createButton.config(text = "Create Recurrance")
            self.removeButton.config(state = "disabled")
        
        # Allow user to create/alter task recurance
        self.createButton.config(state = "enabled")
    def createRecurringTask(self):
        '''
            Creates or Alters the recurrance frequency of a task
            Whether altered or created, the reference date is then set to today's date
        '''
        taskName = self.taskEntry.get()
        frequency = self.daysEntry.get()

        # Translate user input into numbers for recurance computation, see recuranceAlgorithm in mTask.py
        if frequency == "Daily":
            frequency = 1
        elif frequency == "Every Other Day":
            frequency = 2
        else:
            frequency = int(frequency[6]) + 1 # Retrieve only the number from the input

        # Update the database
        refDate = datetime.today().date()
        query = f'UPDATE Tasks SET recurFrequency = \"{frequency}\", recurRefDate = \"{refDate}\" WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        self.mTask.mTaskDB.sql_do(query)

        # Show success message based on action
        if self.createButton.cget("text") == "Create Recurrance":
            mBox.showinfo(title = "Creation Success!", message= "You have created a task recurrance")
        elif self.createButton.cget("text") == "Alter Recurrance":
            mBox.showinfo(title = "Alter Success!", message= "You have altered a task recurrance")
    def removeRecurrance(self):
        '''
            Deactivates the recurance property of a task by setting both related values in the database to NULL
            Remvoval is only for tasks which have been previously configured to recur
        '''
        taskName = self.taskEntry.get()

        query = f'UPDATE Tasks SET recurFrequency = NULL, recurRefDate = NULL WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        self.mTask.mTaskDB.sql_do(query)

        self.removeButton.config(state = "disabled")
        mBox.showinfo(title = "Success!", message= "You have removed this task occurance")

    def getwindowInfo(self, event):
        '''
            Prints the current dimensions of a widget based on a binding event attachted to it
        '''
        window = event.widget
        print("x : " + str(window.winfo_width()))
        print("y : " + str(window.winfo_height()))