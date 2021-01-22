import os
from ttk import *
from vtk import *
import datetime
import pandas as pd
import dill
from tqdm import tqdm
from GPSPhoto import gpsphoto

class Project:
    def __init__(self):
        pass
    
    def create(self, projectName, projectPath, config, videos=[],tracks=[]):

        #MANAGE CREATE PROJECT
        curr_files = os.listdir(projectPath)
        if projectName in curr_files:
            i = 0
            while projectName+'_'+str(i) in curr_files:
                i+=1
            projectName+='_'+str(i)
        os.mkdir(projectPath+'/'+projectName+'/')
        projectPath += '\\'+projectName+'\\'
        self.projectPath = projectPath
        del(projectName, projectPath)
        
        #MANAGE FILENAMES
        self.videos = videos
        self.tracks = tracks
        del(videos, tracks)
        
        #READ DATA INTO DATAFRAMES    
        framesDFs = []
        fps_list = []
        pointsDFs = []
        for video in self.videos: 
            framesDFs.append(getTimestamps(video, config))
            fps_list.append(getFps(video))
        for track in self.tracks:
            pointsDFs.append(trackExtract(track))
        self.framesDFs = framesDFs
        self.pointsDFs = pointsDFs
        self.fps_list = fps_list
        del(framesDFs, fps_list, pointsDFs)
        
    def match(self, time_col, lat_col, long_col, ele_col, maxtimediff, timeoffset):
        self.taggedDFs = []
        for pointsDF in self.pointsDFs:
            pointsDF = trackParse(pointsDF, time_col, lat_col, long_col, ele_col)
            for framesDF in self.framesDFs:          
                framesDF['adjTimestamp'] = [i+datetime.timedelta(hours=timeoffset) for i in framesDF['Timestamp']]
                video_ind = self.framesDFs.index(framesDF)
                curr_frame = None
                point_ind = 0
                
                for pointTime in pointsDF['Timestamp']:
                    timedelta = abs((pointTime - framesDF['adjTimestamp'][0]).total_seconds())
                    if timedelta <= maxtimediff:
                        frame_ind = 0
                        curr_frame = framesDF.loc[frame_ind, 'Frame']
                        break
                    point_ind+=1
                    
                if curr_frame is None:
                    for pointTime in tqdm(pointsDF['Timestamp']):
                        timedeltas = [abs((pointTime-frameTime).total_seconds()) for frameTime in framesDF['adjTimestamp']]
                        min_delta = min(timedeltas)
                        if min_delta <= maxtimediff:
                            frame_ind = timedeltas.index(min_delta)
                            curr_frame = framesDF.loc[frame_ind, 'Frame']
                            break
                        point_ind+=1

                if curr_frame is not None:
                        fps = self.fps_list[video_ind]
                        taggedDF = pointsDF
                        while frame_ind < len(framesDF['Timestamp']):
                            curr_frame = framesDF['Frame'][frame_ind]
                            taggedDF.loc[point_ind,'Frame'] = curr_frame
                            delta = (pointsDF['Timestamp'][point_ind] - pointsDF['Timestamp'][point_ind-1]).total_seconds()
                            frame_ind+=int(delta*fps)
                            point_ind+=1
                        taggedDF = taggedDF.dropna()
                        taggedDF = taggedDF.reset_index(drop=True)
                        self.taggedDFs.append(taggedDF)
                        self.framesDFs.pop(video_ind)
                        del(taggedDF,pointsDF,framesDF)
                        break  
                    
    def export(self, export_path):
        time = datetime.datetime.now()
        for ind in range(len(self.videos)):
            createFrames(self.videos[ind],self.projectPath,export_path,self.taggedDFs[ind])
        self.taggedDFs = pd.concat(self.taggedDFs, ignore_index=True)
        i = 0
        for frame in tqdm(self.taggedDFs['Frame']):
            photo = gpsphoto.GPSPhoto(export_path+frame)
            info = gpsphoto.GPSInfo((self.taggedDFs.loc[i, 'Latitude'], 
                                     self.taggedDFs.loc[i, 'Longitude']), 
                                    alt=int(self.taggedDFs.loc[i, 'Elevation']), 
                                    timeStamp=self.taggedDFs.loc[i, 'Timestamp'])
            photo.modGPSData(info, export_path+frame)
            i+=1

    def load(self, projectPath):
        pickle = ''
        for file in os.listdir(projectPath):
            print(file)
            if len(file.split('.')) == 2 and file.split('.')[1] == 'pkl':
                pickle = projectPath+'\\'+file
                break
        if pickle == '':
            return
        with open(pickle, 'rb') as f:
            data = dill.load(f)
        for atr in (projectPath, projectName, videos, tracks, framesDFs, pointsDFs, taggedDFs, fps_list):
            try:
                self.atr = data.atr
            except AttributeError: self.atr = None
        
    def save(self,project):
        with open(self.projectPath+self.projectName+'.pkl', 'wb') as f:
            dill.dump(project, f)
