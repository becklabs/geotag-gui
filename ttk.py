# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 19:38:35 2020

@author: beck
"""

import pandas as pd
import gpxpy
import pytz
import dateparser
import sys
import datetime

def read_gpx(gps_filename):
    points = []
    with open(gps_filename,'r') as gpxfile:
        gpx = gpxpy.parse(gpxfile)
        for track in gpx.tracks:
            for segment in track.segments:
                sys.stdout.flush()
                for point in segment.points:
                    dict = {'timestamp': point.time,
                            'latitude': point.latitude,
                            'longitude': point.longitude,
                            'elevation': point.elevation
                            }
                    points.append(dict)
        gps_telem = pd.DataFrame.from_dict(points)
    return gps_telem

def trackExtract(gps_filename):
    ext = gps_filename.split('/')[-1].split('.')
    if ext[1] == 'csv':
        gps_telem = pd.read_csv(gps_filename)
    if ext[1] == 'gpx':
        gps_telem = read_gpx(gps_filename)
    return gps_telem

def trackParse(data, time_col, lat_col, long_col, ele_col, track_tz):
    gps_telem = pd.DataFrame()
    gps_telem['Timestamp'] = [track_tz.localize(dateparser.parse(data.loc[i,time_col])).astimezone(pytz.timezone('UTC')) for i in range(len(data[time_col]))]
    print(gps_telem['Timestamp'])
    gps_telem['Latitude'] = data[lat_col]
    gps_telem['Longitude'] = data[long_col]
    if ele_col != 'None':
        gps_telem['Elevation'] = data[ele_col]
    return gps_telem