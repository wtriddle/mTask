from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox
from datetime import datetime

class TaskFunctions():
    """Contains menu functions for the tasks sub-menu. Includes the functionality for each pop-up form.

        Attributes:
            mTask (inst) : Top level mTask instance
    """
    def __init__(self, mTask):
        self.mTask = mTask 

    def newTask(self):
        """Pop-up form for new task creation."""

        # New pop-up window creation
        win = Toplevel(self.mTask.root)
        win.title('Create a New Task')
        win.geometry("-2450+250")
        win.bind("<KeyRelease>", self.refreshNewTask) # Refresh GUI for UI/UX 

        # Main container to hold form widgets
        container = ttk.Frame(win)
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
        self.submitButton = ttk.Button(container, text = "Create", command = self.submitNewTask, state = "disabled")
        self.submitButton.grid(row = 6, column = 0, pady = 20, padx = 10)

        # Allow instant typing into new task name input field when window is created
        self.taskEntry.focus()
        
    def refreshNewTask(self, event):
        """Enable/Disable submission button based on inputs of task entry fields."""

        taskName = self.taskEntry.get()
        taskTime = self.timeEntry.get()

        # Submission can only occur when a task name and time are specified
        if taskName and taskTime:
            self.submitButton.config(state = "enabled")
        else:
            self.submitButton.config(state = "disabled")

    def submitNewTask(self):
        """Transfer entry field data into the Tasks table and append the task to the Tasks tab."""

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
        """Pop-up form for loading a task into a specific routine tab currently in the GUI."""

        userTasks = self.mTask.loadUserTasks()

        # Only currently loaded routines can recieve a loaded task
        userRoutines = [str(self.mTask.nb.tab(i, option = "text")) for i in range(len(self.mTask.nb.winfo_children()))]

        # New pop-up window creation
        win = Toplevel(self.mTask.root)
        win.geometry("-2450+250")

        # Main container frame for all form widgets
        container = ttk.Frame(win)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Selection of a task input area
        ttk.Label(container, text = "Choose a Task").grid(row = 0, column = 0, pady = 10, padx = 10)
        self.taskEntry = ttk.Combobox(container, state = "readonly", values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.refreshLoadTask) # Refresh GUI for UI/UX 
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Selection of a routine tab input area
        ttk.Label(container, text = "Choose a Routine").grid(row = 2, column = 0, pady = 10, padx = 10)
        self.routineEntry = ttk.Combobox(container, state = "readonly",values = userRoutines)
        self.routineEntry.bind("<<ComboboxSelected>>", self.refreshLoadTask) # Refresh GUI for UI/UX 
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Action button for loading a task
        self.submitButton = ttk.Button(container, text = "Load", command = self.submitLoadTaskData, state = "disabled")
        self.submitButton.grid(row = 4, column = 0, pady = 20, padx = 10)

    def refreshLoadTask(self, event):
        """Enable/Disable submission button based on data entry fields."""

        taskName = self.taskEntry.get()
        routineName = self.routineEntry.get()

        # Task can only be loaded if both a task name and routine tab are specified
        if taskName and routineName:
            self.submitButton.config(state = "enabled")
        else:
            self.submitButton.config(state = "disabled")

        event.widget.master.focus() # Remove blue background for comobox when selected

    def submitLoadTaskData(self):
        """Load specific task-routine data into the routine tab specified. Description defaults to Tasks table description for task."""

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
        """Form to edit the task name, time, and description for a specific routine."""

        userTasks = self.mTask.loadUserTasks()

        # Popup window creation
        win = Toplevel(self.mTask.root)
        win.geometry("-2450+250")
        
        # Main container for form widgets
        container = ttk.Frame(win)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Selection of task input area
        ttk.Label(container, text = "Choose a Task to Change").grid(row = 0, column = 0, pady = 10, padx = 10)
        self.taskEntry = ttk.Combobox(container, state = "readonly", values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.showEditableRoutines)
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Selection of routine input area
        ttk.Label(container, text = "Choose the routine to alter it from").grid(row = 2, column = 0, pady = 10, padx = 10)
        self.routineEntry = ttk.Combobox(container, state = "disabled")
        self.routineEntry.bind("<<ComboboxSelected>>", self.showEditableData)
        self.routineEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Edit task name input area
        ttk.Label(container, text = "Enter a new Task Name").grid(row = 4, column = 0, pady = 10, padx = 10)
        self.newTaskEntry = ttk.Entry(container, state = "disabled")
        self.newTaskEntry.grid(row = 5, column = 0, padx = 10, pady = 10)

        # Edit task time input area
        ttk.Label(container, text = "Enter a new Task Start Time").grid(row = 6, column = 0, pady = 10, padx = 10)
        self.newTimeEntry = ttk.Entry(container, state = "disabled")
        self.newTimeEntry.grid(row = 7, column = 0, padx = 10, pady = 10)

        # Edit task description area
        ttk.Label(container, text = "Change the Description").grid(row = 8, column = 0, pady = 10, padx = 10)
        self.newDescriptionEntry = Text(container, wrap = WORD, state = "disabled", height = 10, width = 30)
        self.newDescriptionEntry.grid(row = 9, column = 0, padx = 10, pady = 10)

        # Submission of edited content action
        self.submitButton = ttk.Button(container, text = "Edit", command = self.submitEditTaskData)
        self.submitButton.grid(row = 10, column = 0, pady = 20, padx = 10)

    def showEditableRoutines(self, event):
        """Show all task-routine relations in the routineEntry combobox for a given task selection."""

        taskName = self.taskEntry.get()

        query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\"'
        recs = list(self.mTask.mTaskDB.sql_query(query))
        userRoutines = [rec['routineName'] for rec in recs]

        self.routineEntry.config(values = userRoutines, state = "readonly")

        event.widget.master.focus() # Remove blue background for task comobox when selected

    def showEditableData(self,event):
        """Fill the task editing fields with the current data from the database about the selected task-routine relation."""
        
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

        event.widget.master.focus() # Remove blue background for task comobox when selected

    def submitEditTaskData(self):
        """Update the specific task-routine task data based on the edit form entry fields."""

        taskName = self.taskEntry.get()
        routineName = self.routineEntry.get()

        newTaskName = self.newTaskEntry.get()
        newTime = self.newTimeEntry.get()
        newDescription = self.newDescriptionEntry.get("1.0", END)
        
        query = f'UPDATE Tasks SET taskName = \"{newTaskName}\", taskTime = \"{newTime}\", taskDescription = \"{newDescription}\" WHERE taskName = \"{taskName}\" AND routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)
        mBox.showinfo(title = "Sucess!", message= "Your task had been updated")

    def configRecurringTask(self):
        """Form to configure a recurring task based on a 1-6 day repeateing schedule"""

        userTasks = self.mTask.loadUserTasks(routineName="Tasks")

        # Popup form window
        win = Toplevel(self.mTask.root)
        win.geometry("-2450+250")

        # Main container to hold form widgets
        container = ttk.Frame(win)
        container.pack(expand = True, fill = "both")
        container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Task selection area
        ttk.Label(container, text = "Choose a task to configure").grid(row = 0, column = 0, padx = 10, pady = 10)
        self.taskEntry = ttk.Combobox(container, values = userTasks)
        self.taskEntry.bind("<<ComboboxSelected>>", self.refreshConfigRecurrence) # Update GUI for UI/UX
        self.taskEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Selectable frequency of recurance list creation
        self.recurFrequencies = [("Every " + str(x) + " days ") for x in range(2,7)]
        self.recurFrequencies.insert(0, "Every other day")
        self.recurFrequencies.insert(0, "Daily")

        # Frequency of recurance selection area
        ttk.Label(container, text = "This task shall occur: ").grid(row = 2, column = 0, padx = 10, pady = 10)
        self.daysEntry = ttk.Combobox(container, values = self.recurFrequencies)
        self.daysEntry.bind("<<ComboboxSelected>>", lambda e: container.focus()) # Remove blue background for comobox when selected
        self.daysEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Submission of recurrance action
        self.createButton = ttk.Button(container, text = "Create Recurrance", command = self.createRecurringTask, state = "disabled")
        self.createButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        # Removal of exsisting recurance action
        self.removeButton = ttk.Button(container, text = "Remove Recurrance", command = self.removeRecurrance, state = "disabled")
        self.removeButton.grid(row = 5, column = 0, padx = 10, pady = 10)

    def refreshConfigRecurrence(self, event):
        """Refresh the configure recurrence form window based on the task data from the database"""

        taskName = self.taskEntry.get()
        event.widget.master.focus() # Remove blue background for comobox when selected

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
        """Create or Alter the recurrance frequency of a task."""

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
        """Deactivate the recurrance property of a task by setting both related values in the database to NULL."""

        taskName = self.taskEntry.get()

        query = f'UPDATE Tasks SET recurFrequency = NULL, recurRefDate = NULL WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
        self.mTask.mTaskDB.sql_do(query)

        self.removeButton.config(state = "disabled")
        mBox.showinfo(title = "Success!", message= "You have removed this task occurance")

    def getwindowInfo(self, event):
        """
            Prints the current dimensions of a widget based on a binding event attachted to it
        """
        window = event.widget
        print("x : " + str(window.winfo_width()))
        print("y : " + str(window.winfo_height()))