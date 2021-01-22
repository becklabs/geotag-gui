import tkinter as tk
import tkinter.filedialog as fg
from tkinter import ttk 
from newalgo0 import Project
import os
import datetime
import pandas as pd
from pytz import timezone
import pytz

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
        self.controller.project.load(projectPath = self.projectPath)

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
        
        #WINDOW ELEMENTS
        self.time_col_str = tk.StringVar(self)
        self.time_col_str.set('None')
        time_col_label = tk.Label(self, text = 'Desired Time Column:')
        time_col_menu = tk.OptionMenu(self, self.time_col_str, *columns)
        
        self.lat_col_str = tk.StringVar(self)
        self.lat_col_str.set('None')
        lat_col_label = tk.Label(self, text = 'Desired Lat Column:')
        lat_col_menu = tk.OptionMenu(self, self.lat_col_str, *columns)
        
        self.long_col_str = tk.StringVar(self)
        self.long_col_str.set('None')
        long_col_label = tk.Label(self, text = 'Desired Long Column:')
        long_col_menu = tk.OptionMenu(self, self.long_col_str, *columns)
        
        self.ele_col_str = tk.StringVar(self)
        self.ele_col_str.set('None')
        ele_col_label = tk.Label(self, text = 'Desired Ele Column:')
        ele_col_menu = tk.OptionMenu(self, self.ele_col_str, *columns)
        
        abbrev_tz = ['UTC','AST','EST','EDT','CST','CDT','MST','MDT','PST','PDT','AKST','AKDT','HST','HAST','HADT','SST','SDT','CHST']
        pytz.common_timezones
        self.video_tz_str = tk.StringVar(self)
        self.video_tz_str.set('EST')
        video_tz_label = tk.Label(self, text = 'Video Timezone:')
        video_tz_menu = tk.OptionMenu(self, self.video_tz_str, *pytz.common_timezones)
        
        self.track_tz_str = tk.StringVar(self)
        self.track_tz_str.set('UTC')
        track_tz_label = tk.Label(self, text = 'Track Timezone:')
        track_tz_menu = tk.OptionMenu(self, self.track_tz_str, *pytz.common_timezones)
        
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

        video_tz_label.grid(row = 5, column = 1, pady = 10, sticky = 'W')
        video_tz_menu.grid(row = 5, column = 2, pady = 10)
        
        track_tz_label.grid(row = 6, column = 1, pady = 10, sticky = 'W')
        track_tz_menu.grid(row = 6, column = 2, pady = 10)
        
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
        for i in [self.time_col_str, self.lat_col_str, self.long_col_str]:
            if i == 'None':
                info = False
                break
        if info == True:
            self.match_status_str.set('Matching...')
            self.controller.project.match(self.time_col_str.get(), 
                                            self.lat_col_str.get(), 
                                            self.long_col_str.get(), 
                                            self.ele_col_str.get(), 
                                            timezone(self.video_tz_str.get()),
                                            timezone(self.track_tz_str.get()))
            
            points = [len(df.index) for df in self.controller.project.taggedDFs]
            for i in points:
                print(i)
                self.points+=i
            self.match_status_str.set('Matched '+str(self.points)+' points')        
        
            self.continue_button = tk.Button(self, text ='Continue', 
                                command = lambda : self.controller.show_frame(ExportPage))
            self.continue_button.grid(row=9, column=4)
            
class ExportPage(tk.Frame):  
    def __init__(self, parent, controller): 
        
        tk.Frame.__init__(self, parent) 
        
        #WINDOW VARIABLES
        
        #WINDOW ELEMENTS
        self.ppath_str = tk.StringVar(self)
        self.ppath_entry = tk.Entry(self, textvariable = self.ppath_str)
        
        ppath_label = tk.Label(self, text = 'Desired Project Path: ')
        
        ppath_button = tk.Button(self, text = 'Select',
        command = self.get_p_path)
        
        back_button = tk.Button(self, text ="Back", 
                            command = lambda : controller.show_frame(StartPage))
        
        #WINDOW DRAW COMMANDS
        self.ppath_entry.grid(row = 1, column = 2, ipadx = 80, sticky = 'W', padx = 15, pady = 10)
        
        ppath_label.grid(row = 1, column= 1, sticky = 'W', pady = 10)
        
        back_button.grid(row=0, column=3)     
    
    #WINDOW FUNCTIONS
    def get_p_path(self):
        self.projectPath = str(tk.filedialog.askdirectory())+'/'
        self.ppath_str.set(self.projectPath)
        self.get_p_name()
        
app = GeotagTool() 
app.geometry('560x460')
app.mainloop()
