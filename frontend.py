import tkinter as tk
import tkinter.filedialog as fg
from backend import Project
import os
import datetime
import pandas as pd
from pytz import timezone
import pytz
from threading import Thread

#WINDOW CLASS FORMAT (doesnt include __init__)
#1. WINDOW VARIABLES
#2. WINDOW ELEMENTS
#3. DRAW COMMANDS
#4. WINDOW FUNCTIONS

class GeotagTool(tk.Tk): # controller
      
    def __init__(self, *args, **kwargs):  
          
        tk.Tk.__init__(self, *args, **kwargs) 
        
        self.project = Project()
        
        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)  
        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 
   
        self.frames = {}   
        
        for F in (StartPage, LoadProjectPage, LoadDataPage, ExportPage): 
   
            frame = F(container, self) 
   
            self.frames[F] = frame  
   
            frame.grid(row = 0, column = 0, sticky ="nsew") #This is the problem, also have to convert all grids to packs
   
        self.show_frame(StartPage) 
   
    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 
   
# Choose to create a project or load an existing project   
class StartPage(tk.Frame): 
    def __init__(self, parent, controller):  

        tk.Frame.__init__(self, parent) 
        
        #WINDOW VARIABLES
        version = '0.0.1'
        
        #WINDOW ELEMENTS
        window_label = tk.Label(self,text ='Geotag Tool '+version,font=('Arial',12,'bold'))
        
        create_button = tk.Button(self, text ='New Project', 
        command = lambda : controller.show_frame(LoadDataPage))
        
        load_button = tk.Button(self, text ='Load Project', 
        command = lambda : controller.show_frame(LoadProjectPage))
        
        #DRAW COMMANDS
        window_label.grid(row = 0, column = 0, pady = 10)
        create_button.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'W') 
        load_button.grid(row = 4, column = 0, padx = 10, pady = 10, sticky = 'W') 

#Page where user can select a project folder that has been previously generated and load the data from that folder
class LoadProjectPage(tk.Frame): 
      
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        
        #WINDOW VARIABLES
        self.controller = controller
        self.parent = parent
        
        #WINDOW ELEMENTS
        path_button = tk.Button(self, text = 'Select',
        command = self.get_p_path)
        
        path_label = tk.Label(self, text = 'Project File( .pkl): ')
        
        self.path_str = tk.StringVar()
        
        self.path_entry = tk.Entry(self, textvariable = self.path_str)
        
        load_button = tk.Button(self, text = 'Load Project',
        command = self.load_project)
        
        back_button = tk.Button(self, text ="Back", 
        command = lambda : controller.show_frame(StartPage)) 
        
        #DRAW COMMANDS
        path_button.grid(row = 1, column = 3, sticky = 'W', pady = 15)
        path_label.grid(row = 1, column = 1, sticky = 'W', pady = 15)
        self.path_entry.grid(row = 1, column = 2, sticky = 'W', pady = 15, ipadx = 90)
        load_button.grid(row = 6, column = 1, sticky = 'W', pady = 15)
        back_button.grid(row = 6, column = 2, sticky = 'W', pady = 15)
    
    #WINDOW FUNCTIONS
    def get_p_path(self):
        self.projectPath = tk.filedialog.askopenfilename(filetypes=[('Project Files', '*.pkl')])
        self.path_str.set(str(self.projectPath))
        
    def load_project(self):
        if self.path_str.get() == '':
            self.path_entry.configure({"background": "red"})
            return
        else:
            self.path_entry.configure({"background": "white"})
        self.controller.project.load(projectFile = self.path_str.get())
        
        for attr in ['projectName','config','videos','tracks']:
            if attr in vars(self.controller.project):
                setattr(self.controller, attr, getattr(self.controller.project, attr))
        self.controller.project.create(self.controller.project.projectName, 
                                       self.controller.project.config, 
                                       videos = self.controller.project.videos, 
                                       tracks =self.controller.project.tracks)
        frame = MatchPage(self.parent, self.controller)
        self.controller.frames[MatchPage] = frame
        frame.grid(row = 0, column = 0, sticky ="nsew")
        for attr in ['time_col','lat_col','long_col','ele_col','offset']:
            if attr in vars(self.controller.project):
                setattr(self.controller, attr, getattr(self.controller.project, attr))
        frame.time_col.set(self.controller.time_col)
        frame.lat_col.set(self.controller.lat_col)
        frame.long_col.set(self.controller.long_col)
        frame.ele_col.set(self.controller.ele_col)
        frame.offset.set(self.controller.offset)
        
        self.controller.show_frame(MatchPage)
        
