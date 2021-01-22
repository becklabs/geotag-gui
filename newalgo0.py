import os
from ttk import *
from vtk import *
import datetime
import pandas as pd
import dill
from tqdm import tqdm
from GPSPhoto import gpsphoto
import pytz

class Project:
    def __init__(self):
        pass
    
    def create(self, projectName, config, videos=[],tracks=[]):

        #MANAGE PROJECT NAME
        self.projectName = projectName
        del(projectName)
        
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
        
    def match(self, time_col, lat_col, long_col, ele_col, video_tz, track_tz):
        self.taggedDFs = []
        for pointsDF in self.pointsDFs:
            pointsDF = trackParse(pointsDF, time_col, lat_col, long_col, ele_col)
            pointsDF['Timestamp'] = [track_tz.localize(ts.replace(tzinfo=None), is_dst = None).astimezone(pytz.timezone('UTC')) for ts in pointsDF['Timestamp']]
            for framesDF in self.framesDFs:   
                framesDF['Timestamp'] = [video_tz.localize(ts.replace(tzinfo=None), is_dst = None).astimezone(pytz.timezone('UTC')) for ts in framesDF['Timestamp']]
                #Check if matching is possible
                if (pointsDF['Timestamp'].iloc[0] - framesDF['Timestamp'].iloc[-1]).total_seconds() > 0 or (framesDF['Timestamp'].iloc[0] - pointsDF['Timestamp'].iloc[-1]).total_seconds() > 0:
                    print('matching impossible')
                    continue
                
                video_ind = self.framesDFs.index(framesDF)
                track_ind = self.pointsDFs.index(pointsDF)
                fps = self.fps_list[video_ind]        

                initial_offset = (pointsDF['Timestamp'][0] - framesDF['Timestamp'][0]).total_seconds()
                point_ind = 0
                
                #Finds the index of the first GPS point after the video starts + difference in time between video start and said point
                if initial_offset < 0: # If video started after track started
                    while pointsDF['Timestamp'][point_ind] < framesDF['Timetamp'][0]:
                        point_ind+=1
                    point_delta = (pointsDF['Timestamp'][point_ind] - framesDF['Timestamp'][0]).total_seconds()
                
                #Selects the first gps point and sets difference between 
                if initial_offset > 0: # If video started before track started
                    point_delta = initial_offset
                    
                frame_ind = round(point_delta*fps)
                taggedDF = pointsDF
                matched_inds = []
                
                while frame_ind <= len(framesDF['Timestamp']):
                    curr_frame = framesDF['Frame'][frame_ind]
                    taggedDF.loc[point_ind,'Frame'] = curr_frame
                    delta = (pointsDF['Timestamp'][point_ind+1] - pointsDF['Timestamp'][point_ind]).total_seconds()
                    frame_ind+=round(delta*fps)
                    matched_inds.append(point_ind)
                    point_ind+=1
                    
                taggedDF = taggedDF.dropna()
                taggedDF = taggedDF.reset_index(drop=True)
                self.taggedDFs.append(taggedDF)
                self.framesDFs.pop(video_ind)
                pointsDF = pointsDF.drop(matched_inds)
                del(taggedDF,framesDF)
                    
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

    def load(self, projectFile):
        with open(projectFile, 'rb') as f:
            data = dill.load(f)
        for atr in (projectPath, projectName, videos, tracks, framesDFs, pointsDFs, taggedDFs, fps_list):
            try:
                self.atr = data.atr
            except AttributeError: self.atr = None
        
    def save(self, projectPath):
        
        #MANAGE PROJECT PATH
        curr_files = os.listdir(projectPath)
        if self.projectName in curr_files:
            i = 0
            while self.projectName+'_'+str(i) in curr_files:
                i+=1
            self.projectName+='_'+str(i)
        projectPath += '\\'+self.projectName
        self.projectPath = projectPath
        del(projectPath)
        
        with open(self.projectPath+'.pkl', 'wb') as f:
            dill.dump(project, f)
