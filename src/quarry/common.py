'''
Created on Dec 10, 2009

@author: Christopher Nelson
'''

import os
import sys

def get_home_dir():
    if sys.platform == "win32":
       home_dir = os.path.join(os.environ["APPDATA"], "quarry")
    else:
       # Assume a unix platform
       home_dir = os.path.join(os.environ["HOME"], ".quarry")
    
    # Create the settings directory    
    if not os.path.exists(home_dir):
       os.mkdir(home_dir)
       
    return home_dir
    