# Autoscan on: select folder where input files are; Autoscan off select video and track files individually        
class LoadDataPage(tk.Frame):  
    
    def __init__(self, parent, controller): 
        
        tk.Frame.__init__(self, parent) 
        
        #WINDOW VARIABLES
        self.controller = controller
        self.parent = parent
        time = datetime.datetime.now()
        projectName = 'project'+ time.strftime('%Y-%m-%d_%H%M%S')
        self.projectName = projectName
        self.yoffset = 1
        
        #WINDOW ELEMENTS
        window_label = tk.Label(self,text ='Project Setup',font=('Arial',12,'bold'))
        
        self.autoscan_int = tk.IntVar()
        autoscan_check = tk.Checkbutton(self, text='', variable=self.autoscan_int, width = 5)
        autoscan_label = tk.Label(self, text = 'Autoscan')
        
        self.next_button = tk.Button(self, text = 'Continue', command = self.get_input)
        
        self.name_str = tk.StringVar(self)
        self.name_str.set(self.projectName)
        name_label = tk.Label(self, text = 'Project Name: ')
        self.name_entry = tk.Entry(self, textvariable = self.name_str)
        
        self.pconfig_str = tk.StringVar(self)
        self.pconfig_str.set('EXIF')
        p_config = tk.OptionMenu(self, self.pconfig_str, 'EXIF', 'trident')
        p_config_label = tk.Label(self, text = 'Project Config: ')
        
        back_button = tk.Button(self, text ="Back", 
        command = lambda : controller.show_frame(StartPage))
        
        #DRAW COMMANDS
        window_label.grid(row = -1+self.yoffset, column = 1, sticky = 'W', pady = 10)
        name_label.grid(row = 0+self.yoffset, column = 1, sticky = 'W', pady = 10)
        self.name_entry.grid(row = 0+self.yoffset, column = 2, sticky = 'W', pady = 15, ipadx = 45)
        p_config_label.grid(row = 2+self.yoffset, column = 1, sticky = 'W', pady = 10)
        p_config.grid(row = 2+self.yoffset, column = 2, sticky = 'W', pady = 10)
        autoscan_check.grid(row = 3+self.yoffset, column = 2, sticky = 'W', pady = 10)
        autoscan_label.grid(row = 3+self.yoffset, column = 1, sticky = 'W', pady = 10)
        self.next_button.grid(row = 8+self.yoffset, column = 1, sticky = 'W', pady = 10)
        back_button.grid(row=8+self.yoffset, column = 2)
    
    #WINDOW FUNCTIONS
    def get_i_path(self):
        self.inputPath = str(tk.filedialog.askdirectory())+'/'
        self.ipath_str.set(self.inputPath)
        
    def get_p_path(self):
        self.projectPath = str(tk.filedialog.askdirectory())+'/'
        self.ppath_str.set(self.projectPath)
        self.get_p_name()
        
    def get_p_name(self):
        self.projectName = self.name_str.get()
        
    def get_video(self):
        video = tk.filedialog.askopenfilename()
        self.videos.append(video)
        self.videos_str.set(str([i.split('/')[-1] for i in self.videos]))
        
    def get_track(self):
        track = tk.filedialog.askopenfilename()
        self.tracks.append(track)
        self.tracks_str.set(str([i.split('/')[-1] for i in self.tracks]))
        
    def get_input(self):
        if self.name_str.get() == '':
            self.name_entry.configure({"background": "red"})
            return
        else:
            self.name_entry.configure({"background": "white"})
            
        self.next_button.destroy()
        if self.projectName != None:
            autoscan = self.autoscan_int.get() == 1
            if autoscan is True:
                ipath_button = tk.Button(self, text = 'Select',
                command = self.get_i_path)
                self.ipath_str = tk.StringVar(self)
                self.ipath_entry = tk.Entry(self, textvariable = self.ipath_str)
                ipath_label = tk.Label(self, text = 'Input Folder: ')
                
                next_button1 = tk.Button(self, text = 'Scan For Files', command = self.autoscan)
                
                ipath_button.grid(row = 4+self.yoffset, column = 3, padx = 10, pady = 10, sticky = 'W')
                self.ipath_entry.grid(row = 4+self.yoffset, column = 2, padx = 10, pady = 10, ipadx=90)
                ipath_label.grid(row = 4+self.yoffset, column = 1, padx = 10, pady = 10, sticky = 'W')
                next_button1.grid(row = 5+self.yoffset, column = 1, padx = 10, pady = 10)
                
            if autoscan is False:
                self.videos = []
                self.tracks = []
                video_button = tk.Button(self, text = 'Add Video', command = self.get_video)
                self.video_str = tk.StringVar(self)
                self.video_entry = tk.Entry(self, textvariable = self.video_str)
                
                track_button = tk.Button(self, text = 'Add Track', command = self.get_track)
                self.track_str = tk.StringVar(self)
                self.track_entry = tk.Entry(self, textvariable = self.track_str)
                
                self.load_str = tk.StringVar()
                load_status = tk.Label(self, textvariable = self.load_str)
                load_button = tk.Button(self, text ='Load Files', 
                command = self.load_files)
                
                video_button.grid(row = 5+self.yoffset, column = 1, padx = 10, pady = 10)
                self.video_entry.grid(row = 5+self.yoffset, column = 2, padx = 10, pady = 10, ipadx=90)
                track_button.grid(row = 6+self.yoffset, column = 1, padx = 10, pady = 10)
                self.track_entry.grid(row = 6+self.yoffset, column = 2, padx = 10, pady = 10, ipadx=90)
                load_status.grid(row = 8+self.yoffset, column = 2, pady = 10, sticky = 'W')
                load_button.grid(row=8+self.yoffset, column=1, padx = 10, pady = 10)

    def autoscan(self):
        if self.ipath_str.get() == '':
            self.ipath_entry.configure({"background": "red"})
            return
        else:
            self.ipath_entry.configure({"background": "white"})
        videos = []
        tracks = []
        self.next_button.pack_forget()
        for filename in os.listdir(str(self.inputPath)):
            if 'MP4' in filename.split('.'):
                if len(filename.split('.')) <= 2:
                    videos.append(str(self.inputPath)+filename)
            if 'gpx' in filename.split('.'):
                if len(filename.split('.')) <= 2:
                    tracks.append(str(self.inputPath)+filename)
            if 'csv' in filename.split('.'):
                if len(filename.split('.')) <= 2:
                    tracks.append(str(self.inputPath)+filename)
        self.videos = videos
        self.tracks = tracks
        
        video_label = tk.Label(self, text=  'Videos: ')
        self.video_str = tk.StringVar(self)
        self.video_str.set(str([i.split('/')[-1] for i in self.videos]))
        self.video_entry = tk.Entry(self, textvariable=self.video_str)
        
        
        track_label = tk.Label(self, text=  'Tracks: ')
        self.track_str = tk.StringVar(self)
        self.track_str.set(str([i.split('/')[-1] for i in self.tracks]))
        self.track_entry = tk.Entry(self, textvariable=self.track_str)
        
        
        self.load_str = tk.StringVar()
        load_status = tk.Label(self, textvariable = self.load_str)
        
        load_button = tk.Button(self, text ='Load Files', 
        command=self.load_files)

        video_label.grid(row = 6+self.yoffset, column = 1, padx = 10, pady = 10)
        self.video_entry.grid(row = 6+self.yoffset, column = 2, padx = 10, pady = 10, ipadx=90)
        track_label.grid(row = 7+self.yoffset, column = 1, padx = 10, pady = 10)
        self.track_entry.grid(row = 7+self.yoffset, column = 2, padx = 10, pady = 10, ipadx=90)
        load_status.grid(row = 8+self.yoffset, column = 2, sticky = 'W')
        load_button.grid(row=8+self.yoffset, column=1)
    
    def load_files(self):
        if self.video_str.get() == '':
            self.video_entry.configure({"background": "red"})
            return
        else:
            self.video_entry.configure({"background": "white"})
        if self.track_str.get() == '':
            self.track_entry.configure({"background": "red"})
            return
        else:
            self.video_entry.configure({"background": "white"})
            
        self.config = self.pconfig_str.get()
        self.load_str.set('Loading files...')
        self.controller.project.create(self.projectName, self.config, videos = self.videos, tracks = self.tracks)
        frame = MatchPage(self.parent, self.controller) 
        self.controller.frames[MatchPage] = frame  
        frame.grid(row = 0, column = 0, sticky ="nsew")
        self.controller.show_frame(MatchPage)

