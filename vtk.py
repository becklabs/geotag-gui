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
import pytesseract
import imutils

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

def splitPath(file):
    if '\\' in file:
        listfile = file.split('\\')
        filename = listfile[-1]
        folder = file[:len(file)-len(filename)]
    elif '/' in file:
        listfile = file.split('/')
        filename = listfile[-1]
        folder = file[:len(file)-len(filename)]
    else:
        filename=file
        folder = ''
    return folder,filename
        
        
def getTimestamps(file, config):
    offsets = getOffsets(file)
    creationdate = getCreationDate(file, config)
    
    #CALCULATE TIMESTAMPS
    timestamps = [creationdate+offset for offset in offsets]
    
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

def createFrames(file,projectPath,export_path,taggedDF):
    taggedList = [taggedDF.loc[i,'Frame'] for i in range(len(taggedDF['Frame']))]
    short_fnames = [int(i.split('.')[1].split('_')[1]) for i in taggedList]
    frames = {}
    if export_path not in os.listdir(projectPath):
        os.mkdir(projectPath+export_path)
    cap = cv2.VideoCapture(file)
    sys.stdout.flush()
    pbar = tqdm(total=len(taggedList))
    i=0
    with tqdm(total=len(taggedList)) as pbar:
        while(cap.isOpened()):
            frame_exists, frame = cap.read()
            if frame_exists:
                if i in short_fnames:
                    frames[taggedList[short_fnames.index(i)]] = frame
                    pbar.update(1)
                i+=1
            else:
                break
    cap.release()
    for i in tqdm(frames):
        cv2.imwrite(export_path+'/'+i,frames.get(i))