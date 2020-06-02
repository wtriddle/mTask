from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox

from bwDB import bwDB
from taskFunctions import TaskFunctions
from routineFunctions import RoutineFunctions

from threading import Thread
from queue import Queue
import time

class mTask():

    def __init__(self):
        
        # Root, Database, and Menu Init -----------------------------------------------------------------------
        self.root = Tk()                                                # Top level window
        self.root.title('mTask')                                        # Assign a title
        self.root.geometry("640x480+10+15")

        self.initDB()                                                   # Initalize user database

        self.taskFunctions = TaskFunctions(self)                        # Initalize task menu functionality
        self.routineFunctions = RoutineFunctions(self)                  # Initalize routine menu functionality
        self.initMenu(self.taskFunctions, self.routineFunctions)        # Initialize menu with functionality
        # ~ Root, Database, and Menu Init --------------------------------------------------------------------

        # Tab Control Init -----------------------------------------------------------------------------------
        self.tabControl = ttk.Notebook(self.root)                       # Top level notebook 
        self.tabControl.pack(padx=10,pady=10)                           # Pack into GUI

        self.addRoutineToGUI(routineName = "Tasks")                     # Default tab for tasks w/o specific routine
        # ~ Tab Control --------------------------------------------------------------------------------------

        # Styles ---------------------------------------------------------------------------------------------
        # self.style = ttk.Style(self.root)
        # self.style.configure("TButton", background = "yellow", foreground = "green")
        # ~ Styles ---------------------------------------------------------------------------------------------
    
    def addTaskToGUI(self, taskName, taskTime, routineName):
        '''
            Adds new tab to window with all task objects specified in task
            tasks is list of dictionaries with following form:
                {'taskName':str(value),'taskTime' : str(value), 'routineName' : routineName}
        '''
        for i, tab in enumerate(self.tabControl.winfo_children()):

            tabTitle = str(self.tabControl.tab(i, option = "text"))
            
            if tabTitle == routineName:
                
                # Widgets associtated with routine tab
                toDoTaskFrame = tab.winfo_children()[0]
                progressFrame = tab.winfo_children()[2]
                progressBar = progressFrame.winfo_children()[0]

                # Error if task is already inside of GUI
                loadedTasks = []
                for child in toDoTaskFrame.winfo_children():
                    if child.winfo_class() == "TButton":
                        loadedTasks.append(str(child.cget('text')[9:len(child.cget('text'))]))
                if taskName in loadedTasks:
                    mBox.showerror(title = "Task Insertion Error", message= "Please enter a task that is not loaded into the " + routineName + " tab")
                    return 

                # Update the toDoTaskFrame
                numTasks = int(len(toDoTaskFrame.winfo_children()) / 3) # 3 widgets per task
                button = ttk.Button(toDoTaskFrame, text = "Complete " + taskName)
                button.grid(row = numTasks, column = 0 , padx = 15, pady = 15)
                button.bind("<Button-1>", self.completionOfTask)
                ttk.Label(toDoTaskFrame, text = str(taskTime)).grid(row = numTasks, column = 1 , padx = 15, pady = 15)
                ttk.Label(toDoTaskFrame, text = str(taskName)).grid(row = numTasks, column = 2 , padx = 15, pady = 15)
                
                # Increment maximum on progressbar 
                currentMax = progressBar.cget("maximum") + 0.0
                progressBar.configure(maximum = currentMax + 1.0)

    def addRoutineToGUI(self, tasks =  [], routineName = ""):
        '''
            Adds new tab to root window with label frames and a progress bar.
            If the optional tasks list argument is specified, the function will:
                automatically paste tasks to the in-complete frame,
                and configure the progress bar
        '''

        self.routineTab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.routineTab, text = routineName)

        self.toDoTaskFrame = LabelFrame(self.routineTab, text = "Incomple Tasks", width = 100, height = 100)
        self.completedTaskFrame = LabelFrame(self.routineTab, text = "Completed Tasks")
        self.progressFrame = LabelFrame(self.routineTab, text = "Progress")
        self.progressBar = ttk.Progressbar(self.progressFrame, mode = "determinate", maximum = 0.0)

        self.toDoTaskFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        self.completedTaskFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        self.progressFrame.pack(fill = "both", padx = 10, pady = 10)
        self.progressBar.pack(fill = "both", expand = True, padx = 10, pady = 10)

        ttk.Label(self.toDoTaskFrame, text = "Complete Task").grid(row = 0, column = 0 , padx = 15, pady = 15)
        ttk.Label(self.toDoTaskFrame, text = "Time").grid(row = 0, column = 1 , padx = 15, pady = 15)
        ttk.Label(self.toDoTaskFrame, text = "Task").grid(row = 0, column = 2 , padx = 15, pady = 15)

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
            Removes the completed task from the in-complete window,
            Adds the task to the completed window,
            and updates the routine progress bar
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
            
            if currentRow == completedRow: 
                task.destroy()
            
            # Shift all task widgets below the completed row up by one to refactor the GUI
            elif currentRow > completedRow:
                task.grid_configure(row = currentRow - 1)

        # Update the completed task frame
        numCompletedTasks = int(len(completedFrame.winfo_children()) / 2) # 2 widgets per completed task
        ttk.Label(completedFrame, text = taskName).grid(row = numCompletedTasks, column = 0, padx = 15, pady = 15)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S %p", t)
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
            time.sleep(0.01)
            i+=1

    def initDB(self):

        self.mTaskDB = bwDB(filename = "mTaskDB.db")

        self.mTaskDB.sql_do('''
            CREATE TABLE IF NOT EXISTS Tasks(
                id INTEGER PRIMARY KEY,
                taskName TEXT,
                taskTime TEXT,
                taskDescription TEXT,
                routineName TEXT DEFAULT \"Tasks\" NOT NULL,
                CONSTRAINT task_info UNIQUE(taskName, routineName)
            );
        ''')

        self.mTaskDB.sql_do('''
            CREATE TABLE IF NOT EXISTS Routines(
                routineName TEXT PRIMARY KEY,
                routineDescription TEXT
            );
        ''')
        self.mTaskDB.set_table("Routines")
        if self.mTaskDB.countrecs() == 0:
            query = f'INSERT INTO Routines VALUES (\"Tasks\", \"DEFAULT\")'
            self.mTaskDB.sql_do(query)

    def initMenu(self, taskFunctions, routineFunctions):
        self.menubar = Menu(self.root)
        self.root.config(menu = self.menubar)

        self.taskMenu = Menu(self.menubar, tearoff = 0)
        self.taskMenu.add_command(label = "New Task", command = taskFunctions.newTask)
        self.taskMenu.add_command(label = "Edit Task", command = taskFunctions.editTask)
        self.taskMenu.add_command(label = "Load Task", command = taskFunctions.loadTask)
        self.menubar.add_cascade(menu = self.taskMenu, label = "Tasks")

        self.routinesMenu = Menu(self.menubar, tearoff = 0)
        self.routinesMenu.add_command(label = "New Rouine", command = routineFunctions.newRoutine)
        self.routinesMenu.add_command(label = "Edit Rouine", command = routineFunctions.editRoutine)
        self.routinesMenu.add_command(label = "Load Rouine", command = routineFunctions.loadRoutine)
        self.menubar.add_cascade(menu = self.routinesMenu, label = "Rouines")

    def loadUserTasks(self):
        self.mTaskDB.set_table(tablename = "Tasks")
        recs = list(self.mTaskDB.getrecs())
        userTasks = []
        if recs:
            userTasks = [rec['taskName'] for rec in recs]
            userTasks = list(dict.fromkeys(userTasks))
        return userTasks
    
    def loadUserRoutines(self):
        self.mTaskDB.set_table(tablename = "Routines")
        recs = list(self.mTaskDB.getrecs())
        userRoutines = []
        if recs:
            userRoutines = [rec['routineName'] for rec in recs]
            userRoutines = list(dict.fromkeys(userRoutines))
        return userRoutines
        
# mTask object
mtask = mTask()

# Begin mainloop for tk constructor window outside class
mtask.root.mainloop()

        