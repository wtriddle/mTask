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
    """
        Central class for GUI layout, updates, and initalizations.
        Includes common database functionality
    """

    def __init__(self):
        """GUI init"""
        
        # Root, Database, and Menu Init ----------------------------------------------------------
        self.root = Tk()                                    # Top level window
        self.root.title('mTask')                            # Assign a title
        self.root.geometry("-2650+150")                     # Temporary geometry configuration
        self.root.iconbitmap("mTask.ico")                   # mTask icon config

        self.initDB()                                       # Initalize user database

        tFuncs = TaskFunctions(self)                        # Initalize task menu functionality
        rFuncs = RoutineFunctions(self)                     # Initalize routine menu functionality
        hFuncs = HelpFunctions(self)                        # Initalize help menu functionality
        self.initMenu(tFuncs,                               # Create menu with functionality
                    rFuncs, 
                    hFuncs
                    ) 
        # ~ Root, Database, and Menu Init ---------------------------------------------------------

        # Tab Control Init ------------------------------------------------------------------------
        self.nb = ttk.Notebook(self.root)                       # Top level notebook 
        self.nb.pack(padx=10, pady=10, ipadx=100, ipady=100)    # Pack notebook into GUI
        self.initTabs()                                         # Initialize the GUI with recurring tasks/routines
        # ~ Tab Control -----------------------------------------------------------------------------

        # Styles ------------------------------------------------------------------------------------
        self.s = ttk.Style(self.root)                           # Main style

        self.s.theme_use("xpnative")

        self.s.configure("TButton", background = "#1b262c", foreground = "#0f4c75", relief = "RIDGE", font = ("times", 15))
        self.s.configure("TFrame", background = "#0f4c75", foreground = "#1b262c", font = ("times", 12))
        self.s.configure("TLabel", background = "#0f4c75", foreground = "#acdbdf", font = ("times", 15))
        self.s.configure("TLabelframe", background = "#0f4c75", foreground = "green", font = ("times", 12))

        self.root.option_add("*TEntry.font", ("times", 15))
        self.root.option_add("*TCombobox*Listbox.font", ("times", 15))
        self.root.option_add("*TCombobox.font", ("times", 15))
        self.root.option_add("*TCombobox.background", "green")
        self.root.option_add("*TCombobox*Listbox.background", "#1f4287")
        self.root.option_add("*TCombobox*Listbox.foreground", "#00d5ff")
        # ~ Styles -------------------------------------------------------------------------------------------

    def addTaskToGUI(self, taskName, taskTime, taskDescription, routineName):
        """Appends three task widgets to a specific routine tab and increases the maximum of the routine progress bar by 1

            An exception is raised for a non-exsistent routine tab
            An error is raised for an already loaded task     
        """

        # Locate tab for task appension
        tab = self.getRoutineTab(routineName)
        if not tab:
            raise Exception("Could not add tasks to a tab that does not exist")

        # Relevent widgets within tab
        tdFrame = tab.winfo_children()[0] # To-do Task Frame
        pFrame = tab.winfo_children()[2] # Progress bar frame
        pBar = pFrame.winfo_children()[0] # Progress bar

        # Present an Error if task is already inside of tab
        loadedTasks = [child.cget("text") for child in tdFrame.winfo_children()]
        if taskName in loadedTasks:
            mBox.showerror(title="Task Insertion Error", 
            message="Please enter a task that is not loaded into the " + routineName + " tab")
            return 

        # Compute which row to append new task info to
        numTasks = int(len(tdFrame.winfo_children()) / 3) # 3 widgets per task row, divide total widgets by 3

        # Completion Button
        b = ttk.Button(tdFrame, text = "Complete " + taskName)
        b.grid(row = numTasks, column = 0 , padx = 15, pady = 15)
        b.bind("<Button-1>", self.completionOfTask) 

        # Task Time
        ttk.Label(tdFrame, text = str(taskTime)).grid(row = numTasks, column = 1 , padx = 15, pady = 15)

        # Task Name
        tLabel = ttk.Label(tdFrame, text = str(taskName))
        tLabel.grid(row = numTasks, column = 2 , padx = 15, pady = 15)
        
        # Increment maximum on pBar 
        currentMax = pBar.cget("maximum") + 0.0
        pBar.configure(maximum = currentMax + 1.0)

        # Set the focus to the tab where the task was added to
        self.nb.select(tab)

        # Add descriptor to label.
        descriptor.createDescriptor(tLabel, taskDescription)

    def addRoutineToGUI(self, tasks = [], *, routineName = ""):
        """Adds a routine tab to the GUI with full task listings and progress bar functionality
        
            Keyword Arguments:
            routineName -- The name of the new tab
            tasks -- List of task dictionaries, whose keys are {taskName, taskTime, routineName}

            Exception is raised if there is not a unanimous routineName shared among all dictionaries in the tasks list
        """

        r = ttk.Frame(self.nb)
        self.nb.add(r, text = routineName)

        tdFrame = ttk.LabelFrame(r, text = " Incomplete Tasks ")
        ctFrame = ttk.LabelFrame(r, text = " Completed Tasks ") 
        pFrame = ttk.LabelFrame(r, text = " Progress ")
        pBar = ttk.Progressbar(pFrame, mode = "determinate", maximum = 0.0)

        tdFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        tdFrame.columnconfigure(0, weight = 1)
        tdFrame.columnconfigure(1, weight = 1)
        tdFrame.columnconfigure(2, weight = 1)

        ctFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        ctFrame.columnconfigure(0, weight = 1)
        ctFrame.columnconfigure(1, weight = 1)

        pFrame.pack(fill = "both", padx = 10, pady = 10)
        pBar.pack(fill = "both", expand = True, padx = 10, pady = 10)

        ttk.Label(tdFrame, text = "Complete Task").grid(row = 0, column = 0 , padx = 15, pady = 15, sticky = NS)
        ttk.Label(tdFrame, text = "Time").grid(row = 0, column = 1 , padx = 15, pady = 15, sticky = NS)
        ttk.Label(tdFrame, text = "Task").grid(row = 0, column = 2 , padx = 15, pady = 15, sticky = NS)

        if tasks:
            for task in tasks:
                if routineName != task['routineName']:
                    raise Exception("All tasks must have the same routineName property")
                self.addTaskToGUI(**task)
        
        ttk.Label(ctFrame, text = "Completed Tasks").grid(row = 0, column = 0 , padx = 15, pady = 15)
        ttk.Label(ctFrame, text = "Completion Time").grid(row = 0, column = 1 , padx = 15, pady = 15)

        self.nb.select(r)
 
    def completionOfTask(self, event):
        """Removes the completed task row, increments the progress bar and updates the competed task frame with a time stamp"""

        # Widgets 
        b = event.widget
        tdFrame = b.master
        tab = tdFrame.master
        ctFrame = tab.winfo_children()[1]
        pFrame = tab.winfo_children()[2]
        pBar = pFrame.winfo_children()[0]

        # Update the in-completed task frame
        ctRow = b.grid_info()['row'] # Completed task row
        taskName = str(b.cget('text')[9:len(b.cget('text'))]) # Remove the string "completed " from button text
        
        for task in tdFrame.winfo_children():
            row = task.grid_info()['row']
            
            # Destroy completed task from in-complete window
            if row == ctRow: 
                task.destroy()
            
            # Shift all task widgets below the completed row up by one to refactor the GUI
            elif row > ctRow:
                task.grid_configure(row = row - 1)

        # Update the completed task frame
        numCTs = int(len(ctFrame.winfo_children()) / 2) # 2 widgets per completed task
        ttk.Label(ctFrame, text = taskName).grid(row = numCTs, column = 0, padx = 15, pady = 15)
        t = time.localtime()
        t = time.strftime("%I:%M %p", t) # Completed time in 12-hour am/pm format
        ttk.Label(ctFrame, text = t).grid(row = numCTs, column = 1, padx = 15, pady = 15)

        # Update the progress bar in a new thread
        runT = Thread(target = lambda : self.updateProgressBar(pBar), daemon= True)
        runT.start()

    def updateProgressBar(self, pBar):
        """Threaded loop to make progress bar smoothly fill, for about 1 second
        
            Shows message if routine reaches completion
        """

        i = 0 
        while i <= 100:
            pBar.step(0.01)
            if pBar.cget("value") > pBar.cget("maximum") - 0.01:
                mBox.showinfo(title="Success", message="You did it! Congrats you finsihed a routine!")
                return
            time.sleep(0.01)
            i+=1

    def initDB(self):
        """Initalizes the mTaskDB object and creates the Tasks and Routines tables if they do not exist"""

        self.mTaskDB = bwDB(filename = "mTaskDB.db")

        self.mTaskDB.sql_do("""
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
        """)

        self.mTaskDB.sql_do("""
            CREATE TABLE IF NOT EXISTS Routines(
                routineName TEXT PRIMARY KEY,
                routineDescription TEXT,
                recurFrequency INTEGER DEFAULT NULL,
                recurRefDate TEXT DEFAULT NULL
            );
        """)
        self.mTaskDB.set_table("Routines")
        if self.mTaskDB.countrecs() == 0:
            query = f'INSERT INTO Routines (routineName, routineDescription) VALUES (\"Tasks\", \"DEFAULT\")'
            self.mTaskDB.sql_do(query)

    def initMenu(self, tFuncs, rFuncs, hFuncs):
        """Initializes the menu of mTask with corresponding functionality"""

        menuBar = Menu(self.root) 
        self.root.config(menu = menuBar)

        # Task menu commands
        tMenu = Menu(menuBar, tearoff = 0)
        tMenu.add_command(label = "New Task", command = tFuncs.newTask)
        tMenu.add_command(label = "Edit Task", command = tFuncs.editTask)
        tMenu.add_command(label = "Load Task", command = tFuncs.loadTask)
        tMenu.add_separator()
        tMenu.add_command(label = "Configure Recurring Task", command = tFuncs.configRecurringTask)
        menuBar.add_cascade(menu = tMenu, label = "Tasks")

        # Routine menu commands
        rMenu = Menu(menuBar, tearoff = 0)
        rMenu.add_command(label = "New Rouine", command = rFuncs.newRoutine)
        rMenu.add_command(label = "Edit Rouine", command = rFuncs.editRoutine)
        rMenu.add_command(label = "Load Rouine", command = rFuncs.loadRoutine)
        rMenu.add_separator()
        rMenu.add_command(label = "Configure Recurring Routine", command = rFuncs.configRecurringRoutine)
        menuBar.add_cascade(menu = rMenu, label = "Rouines")

        # Help menu commands
        hMenu = Menu(menuBar, tearoff = 0)
        hMenu.add_command(label = "Guide", command = hFuncs.showGuide)
        hMenu.add_command(label = "Info", command = hFuncs.showInfo)
        menuBar.add_cascade(menu = hMenu, label = "Help")

    def loadUserTasks(self, routineName = "All"):
        """Returns a list of task name strings from mTaskDB
            
            Keyword argument:
            routineName -- Which routine to load the tasks from (default "All")
            Exception raised for non-exsisting routineName in the database
        """

        self.mTaskDB.set_table(tablename = "Tasks")
        recs = list(self.mTaskDB.getrecs())
        
        # If a specific routine is chosen, overwrite recs
        if routineName != "All":
            userRoutines = self.loadUserRoutines()
            if routineName not in userRoutines:
                raise Exception("Routine name does not exist in the mTaskDB. Create it or choose another routine name")
            query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\"'
            recs = list(self.mTaskDB.sql_query(query))

        if not recs:
            return []

        userTasks = [rec['taskName'] for rec in recs]
        userTasks = list(dict.fromkeys(userTasks)) # Unqiue names only
        
        return userTasks
    
    def loadUserRoutines(self):
        """Returns a list of all user routines inside of the Routines table from mTaskDB"""

        self.mTaskDB.set_table(tablename = "Routines")
        recs = list(self.mTaskDB.getrecs())

        if not recs:
            return []        

        # routineName is PK in DB, already unique
        userRoutines = [rec['routineName'] for rec in recs] 

        return userRoutines
    
    def loadSpecificRoutine(self, routineName):
        """Load a routine directly into the GUI with its tasks into a new tab, where only the routineName is required"""

        # Destroy the routine tab if it is already loaded
        tab = self.getRoutineTab(routineName)
        if tab:
            tab.destroy()

        # Retrieve all routine specific tasks from database in a GUI acceptable form
        routineTasks = []
        query = f'SELECT * FROM Tasks WHERE routineName = \"{routineName}\"'
        tasks = list(self.mTaskDB.sql_query(query))
        for task in tasks:
            routineTasks.append({
                'taskName': task['taskName'], 
                'taskTime' : task['taskTime'],
                'taskDescription' : task['taskDescription'], 
                'routineName' : routineName})
        
        # Add the routine to the GUI
        self.addRoutineToGUI(routineName=routineName, tasks=routineTasks)

    def getRoutineTab(self, routineName):
        """Returns the tab widget for a specific routine. Returns False if the tab does not exist or is not loaded"""

        for i, tab in enumerate(self.nb.winfo_children()):
            tabTitle = str(self.nb.tab(i, option = "text"))
            if tabTitle == routineName:
                return tab
        else:
            return False

    def initTabs(self):
        """Initalizes the tabs based on recurrant properties of tasks and routines set by the user"""

        # Tasks Tab Init ---------------------------------------------
        self.mTaskDB.set_table("Tasks")
        recs = self.mTaskDB.getrecs()

        # Loads tasks with a recuring property
        recurringTasks = [rec for rec in recs if rec['recurRefDate']]
        
        if recurringTasks:
            todaysTasks = self.recurantAlgorithm(recurringTasks) # Determine what tasks should be auto-loaded
            tasksToAdd = []
            for task in todaysTasks:
                tasksToAdd.append({
                    'taskName': task['taskName'], 
                    'taskTime' : task['taskTime'],
                    'taskDescription' : task['taskDescription'], 
                    'routineName' : "Tasks"})
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
    def recurantAlgorithm(self, recurList):
        """
            Determines what routines or tasks should be automatically loaded into the GUI based on the recurring property configuration
            Works for both routines and tasks
        """
        loadedToday = [] 
        today = datetime.datetime.today().date() # In the form YYYY-MM-DD

        # Loop over exsisting recuring entries
        for rec in recurList:

            # Data from database about recurrances
            frequency = int(rec['recurFrequency']) # A number 1-7
            refDate = rec['recurRefDate'].split("-") # A date in a YYYY-MM-DD form

            # Create create reference date as a datetime object 
            refInfo = {
                'year':int(refDate[0]), 
                'month' : int(refDate[1]), 
                'day' : int(refDate[2])}
            refDate = datetime.date(**refInfo)

            # Use datetime object to determine if a recurant task is to recur today
            daysSinceCreation = today - refDate
            if daysSinceCreation.days % frequency == 0:
                loadedToday.append(rec)

        return loadedToday
    
# ==================
# Creation of GUI
# ==================

# mTask object
mtask = mTask()

# Begin mainloop for tk constructor window outside class
mtask.root.mainloop()

        