# Main function called on inputs: desired columns, time offset, maxtimediff       
class MatchPage(tk.Frame):  
    def __init__(self, parent, controller): 
        
        tk.Frame.__init__(self, parent) 
        
        #WINDOW VARIABLES
        self.controller = controller
        columns = list(self.controller.project.pointsDFs[0].columns)
        self.controller.time_col = 'None'
        self.controller.lat_col = 'None'
        self.controller.long_col = 'None'
        self.controller.ele_col = 'None'
        self.controller.offset = ''
        
        #WINDOW ELEMENTS
        self.time_col = tk.StringVar(self)
        self.time_col.set(self.controller.time_col)
        time_col_label = tk.Label(self, text = 'Desired Time Column:')
        time_col_menu = tk.OptionMenu(self, self.time_col, *columns)
        
        self.lat_col = tk.StringVar(self)
        self.lat_col.set(self.controller.lat_col)
        lat_col_label = tk.Label(self, text = 'Desired Lat Column:')
        lat_col_menu = tk.OptionMenu(self, self.lat_col, *columns)
        
        self.long_col = tk.StringVar(self)
        self.long_col.set(self.controller.long_col)
        long_col_label = tk.Label(self, text = 'Desired Long Column:')
        long_col_menu = tk.OptionMenu(self, self.long_col, *columns)
        
        self.ele_col = tk.StringVar(self)
        self.ele_col.set(self.controller.ele_col)
        ele_col_label = tk.Label(self, text = 'Desired Ele Column:')
        ele_col_menu = tk.OptionMenu(self, self.ele_col, *columns)
        
        self.offset = tk.StringVar(self)
        self.offset.set(self.controller.offset)
        offset_label = tk.Label(self, text = 'Manual Time Offset: ')
        offset_label2 = tk.Label(self, text = '(leave blank for auto)')
        offset_entry = tk.Entry(self, textvariable = self.offset)
        
        self.match_status_str = tk.StringVar(self)
        match_status = tk.Label(self,textvariable = self.match_status_str)
        match_button = tk.Button(self, text ='Match', command = self.do_match)
        
        back_button = tk.Button(self, text ='Back', 
                            command = lambda : controller.show_frame(StartPage))

        #DRAW COMMANDS
        time_col_label.grid(row = 1, column = 1, sticky = 'E', pady = 10)
        time_col_menu.grid(row = 1, column = 2, sticky = 'W', pady = 10)
        
        lat_col_label.grid(row = 2, column = 1, sticky = 'E', pady = 10)
        lat_col_menu.grid(row = 2, column = 2, sticky = 'W', pady = 10)
        
        long_col_label.grid(row = 3, column = 1, sticky = 'E', pady = 10)
        long_col_menu.grid(row = 3, column = 2, sticky = 'W', pady = 10)
        
        ele_col_label.grid(row = 4, column = 1, sticky = 'E', pady = 10)
        ele_col_menu.grid(row = 4, column = 2, sticky = 'W', pady = 10)
        
        offset_label.grid(row = 5, column = 1, sticky = 'W', pady = 10)
        offset_label2.grid(row = 5, column = 3, sticky = 'W', pady = 10)
        offset_entry.grid(row = 5, column = 2, sticky = 'W', pady = 15)
        
        match_status.grid(row = 8, column = 2, sticky = 'W')
        match_button.grid(row = 8, column = 1, sticky = 'W')
        
        back_button.grid(row=9, column=5)
    
    #WINDOW FUNCTIONS
    def do_match(self):
        try:
            self.continue_button.pack_forget()
        except AttributeError: pass
        info = True
        self.points = 0
        for i in [self.time_col, self.lat_col, self.long_col]:
            if i == 'None':
                info = False
                break
        if info == True:
            self.controller.project.match(self.time_col.get(), 
                                             self.lat_col.get(), 
                                             self.long_col.get(), 
                                             self.ele_col.get(),
                                             self.offset.get(),
                                             self.match_status_str)      
            
            self.continue_button = tk.Button(self, text ='Continue', 
                                command = lambda : self.controller.show_frame(ExportPage))
            
            
            self.continue_button.grid(row=9, column=4)
            
