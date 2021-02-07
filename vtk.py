# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 19:50:43 2020

@author: beck
"""
import cv2
from tqdm import *
import datetime
import dateparser
import os
import sys
import pandas as pd
import pytz
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from PIL import Image 
import numpy as np
import tempfile
import pytesseract
import imutils
import time
from GPSPhoto import gpsphoto
from threading import Thread

def firstFrame(video):
    if 'timestamp_frame' not in os.listdir(os.getcwd()):
        os.mkdir('timestamp_frame/')
    video_capture = cv2.VideoCapture(video)
    file = 'timestamp_frame/'+video+'_'+ str(0)+'.jpg'
    while(True):
            ret, frame = video_capture.read()
            if not ret:
                break
            im = frame
            break
    video_capture.release()
    PIL_image = Image.fromarray(im.astype('uint8'), 'RGB')
    return PIL_image

def formatFrame(image, LEFT = 50, TOP = 20, RIGHT = 250, BOTTOM = 90):
    image = image.crop((LEFT, TOP, RIGHT, BOTTOM))
    image = np.array(image.convert('RGB'))[:, :, ::-1].copy()
    image = imutils.resize(image, width=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return thresh

def getCreationDate(filename, config):
    if config == 'trident':
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
        image = formatFrame(firstFrame(video))
        data = pytesseract.image_to_string(thresh, lang='eng',config='--psm 6')
        data_str = str(data).split('\n')
        metadata = dateparser.parse(data_str[0]+ ' '+data_str[1])
    else:
        parser = createParser(filename)
        metadata = extractMetadata(parser).get('creation_date')
    return metadata

def getOffsets(file):
    #GET DELTA SECONDS FOR EVERY FRAME
    cap = cv2.VideoCapture(file)
    totalframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    offsets = [0]
    for i in range(totalframes-1):
        offsets.append(offsets[-1]+1000/fps)
    offsets = [datetime.timedelta(milliseconds=i) for i in offsets]
    return offsets

def getTimestamps(file, config):
    offsets = getOffsets(file)
    creationdate = getCreationDate(file, config)
    
    #CALCULATE TIMESTAMPS
    timestamps = [(creationdate+offset).replace(tzinfo = pytz.timezone('UTC')) for offset in offsets]
    
    #GENERATE FRAME NAMES
    frames = [file.split('/')[-1]+'_'+str(i)+'.jpg' for i in range(len(timestamps))]
    
    #EXPORT DATA AS CSV
    df = pd.DataFrame()
    df['Frame'] = frames
    df['Timestamp'] = timestamps
    return df

def getFps(file):
    cap = cv2.VideoCapture(file)
    return int(cap.get(cv2.CAP_PROP_FPS))

class Writer:
    def __init__(self, stream, export_path, taggedDF, parent, controller):
        self.taggedDF = taggedDF.reset_index()
        self.export_path = export_path
        self.taggedList = [self.taggedDF.loc[i,'Frame'] for i in range(len(self.taggedDF['Frame']))]
        self.frame_inds = [int(i.split('.')[1].split('_')[1]) for i in self.taggedList]
        self.parent = parent
        self.controller = controller
        self.stream = cv2.VideoCapture(stream)
        self.thread = Thread(target=self.write, args=())
        self.thread.setDaemon(True)
        
    def write(self):
        i = 0
        for frame_ind in self.frame_inds:
            self.stream.set(cv2.CAP_PROP_POS_FRAMES, frame_ind)
            (grabbed, frame) = self.stream.read()
            frame_path = self.export_path+self.taggedList[self.frame_inds.index(frame_ind)]
            cv2.imwrite(frame_path, frame)
            #ADD METADATA
            photo = gpsphoto.GPSPhoto(frame_path)
            info = gpsphoto.GPSInfo((self.taggedDF.loc[i, 'Latitude'], 
                                     self.taggedDF.loc[i, 'Longitude']), 
                                    timeStamp=self.taggedDF.loc[i, 'Timestamp'],
                                    alt=int(self.taggedDF.loc[i, 'Elevation']))
            photo.modGPSData(info, frame_path)
            self.parent.num+=1
            i+=1
            self.parent.e_status.set('Writing: '+str(self.parent.num)+'/'+str(self.parent.denom))
        self.stream.release()
        return
    
def createFrames(path, export_path, taggedDF, parent, controller):
    x = len(taggedDF)
    a = int(round(x/3))
    b = int(a*2)

    writer1 = Writer(path, export_path, taggedDF.iloc[:a], parent, controller)
    writer2 = Writer(path, export_path, taggedDF.iloc[a:b], parent, controller)
    writer3 = Writer(path, export_path, taggedDF.iloc[b:], parent, controller)
    
    writer1.thread.start()
    writer2.thread.start()
    writer3.thread.start()
    
    writer1.thread.join()
    writer2.thread.join()
    writer3.thread.join()
    
    parent.e_status.set('Done')
    