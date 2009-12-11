'''
Created on Dec 10, 2009

@author: Christopher Nelson
'''

from ConfigParser import SafeConfigParser

import os
import sys

CONFIG=None

def get_config(**kw):
    global CONFIG
        
    if CONFIG==None:
        config_filename=kw.get("config_filename", None)
        if config_filename:
            CONFIG = SafeConfigParser()
            CONFIG.read(config_filename)
    
    return CONFIG    
        
def get_home_dir():
    if CONFIG and CONFIG.has_option("archive", "data_dir"):
        home_dir = CONFIG.get("archive", "data_dir")        
    else:
        if sys.platform == "win32":
            home_dir = os.path.join(os.environ["APPDATA"], "quarry")
        else:
            # Assume a unix platform
            home_dir = os.path.join(os.environ["HOME"], ".quarry")

    # Create the settings directory    
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
       
    return home_dir
    