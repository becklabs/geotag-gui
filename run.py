import subprocess
import time
import sys
try:
    import tkinter
except ImportError:
    print('Could not find tkinter installation')
    print('Exiting in 5 sec...')
    time.sleep(5)
    sys.exit()
    
required = {'cv2':'opencv-python',
            'datetime':'datetime',
            'dateparser':'dateparser',
            'pandas': 'pandas',
            'pytz': 'pytz',
            'hachoir':'hachoir',
                'PIL':'Pillow',
                'numpy':'numpy',
                'pytesseract':'pytesseract',
                'imutils':'imutils',
                'dill':'dill',
                'gpxpy':'gpxpy',
                'GPSPhoto':'gpsphoto',
                'exifread':'exifread',
                'piexif':'piexif',
                'threading':'threading'
                }

for module in required:
    try:
        __import__(module)
    except ImportError as e:
        print('Missing Package: '+module)
        print('Attempting to install via pip...')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', required.get(module)])
        except subprocess.CalledProcessError:
            print('Failed to install '+ module)
            print('Exiting in 5 sec...')
            time.sleep(5)
            sys.exit()
        print('Installed '+module)
print('Starting App...')

from frontend import GeotagTool    
app = GeotagTool() 
app.geometry('560x460')
app.mainloop()