class ExportPage(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent) 
        
        #WINDOW VARIABLES
        self.controller = controller
        
        #WINDOW ELEMENTS
        window_label = tk.Label(self,text ='Export Page',font=('Arial',12,'bold'))
        
        ppath_label = tk.Label(self, text = 'Project Save Path: ')
        self.ppath_str = tk.StringVar()
        self.ppath_entry = tk.Entry(self, textvariable = self.ppath_str)
        ppath_button = tk.Button(self, text = 'Select',
                                 command = self.get_p_path)
        save_button = tk.Button(self, text = 'Save Project', command = self.save_project)
        self.s_status_str = tk.StringVar(self)
        s_status_label = tk.Label(self, textvariable = self.s_status_str)
            
        epath_label = tk.Label(self, text = 'Image Export Path: ')
        self.epath_str = tk.StringVar()
        self.epath_entry = tk.Entry(self, textvariable = self.epath_str)
        epath_button = tk.Button(self, text = 'Select',
                                 command = self.get_e_path)
        export_button = tk.Button(self, text = 'Export Project', command = self.threading)
        self.e_status_str = tk.StringVar(self)
        e_status_label = tk.Label(self, textvariable = self.e_status_str)
        
        
        back_button = tk.Button(self, text ="Back", 
                        command = lambda : controller.show_frame(StartPage))
        
        #DRAW COMMANDS
        window_label.grid(row = 0, column = 0, pady = 10)
        
        ppath_label.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = 'W')
        self.ppath_entry.grid(row = 1, column = 1, padx = 10, pady = 10, sticky = 'W', ipadx = 90)
        ppath_button.grid(row = 1, column = 2, padx = 10, pady = 10, sticky = 'W')
        save_button.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = 'W')
        s_status_label.grid(row = 2, column = 2, padx = 10, pady = 10, sticky = 'W')
        
        epath_label.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'W')
        self.epath_entry.grid(row = 3, column = 1, padx = 10, pady = 10, sticky = 'W', ipadx = 90)
        epath_button.grid(row = 3, column = 2, padx = 10, pady = 10, sticky = 'W')
        export_button.grid(row = 4, column = 1, padx = 10, pady = 10, sticky = 'W')
        e_status_label.grid(row = 4, column = 2, padx = 10, pady = 10, sticky = 'W')
        
        #WINDOW FUCTIONS
    def get_p_path(self):
        self.projectPath = str(tk.filedialog.askdirectory()) + '/'
        self.ppath_str.set(self.projectPath)
        
    def get_e_path(self):
        self.exportPath = str(tk.filedialog.askdirectory()) + '/'
        self.epath_str.set(self.exportPath)
        
    def save_project(self):
        if self.ppath_str.get() == '':
            self.ppath_entry.configure({"background": "red"})
            return
        else:
            self.ppath_entry.configure({"background": "white"})
        self.controller.project.save(self.ppath_str.get(), self.s_status_str)
    
    def threading(self): 
        t1= Thread(target=self.export_project) 
        t1.setDaemon(True) 
        t1.start()
        
    def export_project(self):
        if self.epath_str.get() == '':
            self.epath_entry.configure({"background": "red"})
            return
        else:
            self.epath_entry.configure({"background": "white"})
            
        self.controller.project.export(self.epath_str.get(), self.e_status_str, self.controller)

