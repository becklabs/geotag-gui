import os
from ttk import *
from vtk import *
import datetime
import pandas as pd
import dill
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
        
        #MISC
        self.config = config
        
    def match(self, time_col, lat_col, long_col, ele_col, offset, match_status):
        self.time_col = time_col
        self.lat_col = lat_col
        self.long_col = long_col
        self.ele_col = ele_col
        self.offset = offset
        match_status.set('Matching...')
        self.taggedDFs = []
        self.pointsDFs = [trackParse(df, time_col, lat_col, long_col, ele_col) for df in self.pointsDFs]
        
        #AUTOMATIC TIME OFFSET
        if offset == '':
            lower = 0
            upper = 0
            onehour = datetime.timedelta(hours = 1)
            framesDF = self.framesDFs[0].copy()
            pointsDF  = self.pointsDFs[0].copy()

            track_started_before = ((pointsDF['Timestamp'].iloc[0] - framesDF['Timestamp'].iloc[0]).total_seconds()) < 0
            if track_started_before:
                while (framesDF['Timestamp'].iloc[0] - pointsDF['Timestamp'].iloc[-1]).total_seconds() > 0:
                    lower+=1
                    pointsDF['Timestamp'] = [ts+onehour for ts in pointsDF['Timestamp']]
                upper = lower
                while (framesDF['Timestamp'].iloc[-1] - pointsDF['Timestamp'].iloc[0]).total_seconds() > 0:
                    upper+=1
                    pointsDF['Timestamp'] = [ts+onehour for ts in pointsDF['Timestamp']]
                upper -= 1
                possible_offsets = list(range(lower, upper+int(upper/abs(upper))))
            else:
                while (pointsDF['Timestamp'].iloc[0] - framesDF['Timestamp'].iloc[-1]).total_seconds() > 0:
                    lower-=1
                    pointsDF['Timestamp'] = [ts-onehour for ts in pointsDF['Timestamp']]
                upper = lower
                while (pointsDF['Timestamp'].iloc[-1] - framesDF['Timestamp'].iloc[0]).total_seconds() > 0:
                    upper-=1
                    pointsDF['Timestamp'] = [ts-onehour for ts in pointsDF['Timestamp']]
                upper += 1
                possible_offsets = list(range(upper, lower+1))
            
            f = self.pointsDFs[0].copy()
            for poffset in possible_offsets:
                pointsDF = f.copy()
                pointsDF['Timestamp'] = [ts+datetime.timedelta(hours = poffset) for ts in pointsDF['Timestamp']]
                if (pointsDF['Timestamp'].iloc[0] - framesDF['Timestamp'].iloc[-1]).total_seconds() > 0 or (framesDF['Timestamp'].iloc[0] - pointsDF['Timestamp'].iloc[-1]).total_seconds() > 0:
                    possible_offsets.remove(poffset)
            offset = possible_offsets[0]
            del(pointsDF, framesDF)
        
        #MAIN MATCHING ALGO
        offset = float(offset)
        offset = datetime.timedelta(hours = offset)
        for pointsDF in self.pointsDFs:
            pointsDF['Timestamp'] = [ts+offset for ts in pointsDF['Timestamp']]
            for framesDF in self.framesDFs:   
                
                #Check if matching is possible
                if (pointsDF['Timestamp'].iloc[0] - framesDF['Timestamp'].iloc[-1]).total_seconds() > 0 or (framesDF['Timestamp'].iloc[0] - pointsDF['Timestamp'].iloc[-1]).total_seconds() > 0:
                    continue
                
                video_ind = self.framesDFs.index(framesDF)
                track_ind = self.pointsDFs.index(pointsDF)
                fps = self.fps_list[video_ind]        

                initial_offset = (pointsDF['Timestamp'][0] - framesDF['Timestamp'][0]).total_seconds()
                point_ind = 0
                
                #Finds the index of the first GPS point after the video starts + difference in time between video start and said point
                if initial_offset < 0: # If video started after track started
                    while pointsDF['Timestamp'][point_ind] < framesDF['Timestamp'][0]:
                        point_ind+=1
                    point_delta = (pointsDF['Timestamp'][point_ind] - framesDF['Timestamp'][0]).total_seconds()
                
                #Selects the first gps point and sets difference between 
                if initial_offset > 0: # If video started before track started
                    print('video started before track')
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
        self.alltaggedDFs = pd.concat(self.taggedDFs, ignore_index=True)
        points = len(self.alltaggedDFs.index)
        match_status.set('Matched '+str(points)+ ' points')
        
    def export(self, export_path, e_status, controller):
        self.e_status = e_status
        self.denom = len(self.alltaggedDFs)
        self.num = 0
        for ind in range(len(self.videos)):
            createFrames(self.videos[ind],export_path,self.taggedDFs[ind], self, controller)
        
        del(self.e_status)
        
    def load(self, projectFile):
        with open(projectFile, 'rb') as f:
            data = dill.load(f)
        for atr in vars(data):
            if hasattr(data, atr):
                setattr(self, atr,getattr(data, atr))
        
    def save(self, projectPath, save_status):
        save_status.set('Saving...')
        #MANAGE PROJECT PATH
        curr_files = os.listdir(projectPath)
        if self.projectName in curr_files:
            i = 0
            while self.projectName+'_'+str(i) in curr_files:
                i+=1
            self.projectName+='_'+str(i)
        projectPath += self.projectName
        self.projectPath = projectPath
        del(projectPath)
        with open(self.projectPath+'.pkl', 'wb') as f:
            dill.dump(self, f)
        save_status.set('Done')
