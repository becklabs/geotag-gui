from geotag_backend import Project
from tkinter import Tk,Label,Entry,Frame,Button,Checkbutton,IntVar
class App:
    def __init__(self):
        self.root = Tk()
        self.root.title('Geotag Tool')
        self._frame = None
        self.switch_frame(StartPage)
    
    def switch_frame(self, frame_class):
        new_frame = frame_class()
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
        
class StartPage:
    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root)
        self.button1 = Button(self.frame, text="Create Project", command=self.add_new_row).grid(row=0,column=0)
        self.button2 = Button(self.frame, text="Load Project", command=self.save).grid(row=0,column=1)

class CreateProject:
    def __init__(self):
        self.frame = Frame(self.root)
        Button(self.frame, text="Select Input", command=self.select_input).grid(row=0,column=0)
        Button(self.frame, text="Load Project", command=self.save).grid(row=0,column=1)
        self.autoscan = IntVar()
        Checkbutton(self.frame, text="Autoscan", variable=self.autoscan).grid(row=1, sticky='W')
    
    def get_autoscan(self):
        return self.autoscan.get() == 1
    
    def select_input(self):
        if self.get_autoscan():
            print('autoscan on')
        else:
            print('autoscan off')

#project = Project()
#project.create(inputPath=r'C:\Users\beck\Documents\CSCR\geotag-tool-python\July31', projectPath=r'C:\Users\beck\Documents\CSCR\geotag-tool-python\July31')
#project.match(timeoffset=4)
#project.export()