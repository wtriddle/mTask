from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox

from bwDB import bwDB
from taskFunctions import TaskFunctions
from routineFunctions import RoutineFunctions
from helpFunctions import HelpFunctions
import descriptor

from threading import Thread
from queue import Queue
import time
import datetime

class mTask():
    '''
        Central class for GUI layout, updates, and initalizations.
        Includes common database functionality
    '''

    def __init__(self):
        
        # Root, Database, and Menu Init -----------------------------------------------------------------------
        self.root = Tk()                                                # Top level window
        self.root.title('mTask')                                        # Assign a title
        self.root.geometry("-2650+150")                                 # Temporary geometry configuration
        self.root.iconbitmap("mTask.ico")                               # mTask icon config

        self.initDB()                                                   # Initalize user database

        self.taskFunctions = TaskFunctions(self)                        # Initalize task menu functionality
        self.routineFunctions = RoutineFunctions(self)                  # Initalize routine menu functionality
        self.helpFunctions = HelpFunctions(self)                        # Initalize help menu functionality
        self.initMenu(self.taskFunctions,                               # Create menu with functionality
                    self.routineFunctions, 
                    self.helpFunctions
                    ) 
        # ~ Root, Database, and Menu Init --------------------------------------------------------------------

        # Tab Control Init -----------------------------------------------------------------------------------
        self.tabControl = ttk.Notebook(self.root)                       # Top level notebook 
        self.tabControl.pack(padx=10,pady=10, ipadx = 100, ipady = 100)                           # Pack into GUI
        self.initTabs()                                                 # Initialize the GUI with recurring tasks/routines
        # ~ Tab Control --------------------------------------------------------------------------------------

        # Styles ---------------------------------------------------------------------------------------------
        self.style = ttk.Style(self.root)
        self.style.configure("TButton", background = "#1b262c", foreground = "#0f4c75", relief = "RIDGE", font = 8)
        self.style.configure("TFrame", background = "#0f4c75", foreground = "#1b262c", font = 8)
        self.style.configure("TLabel", background = "#0f4c75", foreground = "#acdbdf", font = 8)
        self.style.configure("TLabelframe", background = "#0f4c75", foreground = "green", font = 8)
        self.root.option_add("*TEntry.font", 10)
        self.root.option_add("*TCombobox*Listbox.font", 10)
        self.root.option_add("*TCombobox.font", 10)
        self.root.option_add("*TCombobox.background", "green")
        self.root.option_add("*TCombobox*Listbox.background", "#1f4287")
        self.root.option_add("*TCombobox*Listbox.foreground", "#00d5ff")
        # ~ Styles -------------------------------------------------------------------------------------------

    def addTaskToGUI(self, taskName, taskTime, routineName):
        '''
            Appends a taskName and taskTime as labels to the specified routineName tab inside the Incomplete Tasks frame.
            Adds a completion button for the task which activates the completionOfTask function.
            Increases the progressBar maximum by 1.
        '''
        # Loop through exsisting tabs to find correct routine tab
        for i, tab in enumerate(self.tabControl.winfo_children()):

            tabTitle = str(self.tabControl.tab(i, option = "text"))
            
            if tabTitle == routineName:
                
                # Widgets associtated with routine tab
                toDoTaskFrame = tab.winfo_children()[0]
                progressFrame = tab.winfo_children()[2]
                progressBar = progressFrame.winfo_children()[0]

                # Present an Error if task is already inside of GUI
                loadedTasks = [child.cget("text") for child in toDoTaskFrame.winfo_children()]
                if taskName in loadedTasks:
                    mBox.showerror(title = "Task Insertion Error", message= "Please enter a task that is not loaded into the " + routineName + " tab")
                    return 

                # Update the toDoTaskFrame with new task information
                numTasks = int(len(toDoTaskFrame.winfo_children()) / 3) # 3 widgets per row
                button = ttk.Button(toDoTaskFrame, text = "Complete " + taskName)
                button.grid(row = numTasks, column = 0 , padx = 15, pady = 15)
                button.bind("<Button-1>", self.completionOfTask) 
                ttk.Label(toDoTaskFrame, text = str(taskTime)).grid(row = numTasks, column = 1 , padx = 15, pady = 15)
                self.taskNameLabel = ttk.Label(toDoTaskFrame, text = str(taskName))
                self.taskNameLabel.grid(row = numTasks, column = 2 , padx = 15, pady = 15)
                
                # Increment maximum on progressbar 
                currentMax = progressBar.cget("maximum") + 0.0
                progressBar.configure(maximum = currentMax + 1.0)

                # Set the focus to the tab where the task was added to
                self.tabControl.select(tab)

                # Add descriptor to label. Load default Tasks description if routine-task specific rec doesn't exist
                query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\" AND taskName = \"{taskName}\"'
                rec = self.mTaskDB.sql_query_row(query)
                if not rec:
                    query = f'SELECT * FROM Tasks WHERE routineName = \"Tasks\" AND taskName = \"{taskName}\"'
                    rec = self.mTaskDB.sql_query_row(query)
                rec = dict(rec)
                taskDescription = rec['taskDescription']
                descriptor.createDescriptor(self.taskNameLabel, taskDescription)
  
    def addRoutineToGUI(self, tasks =  [], routineName = ""):
        '''
            Adds new tab to root window with label frames and a progress bar.
            tasks argument is a list of dictionaries with the data about each task
            each dictionary is unpacked using the addTaskToGUI function
            Every dictionary must have the same routineName as the argument given.
        '''

        self.routineTab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.routineTab, text = routineName)

        self.toDoTaskFrame = ttk.LabelFrame(self.routineTab, text = " Incomplete Tasks ")
        self.completedTaskFrame = ttk.LabelFrame(self.routineTab, text = " Completed Tasks ")
        self.progressFrame = ttk.LabelFrame(self.routineTab, text = " Progress ")
        self.progressBar = ttk.Progressbar(self.progressFrame, mode = "determinate", maximum = 0.0)

        self.toDoTaskFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        self.toDoTaskFrame.columnconfigure(0, weight = 1)
        self.toDoTaskFrame.columnconfigure(1, weight = 1)
        self.toDoTaskFrame.columnconfigure(2, weight = 1)
        self.completedTaskFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        self.completedTaskFrame.columnconfigure(0, weight = 1)
        self.completedTaskFrame.columnconfigure(1, weight = 1)
        self.progressFrame.pack(fill = "both", padx = 10, pady = 10)
        self.progressBar.pack(fill = "both", expand = True, padx = 10, pady = 10)

        ttk.Label(self.toDoTaskFrame, text = "Complete Task").grid(row = 0, column = 0 , padx = 15, pady = 15, sticky = NS)
        ttk.Label(self.toDoTaskFrame, text = "Time").grid(row = 0, column = 1 , padx = 15, pady = 15, sticky = NS)
        ttk.Label(self.toDoTaskFrame, text = "Task").grid(row = 0, column = 2 , padx = 15, pady = 15, sticky = NS)

        if tasks:
            for task in tasks:
                if routineName != task['routineName']:
                    raise Exception("All tasks must have the same routineName property")
                self.addTaskToGUI(**task)
        
        ttk.Label(self.completedTaskFrame, text = "Completed Tasks").grid(row = 0, column = 0 , padx = 15, pady = 15)
        ttk.Label(self.completedTaskFrame, text = "Completion Time").grid(row = 0, column = 1 , padx = 15, pady = 15)

        self.tabControl.select(self.routineTab)
 
    def completionOfTask(self, event):
        '''
            Removes the row of the completed task from the in-complete window,
            Adds the task to the completed window with a timestamp of completion,
            and increments the routine progress bar in a new thread
        '''

        # Widgets 
        button = event.widget
        toDoTaskFrame = button.master
        tab = toDoTaskFrame.master
        completedFrame = tab.winfo_children()[1]
        progressFrame = tab.winfo_children()[2]
        progressBar = progressFrame.winfo_children()[0]

        # Update the in-completed task frame
        completedRow = button.grid_info()['row']
        taskName = str(button.cget('text')[9:len(button.cget('text'))]) # Remove the string "completed " from button text
        
        for task in toDoTaskFrame.winfo_children():
            currentRow = task.grid_info()['row']
            
            # Destroy completed task from in-complete window
            if currentRow == completedRow: 
                task.destroy()
            
            # Shift all task widgets below the completed row up by one to refactor the GUI
            elif currentRow > completedRow:
                task.grid_configure(row = currentRow - 1)

        # Update the completed task frame
        numCompletedTasks = int(len(completedFrame.winfo_children()) / 2) # 2 widgets per completed task
        ttk.Label(completedFrame, text = taskName).grid(row = numCompletedTasks, column = 0, padx = 15, pady = 15)
        t = time.localtime()
        current_time = time.strftime("%I:%M %p", t) # Completed time in 12-hour am/pm format
        ttk.Label(completedFrame, text = current_time).grid(row = numCompletedTasks, column = 1, padx = 15, pady = 15)

        # Update the progress bar in a new thread
        runT = Thread(target = lambda : self.updateProgressBar(progressBar), daemon= True)
        runT.start()

    def updateProgressBar(self, progressBar):
        '''
            Threaded loop to make progress smoothly fill, for about 1 second
        '''
        i = 0 
        while i <= 100:
            progressBar.step(0.01)
            if progressBar.cget("value") > progressBar.cget("maximum") - 0.01:
                mBox.showinfo(title="Success", message="You did it! Congrats you finsihed a routine!")
                return
            time.sleep(0.01)
            i+=1

    def initDB(self):
        '''
            Initalizes the database for mTask in the file mTaskDB.db and creates the mTaskDB object
        '''

        self.mTaskDB = bwDB(filename = "mTaskDB.db")

        self.mTaskDB.sql_do('''
            CREATE TABLE IF NOT EXISTS Tasks(
                id INTEGER PRIMARY KEY,
                taskName TEXT,
                taskTime TEXT,
                taskDescription TEXT,
                routineName TEXT DEFAULT \"Tasks\" NOT NULL,
                recurFrequency INTEGER DEFAULT NULL,
                recurRefDate TEXT DEFAULT NULL,
                CONSTRAINT task_info UNIQUE(taskName, routineName)
            );
        ''')

        self.mTaskDB.sql_do('''
            CREATE TABLE IF NOT EXISTS Routines(
                routineName TEXT PRIMARY KEY,
                routineDescription TEXT,
                recurFrequency INTEGER DEFAULT NULL,
                recurRefDate TEXT DEFAULT NULL
            );
        ''')
        self.mTaskDB.set_table("Routines")
        if self.mTaskDB.countrecs() == 0:
            query = f'INSERT INTO Routines (routineName, routineDescription) VALUES (\"Tasks\", \"DEFAULT\")'
            self.mTaskDB.sql_do(query)

    def initMenu(self, taskFunctions, routineFunctions, helpFunctions):
        '''
            Initializes the menu of mTask with functionality from classes
        '''
        self.menubar = Menu(self.root)
        self.root.config(menu = self.menubar)

        self.taskMenu = Menu(self.menubar, tearoff = 0)
        self.taskMenu.add_command(label = "New Task", command = taskFunctions.newTask)
        self.taskMenu.add_command(label = "Edit Task", command = taskFunctions.editTask)
        self.taskMenu.add_command(label = "Load Task", command = taskFunctions.loadTask)
        self.taskMenu.add_separator()
        self.taskMenu.add_command(label = "Configure Recurring Task", command = taskFunctions.configRecurringTask)
        self.menubar.add_cascade(menu = self.taskMenu, label = "Tasks")

        self.routinesMenu = Menu(self.menubar, tearoff = 0)
        self.routinesMenu.add_command(label = "New Rouine", command = routineFunctions.newRoutine)
        self.routinesMenu.add_command(label = "Edit Rouine", command = routineFunctions.editRoutine)
        self.routinesMenu.add_command(label = "Load Rouine", command = routineFunctions.loadRoutine)
        self.routinesMenu.add_separator()
        self.routinesMenu.add_command(label = "Configure Recurring Routine", command = routineFunctions.configRecurringRoutine)
        self.menubar.add_cascade(menu = self.routinesMenu, label = "Rouines")

        self.helpMenu = Menu(self.menubar, tearoff = 0)
        self.helpMenu.add_command(label = "Guide", command = helpFunctions.showGuide)
        self.helpMenu.add_command(label = "Info", command = helpFunctions.showInfo)
        self.menubar.add_cascade(menu = self.helpMenu, label = "Help")

    def loadUserTasks(self, routineName = "All"):
        '''
            Returns a list of all user tasks inside of the Tasks table associated with the input routineName
            If no routineName is given, then all tasks from the database will be returned in the list
        '''
        self.mTaskDB.set_table(tablename = "Tasks")

        if routineName == "All":
            recs = list(self.mTaskDB.getrecs())
        else:
            userRoutines = self.loadUserRoutines()
            if routineName not in userRoutines:
                raise Exception("Routine name does not exist in the database, cannot load tasks")
            query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\"'
            recs = list(self.mTaskDB.sql_query(query))

        userTasks = []
        if recs:
            userTasks = [rec['taskName'] for rec in recs]
            userTasks = list(dict.fromkeys(userTasks))
        return userTasks
    
    def loadUserRoutines(self):
        '''
            Returns a list of all user routines inside of the Routines table from the database
        '''
        self.mTaskDB.set_table(tablename = "Routines")
        recs = list(self.mTaskDB.getrecs())
        userRoutines = []
        if recs:
            userRoutines = [rec['routineName'] for rec in recs]
            userRoutines = list(dict.fromkeys(userRoutines))
        return userRoutines
    
    def loadSpecificRoutine(self, routineName):
        '''
            Load a routine directly into the GUI with its tasks into a new tab, where only the routineName is required
        '''
        routineTasks = []
        query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\"'
        tasks = list(self.mTaskDB.sql_query(query))
        for task in tasks:
            routineTasks.append({'taskName': task['taskName'], 'taskTime' : task['taskTime'], 'routineName' : routineName})
        self.addRoutineToGUI(routineName=routineName, tasks=routineTasks)

    def initTabs(self):
        '''
            Initalizes the tabs based on recurrant properties of tasks and routines set by the user
        '''

        # Tasks Tab Init ---------------------------------------------
        recurringTasks = [] # Loads tasks with a recuring property
        self.mTaskDB.set_table("Tasks")
        recs = self.mTaskDB.getrecs()
        for rec in recs:
            if rec['recurRefDate']:
                recurringTasks.append(rec)
        
        if recurringTasks:
            todaysTasks = self.recurantAlgorithm(recurringTasks) # Determine what tasks should be auto-loaded
            tasksToAdd = []
            for task in todaysTasks:
                tasksToAdd.append({'taskName': task['taskName'], 'taskTime' : task['taskTime'], 'routineName' : "Tasks"})
            self.addRoutineToGUI(routineName= "Tasks", tasks=tasksToAdd)
        else:
            self.addRoutineToGUI(routineName= "Tasks")
        # ~ Tasks Tab Init ---------------------------------------------

        # Routine Tab Init --------------------------------------------
        recurringRoutines = [] # Loads routines with a recuring property
        self.mTaskDB.set_table("Routines")
        recs = self.mTaskDB.getrecs()
        for rec in recs:
            if rec['recurRefDate']:
                recurringRoutines.append(rec)
        
        if recurringRoutines:
            todaysRoutines = self.recurantAlgorithm(recurringRoutines) # Determine what routines should be auto loaded
            for routine in todaysRoutines:
                self.loadSpecificRoutine(routineName=routine['routineName'])
        # ~ Routine Tab Init ------------------------------------------
    def recurantAlgorithm(self, R):
        '''
            Determines what routines or tasks should be automatically loaded into the GUI based on the recurring property configuration
            Works for both routines and tasks
        '''
        loadedToday = [] 
        today = datetime.datetime.today().date() # In the form YYYY-MM-DD

        # Loop over exsisting recuring entries
        for rec in R:

            # Data from database about recurrances
            frequency = int(rec['recurFrequency']) # A number 1-7
            refDate = rec['recurRefDate'].split("-") # A date in a YYYY-MM-DD form

            # Create create reference date as a datetime object 
            refInfo = {'year':int(refDate[0]), 'month' : int(refDate[1]), 'day' : int(refDate[2])}
            refDate = datetime.date(**refInfo)

            # Use datetime object to determine if a recurant task is to recur today
            daysSinceCreation = today - refDate
            if daysSinceCreation.days % frequency == 0:
                loadedToday.append(rec)

        return loadedToday
    

# mTask object
mtask = mTask()

# Begin mainloop for tk constructor window outside class
mtask.root.mainloop()

        