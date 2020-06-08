from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox
from datetime import datetime

class RoutineFunctions():
    '''
        Functions for routine menu pop-up forms and configuration
    '''
    def __init__(self, mTask):
        self.mTask = mTask # Instance of main window 

    def newRoutine(self):
        '''
            Pop-up window form for new routine creation
        '''
        userTasks = self.mTask.loadUserTasks()

        # Form Window ------------------------------------------------------
        
        # Top level pop-up window
        self.window = Toplevel(self.mTask.root)
        self.window.geometry("-2450+250")

        # Main container frame for widgets
        self.container = ttk.Frame(self.window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # New task name creation area
        ttk.Label(self.container, text = "Enter a new routine").grid(row = 0, column = 0, padx = 10, pady = 10)
        self.routineName = StringVar()
        self.routineEntry = ttk.Entry(self.container, textvariable = self.routineName)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Task addition area
        ttk.Label(self.container, text = "Select a task to add").grid(row = 2, column = 0, padx = 10, pady = 10)
        self.taskToStage = ttk.Combobox(self.container, values = userTasks, state = "readonly")
        self.taskToStage.bind("<<ComboboxSelected>>", self.refreshStagingButton)
        self.taskToStage.grid(row = 3, column = 0, padx = 10, pady = 10)
        
        # Staged tasks to be added to routine container frame
        self.stagedTasks = ttk.LabelFrame(self.container, text = self.routineName.get())
        self.stagedTasks.grid(row = 5, column = 0, padx = 10, pady = 10)

        # Action button to add a selected task to the stage
        self.stageTaskButton = ttk.Button(self.container, text = "Add task to Routine", command = self.addTaskToStage)
        self.stageTaskButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        # Routine description entry area
        ttk.Label(self.container, text = "Describe the Routine").grid(row = 6, column = 0, padx = 10, pady = 10)
        self.descriptionEntry = Text(self.container, wrap = WORD, width = 30, height = 10)
        self.descriptionEntry.grid(row = 7, column = 0, padx = 10, pady = 10)
        
        # Creation of new routine action button
        self.createButton = ttk.Button(self.container, text = "Create Routine", command = self.createNewRoutine)
        self.createButton.grid(row = 8, column = 0, padx = 10, pady = 10)

        # Refreshment of GUI for UI/UX
        self.routineEntry.bind("<KeyRelease>", self.refreshNewRoutineForm)
        self.routineEntry.focus()
        # ~ Form Window ------------------------------------------------------
    def refreshStagingButton(self, event):
        '''
            Check currently staged tasks to either enable/disable the staging tasks button
        '''
        self.container.focus() # Remove blue background for comobox when selected
        taskName = self.taskToStage.get()
        stagedTasks = [task.cget('text') for task in self.stagedTasks.winfo_children()]
        if taskName in stagedTasks:
            self.stageTaskButton.config(state = "disabled")
        elif taskName not in stagedTasks:
            self.stageTaskButton.config(state = "enabled")
    def addTaskToStage(self):
        '''
            Adds a task label into the staged tasks frame and disables stageTask button
        '''
        taskName = self.taskToStage.get()
        ttk.Label(self.stagedTasks, text = taskName).grid(row = len(self.stagedTasks.winfo_children()), column = 0, sticky = W)
        self.stageTaskButton.config(state = "disabled")
    def refreshNewRoutineForm(self, event):
        '''
            Updates widget text in new routine creation form to match entered routine name
        '''
        routineName = self.routineName.get()
        if routineName:
            self.stagedTasks.config(text = routineName + " Tasks")
            self.stageTaskButton.config(text = "Add task to " + routineName)
            self.createButton.config(text = "Create " + routineName + " Routine")
    def createNewRoutine(self):
        '''
            Asseses user input from new routine entry form. If valid, new routine is added to the GUI as well as the database
        '''
        routineName = self.routineName.get()
        routineDescription = self.descriptionEntry.get("1.0", END)
        userRoutines = self.mTask.loadUserRoutines()

        # New routine must be unqiue within database
        if routineName in userRoutines:
            mBox.showerror(title = "Routine Creation Error", message= "Please select a routine name that is has not been taken")
            return 

        stagedTasks = [task.cget('text') for task in self.stagedTasks.winfo_children()]
        tasksForGUI = [] # List of task data dictionaries in the form accepted by addRoutineToGUI function

        for taskName in stagedTasks:

            # Retrieve task data from database
            query = f'SELECT * FROM Tasks WHERE taskName = \"{taskName}\" AND routineName = \"Tasks\"'
            rec = dict(self.mTask.mTaskDB.sql_query_row(query))
            taskName = rec['taskName']
            taskTime = rec['taskTime']
            taskDescription = rec['taskDescription']

            # Update Tasks with newly created routine name
            query = f'INSERT INTO Tasks (taskName, taskTime, taskDescription, routineName) VALUES (\"{taskName}\",\"{taskTime}\", \"{taskDescription}\", \"{routineName}\")' 
            self.mTask.mTaskDB.sql_do(query)

            # Update Routines with newly created routine name and description
            query = f'INSERT INTO Routines (routineName, routineDescription) VALUES (\"{routineName}\",\"{routineDescription}\")'
            self.mTask.mTaskDB.sql_do(query)

            # Create accetpable GUI task dictionary
            tasksForGUI.append({'taskName': taskName, 'taskTime' : taskTime, 'routineName' : routineName})

        # Add new routine to GUI with its tasks
        self.mTask.addRoutineToGUI(tasks = tasksForGUI, routineName=routineName)

    def loadRoutine(self):
        '''
            Pop-up form for loading a routine into the GUI with all of its associated tasks
        '''
        userRoutines = self.mTask.loadUserRoutines()

        # Form Window ------------------------------------------------------

        # Top level pop-up window
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")

        # Main container frame for widgets
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1) # Container uses grid for children, all in column 0. Allows smooth resizeability

        # Selection of a routine area
        ttk.Label(self.container, text = "Select a Routine").grid(row = 0, column = 0, padx = 30, pady = 10)
        self.routineEntry = ttk.Combobox(self.container, values = userRoutines, state = "readonly")
        self.routineEntry.bind("<<ComboboxSelected>>", self.refreshLoadRoutine) # Remove blue background for comobox when selected
        self.routineEntry.grid(row = 1, column = 0, padx = 30, pady = 10)

        # Load action on routine 
        self.loadButton = ttk.Button(self.container, text = "Load Routine", command = self.submitLoadRoutine, state = "disabled")
        self.loadButton.grid(row = 2, column = 0, padx = 30, pady = 10)
        # ~ Form Window ------------------------------------------------------
    def refreshLoadRoutine(self, event):
        '''
            Refreshes the load routine form for functionality
        '''
        routineName = self.routineEntry.get()
        if routineName:
            self.loadButton.config(state = "enabled")
        else:
            self.loadButton.config(state = "disabled")
        self.container.focus()
    def submitLoadRoutine(self):
        '''
           Evalutes user input and updates the GUI with the loaded routine.
        '''
        routineName = self.routineEntry.get()
        self.mTask.loadSpecificRoutine(routineName=routineName)
    
    def editRoutine(self):
        '''
            Form which allows routine properties to change, as well as to add/remove tasks that are associated with a particular routine
        '''
        userRoutines = self.mTask.loadUserRoutines()
        userRoutines.remove("Tasks") # Disable editing for default task-routine relation

        # Form Window ------------------------------------------------------

        # Top level pop-up window
        self.window = Toplevel(self.mTask.root)
        self.window.geometry("-2450+250") 
        self.container = ttk.Frame(self.window)

        # Main container for widgets
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1) # Container uses grid for children. Allows smooth resizeability in column 0
        self.container.columnconfigure(1, weight = 1) # Container uses grid for children. Allows smooth resizeability in column 1

        # Selection of routine entry area
        ttk.Label(self.container, text = "Select a Routine").grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
        self.routineEntry = ttk.Combobox(self.container, values = userRoutines, state = "readonly")
        self.routineEntry.bind("<<ComboboxSelected>>", self.showEditableData)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10, columnspan = 2)

        # New routine entry field area
        ttk.Label(self.container, text = "Enter a new Routine Name").grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)
        self.newRoutineEntry = ttk.Entry(self.container)
        self.newRoutineEntry.grid(row = 3, column = 0, padx = 10, pady = 10, columnspan = 2)


        # Addition of Tasks Area ---------------------------------------------------------------------
        # Tasks to add to routine selection field area
        ttk.Label(self.container, text = "Select a Task to Add").grid(row = 4, column = 0, padx = 10, pady = 10)
        self.addableTasks = ttk.Combobox(self.container, state = "readonly")
        self.addableTasks.bind("<<ComboboxSelected>>", self.refreshAddStageButton)
        self.addableTasks.grid(row = 5 , column = 0, padx = 10)
        
        # Action to add task to add stage 
        self.stageAddTask = ttk.Button(self.container, text = "Add Task", command = self.addToAddStage)
        self.stageAddTask.grid(row = 6, column = 0, padx = 10, pady = 5 )

        # Added tasks staging area
        self.addTaskStage = ttk.LabelFrame(self.container, text = " Tasks to Add ")
        self.addTaskStage.grid(row = 7, column = 0)
        # ~ Addition of Tasks Area --------------------------------------------------------------------


        # Removal of Tasks Area -----------------------------------------------------------------------
        # Tasks to remove from routine selection field area
        ttk.Label(self.container, text = "Select a Task to Remove").grid(row = 4, column = 1, padx = 10, pady = 10)
        self.removableTasks = ttk.Combobox(self.container, state = "readonly")
        self.removableTasks.bind("<<ComboboxSelected>>", self.refreshRemoveStageButton)
        self.removableTasks.grid(row = 5 , column = 1, padx = 10)

        # Removed tasks staging area
        self.stageRemoveTask = ttk.Button(self.container, text = "Add Task", command = self.addToRemoveStage)
        self.stageRemoveTask.grid(row = 6, column = 1, padx = 10, pady = 5)
        
        # Action to add a task to the removal stage
        self.removeTaskStage = ttk.LabelFrame(self.container, text = " Tasks to Remove ")
        self.removeTaskStage.grid(row = 7, column = 1)
        # ~ Removal of Tasks Area -----------------------------------------------------------------------


        # New description entry field area
        ttk.Label(self.container, text = "Edit the Routine Description").grid(row = 8, column = 0, columnspan = 2, padx = 10, pady = 10)
        self.newDescriptionEntry = Text(self.container, wrap = WORD, width = 30, height = 10)
        self.newDescriptionEntry.grid(row = 9, column = 0, columnspan = 2, pady = 5, padx = 10)

        # Clear tasks action
        self.clearButton = ttk.Button(self.container, text = "Clear Tasks", command = self.clearEditRoutine)
        self.clearButton.grid(row = 10, column = 0, columnspan = 2, pady = 20)

        # Submission of edited content action
        self.editButton = ttk.Button(self.container, text = "Edit", command = self.submitEditRoutine)
        self.editButton.grid(row = 11, column = 0, columnspan = 2, pady = 20)
        # ~ Form Window ------------------------------------------------------
    def refreshAddStageButton(self, event):
        '''
            Refresh the button to either enable/disable its action based on the stage below it
        '''
        self.container.focus() # Remove blue background for comobox when selected
        taskName = self.addableTasks.get()
        stagedAddTasks = [task.cget('text') for task in self.addTaskStage.winfo_children()]
        if taskName in stagedAddTasks:
            self.stageAddTask.config(state = "disable")
        if taskName not in stagedAddTasks:
            self.stageAddTask.config(state = "enabled")
    def refreshRemoveStageButton(self, event):
        '''
            Refresh the button to either enable/disable its action based on the stage below it
        '''
        self.container.focus() # Remove blue background for comobox when selected
        taskName = self.removableTasks.get()
        stagedRemoveTasks = [task.cget('text') for task in self.removeTaskStage.winfo_children()]
        if taskName in stagedRemoveTasks:
            self.stageRemoveTask.config(state = "disable")
        if taskName not in stagedRemoveTasks:
            self.stageRemoveTask.config(state = "enabled")
    def showEditableData(self, event):
        '''
            Fills entry widgets with current values of routine data based on the database
        '''
        self.container.focus() # Remove blue background for comobox when selected
        routineName = self.routineEntry.get()

        # Selectable comobox values based on current state of database
        removableTasks = self.mTask.loadUserTasks(routineName=routineName) # Every task that is apart of the rouine
        addableTasks = self.mTask.loadUserTasks(routineName="All") # Every task that is not apart of the routine
        for task in removableTasks:
            addableTasks.remove(task)
        self.addableTasks.config(values = addableTasks)
        self.removableTasks.config(values = removableTasks)

        # Routine name and description entries from database
        query = f'SELECT * FROM Routines WHERE routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        self.newRoutineEntry.delete(0, END)
        self.newDescriptionEntry.delete("1.0", END)
        self.newRoutineEntry.insert(0, routineName)
        self.newDescriptionEntry.insert("1.0", rec['routineDescription'])
    def addToRemoveStage(self):
        '''
            Adds the selected task from the task combobox to the removed tasks stage
        '''
        taskName = self.removableTasks.get()
        if not taskName:
            return
        ttk.Label(self.removeTaskStage, text = taskName).grid(row = len(self.removeTaskStage.winfo_children()), column = 0, sticky = W)
        self.stageRemoveTask.config(state = "disable")
    def addToAddStage(self):
        '''
            Adds the selected task from the task combobox to the added tasks stage
        '''
        taskName = self.addableTasks.get()
        if not taskName:
            return
        ttk.Label(self.addTaskStage, text = taskName).grid(row = len(self.addTaskStage.winfo_children()), column = 0, sticky = W)
        self.stageAddTask.config(state = "disable")
    def clearEditRoutine(self):
        '''
            Removes all tasks from the add and remove task stages 
        '''
        for child in self.addTaskStage.winfo_children():
            child.destroy()

        for child in self.removeTaskStage.winfo_children():
            child.destroy()

        self.stageRemoveTask.config(state = "enabled")
        self.stageAddTask.config(staet = "enabled")
    def submitEditRoutine(self):
        '''
            Evalutates the edited data and submits the data to the database. Routine is NOT updated in the GUI after this change
        '''
        oldRoutineName = self.routineEntry.get()
        newRoutineName = self.newRoutineEntry.get()
        routineDescription = self.newDescriptionEntry.get("1.0", END)
        
        # Update routine description
        query = f'UPDATE Routines SET routineDescription = \"{routineDescription}\" WHERE routineName = \"{oldRoutineName}\"'
        self.mTask.mTaskDB.sql_do(query)

        # Update the routine name if changed
        if oldRoutineName != newRoutineName:
            query = f'UPDATE Tasks SET routineName = \"{newRoutineName}\" WHERE routineName = \"{oldRoutineName}\"'
            self.mTask.mTaskDB.sql_do(query)

            query = f'UPDATE Routines SET routineName = \"{newRoutineName}\" WHERE routineName = \"{oldRoutineName}\"'
            self.mTask.mTaskDB.sql_do(query)
        
        # Get staged tasks from their stages
        tasksToAdd = [task.cget("text") for task in self.addTaskStage.winfo_children()]
        tasksToRemove = [task.cget("text") for task in self.removeTaskStage.winfo_children()]
        
        # Add the added stage tasks to routine
        for taskName in tasksToAdd:
            query = f'UPDATE Tasks SET routineName = \"{newRoutineName}\" WHERE taskName = \"{taskName}\"'
            self.mTask.mTaskDB.sql_do(query)

        # Remove the removed stage tasks from routine
        for taskName in tasksToRemove:
            query = f'UPDATE Tasks SET routineName = \"Tasks\" WHERE taskName = \"{taskName}\"'
            self.mTask.mTaskDB.sql_do(query)
        
        mBox.showinfo(title = "Success!", message="Your routine has been successfully updated!")

    def configRecurringRoutine(self):
        '''
            Form to configure a recurring routine
        '''
        userRoutines = self.mTask.loadUserRoutines()

        # Form window ---------------------------------------------

        # Top level pop-up window
        window = Toplevel(self.mTask.root)
        window.geometry("-2450+250")

        # Main container frame for form widgets
        self.container = ttk.Frame(window)
        self.container.pack(expand = True, fill = "both")
        self.container.columnconfigure(0, weight = 1)

        # Selection of routine entry field
        ttk.Label(self.container, text = "Choose a Routine to configure").grid(row = 0, column = 0, padx = 10, pady = 10)
        self.routineEntry = ttk.Combobox(self.container, values = userRoutines)
        self.routineEntry.bind("<<ComboboxSelected>>", self.showConfigData)
        self.routineEntry.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Creation of frequency values field
        ttk.Label(self.container, text = "This routine shall occur: ").grid(row = 2, column = 0, padx = 10, pady = 10)

        self.recurFrequencies = [("Every " + str(x) + " days ") for x in range(2,7)]
        self.recurFrequencies.insert(0, "Every other day")
        self.recurFrequencies.insert(0, "Daily")

        # Frequency of recurrance selection field
        self.daysEntry = ttk.Combobox(self.container, values = self.recurFrequencies)
        self.daysEntry.grid(row = 3, column = 0, padx = 10, pady = 10)

        # Submission of new/altered recurrance
        self.submitButton = ttk.Button(self.container, text = "Create Reccurance", command = self.submiteRecurringRoutine)
        self.submitButton.grid(row = 4, column = 0, padx = 10, pady = 10)

        # Revmoval of reucrrance property
        self.removeButton = ttk.Button(self.container, text = "Remove reccurance", command = self.removeReccurance, state = "disabled")
        self.removeButton.grid(row = 5, column = 0, padx = 10, pady = 10)
        # ~ Form window ---------------------------------------------
    def showConfigData(self, event):
        '''
            Show the currently configured recurrance from the database. 
            If there is data, allow altering/removal. If not, only creation is allowed
        '''
        routineName = self.routineEntry.get()
        self.container.focus() # Remove blue background for comobox when selected

        # Get recurrance data from database
        query = f'SELECT * FROM Routines WHERE routineName = \"{routineName}\"'
        rec = dict(self.mTask.mTaskDB.sql_query_row(query))
        recurFrequency = rec['recurFrequency']

        # Translate numerical representation back to user representation
        if recurFrequency == 1:
            recurFrequency = "Daily"
        elif recurFrequency == 2:
            recurFrequency = "Every other day"
        elif recurFrequency in [3,4,5,6]:
            recurFrequency = "Every " + str(recurFrequency) + " days "
            
        # If there is data, allow altering/removal
        if recurFrequency:
            self.daysEntry.current(self.recurFrequencies.index(recurFrequency))
            self.submitButton.config(text = "Alter Reccurance")
            self.removeButton.config(state = "enabled")
        # If no data, only allow creation of recurrance
        else:
            self.daysEntry.current(0)
            self.submitButton.config(text = "Create Reccurance")
            self.removeButton.config(state = "disabled")
    def submiteRecurringRoutine(self):
        '''
            Evalute user input in reucurrance form to either alter/create routine recurrance
        '''
        routineName = self.routineEntry.get()
        frequency = self.daysEntry.get()
        
        # Translate words to numerical representation for computation of recurrance
        if frequency == "Daily":
            frequency = 1
        elif frequency == "Every Other Day":
            frequency = 2
        else:
            frequency = int(frequency[6]) + 1 # Retrieve only the number
        
        # Create new reference data and update database
        refDate = datetime.today().date()
        query = f'UPDATE Routines SET recurFrequency = \"{frequency}\", recurRefDate = \"{refDate}\" WHERE routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)

        # Show message based on action
        if self.submitButton.cget("text") == "Create Reccurance":
            mBox.showinfo(title = "Creation Success!", message= "You have created a routine reccurance")
        elif self.submitButton.cget("text") == "Alter Reccurance":
            mBox.showinfo(title = "Alter Success!", message= "You have altered a routine reccurance")
    def removeReccurance(self):
        '''
            Remove a previously created recurrance from database
        '''
        routineName = self.routineEntry.get()

        query = f'UPDATE Routines SET recurFrequency = NULL, recurRefDate = NULL WHERE routineName = \"{routineName}\"'
        self.mTask.mTaskDB.sql_do(query)
        
        mBox.showinfo(title = "Success!", message= "You have removed this routine occurance")    
        
    def getwindowInfo(self, event):
        window = event.widget
        print("x : " + str(window.winfo_width()))
        print("y : " + str(window.winfo_height()))

