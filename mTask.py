from tkinter import *
from tkinter import ttk

class mTask():

    def __init__(self):
        
        self.root = Tk()
        self.root.title('mTask')

        # Menu Control ---------------------------------------------------------
        self.menubar = Menu(self.root)
        self.root.config(menu = self.menubar)

        self.taskMenu = Menu(self.menubar, tearoff = 0)
        self.taskMenu.add_command(label = "New Task")
        self.taskMenu.add_command(label = "Edit Task")
        self.taskMenu.add_command(label = "Load Task")
        self.taskMenu.add_command(label = "Save Task")
        self.menubar.add_cascade(menu = self.taskMenu, label = "Tasks")

        self.routinesMenu = Menu(self.menubar, tearoff = 0)
        self.routinesMenu.add_command(label = "New Rouine")
        self.routinesMenu.add_command(label = "Edit Rouine")
        self.routinesMenu.add_command(label = "Load Rouine")
        self.routinesMenu.add_command(label = "Save Rouine")
        self.routinesMenu.add_separator()
        self.routinesMenu.add_command(label = "Add Task")
        self.menubar.add_cascade(menu = self.routinesMenu, label = "Rouines")

        # ~ Menu Control ---------------------------------------------------------

        # Tab Control Init ------------------------------------------------------------
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.pack()

        self.dict1 = [{'taskName':'myTask1','taskTime':'myTime1','routineName':'Tasks'}]
        self.addRoutineToGUI(tasks = self.dict1)
        # ~ Tab Control ------------------------------------------------------------
    
    def addTaskToGUI(self, taskName, taskTime, routineName):
        '''
            Adds new tab to window with all task objects specified in task
            tasks is list of dictionaries with following form:
                {'taskName':str(value),'taskTime' : str(value), 'routineName' : routineName}
        '''
        for i, element in enumerate(self.tabControl.winfo_children()):
            tabTitle = str(self.tabControl.tab(i, option = "text"))
            if tabTitle == routineName:
                for child in element.winfo_children():
                    if child.cget("text") == "Incomple Tasks":
                        numTasks = len(child.winfo_children())
                        ttk.Button(child, text = "Complete").grid(row = numTasks, column = 0 , padx = 15, pady = 15)
                        ttk.Label(child, text = str(taskTime)).grid(row = numTasks, column = 1 , padx = 15, pady = 15)
                        ttk.Label(child, text = str(taskName)).grid(row = numTasks, column = 2 , padx = 15, pady = 15)
                        break
                break
    
    def addRoutineToGUI(self, tasks =  [], routineName = ""):
        '''
            Adds new tab to root window with all task objects, 
            whose values are specified in tasks parameter
            tasks is list of dictionaries with following form:
                {'taskName':str(value),'taskTime' : str(value), 'routineName' : routineName}
            All routineName entries must be identical in tasks. 
            tasks may be empty to create a new empty tab as well.
        '''
        self.routineTab = ttk.Frame(self.tabControl)
        if len(tasks) > 0:
            routineName = tasks[0]['routineName']
        self.tabControl.add(self.routineTab, text = routineName)

        self.toDoTaskFrame = LabelFrame(self.routineTab, text = "Incomple Tasks", width = 100, height = 100)
        self.completedTaskFrame = LabelFrame(self.routineTab, text = "Completed Tasks")
        self.progressBar = ttk.Progressbar(self.routineTab, mode = "determinate", maximum = 10.0, value = 4.2)
        self.toDoTaskFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        self.completedTaskFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)
        self.progressBar.pack(fill = "both", expand = True)

        ttk.Label(self.toDoTaskFrame, text = "Complete Task").grid(row = 0, column = 0 , padx = 15, pady = 15)
        ttk.Label(self.toDoTaskFrame, text = "Time").grid(row = 0, column = 1 , padx = 15, pady = 15)
        ttk.Label(self.toDoTaskFrame, text = "Task").grid(row = 0, column = 2 , padx = 15, pady = 15)

        if len(tasks) > 0:
            for task in tasks:
                if routineName != task['routineName']:
                    raise Exception("All tasks must have the same routineName property")
                self.addTaskToGUI(**task)
        
        ttk.Label(self.completedTaskFrame, text = "Completed Tasks").grid(row = 0, column = 0 , padx = 15, pady = 15)
        ttk.Label(self.completedTaskFrame, text = "Completion Time").grid(row = 0, column = 1 , padx = 15, pady = 15)

    def showParentInfo(self, event):
        print(self.tabControl.tabs())
        
# mTask object
mtask = mTask()

# Begin mainloop for tk constructor window outside class
mtask.root.mainloop()

        