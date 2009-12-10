'''
Created on Dec 10, 2009

@author: Christopher Nelson
@summary: Ties together the message database and the fetcher
'''

from ConfigParser import SafeConfigParser

import common
import db
import fetch
import full_text
import logging, logging.handlers
import os
import pickle
import sys
import time

class Archive:
    def __init__(self, archive_config_file):
        self.config = SafeConfigParser()
        self.config.read(archive_config_file)
                
        self._load_state()
        
        self.db = db.MessageDb(self.config.get("archive", "name"))
        self.index = full_text.Indexer(os.path.join(self.home_dir, self.config.get("archive", "name")))
                                                       
        self.fetcher = fetch.Fetcher(username=self.config.get("email", "username"),
                                     password=self.config.get("email", "password"),
                                     server=self.config.get("email", "server"),
                                     port=self.config.getint("email", "port"),
                                     ssl=self.config.getboolean("email", "ssl"))
        
        self.fetcher.set_search_filter(self.config.get("archive", "filter"))
        
        
        # Set up logging                
        l = logging.getLogger('')        
        
        lh = logging.handlers.RotatingFileHandler(self.config.get("log", "name"),
                                                  maxBytes=self.config.getint("log", "rotate_size"),
                                                  backupCount=self.config.getint("log", "rotate_backups"))
        
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")        
        lh.setFormatter(formatter)
        lh.setLevel(eval("logging.{level}".format(level=self.config.get("log", "level").upper())))                   
        
        l.addHandler(lh)
        
        
    def _load_state(self):
        self.home_dir = common.get_home_dir()
            
        self.state_path = os.path.join(self.home_dir, "{name}.state".format(name=self.config.get("archive", "name")))
        if os.path.exists(self.state_path):
            self.state = pickle.load(open(self.state_path, "rb"))
        else:
            self.state = {}
            
    def _save_state(self):
        pickle.dump(self.state, open(self.state_path, "wb"))
        
    def update(self):
        """This method reads the message id's from the server and determines if it needs to download 
        more messages into it's database."""
        
        last_clock = time.time()
                
        logging.info("running archive update")
        # Get folders
        folders = self.fetcher.get_folder_names()        
        skip_folders = set([x.strip().lower() for x in self.config.get("archive", "skip_folders").split(",")])
        
        for folder in folders:
            if folder.lower() in skip_folders:
                logging.debug("skipping folder %s", folder)
                continue
            else:
                logging.debug("archiving folder %s", folder)
            
            # Get the ids of the messages for this folder
            if folder in self.state:
                last_id = int(self.state[folder])
                ids = [x for x in self.fetcher.get_message_ids(folder) if int(x) > last_id]
            else:
                ids = [x for x in self.fetcher.get_message_ids(folder)]

            # Get the messages
            for id in ids:
                msg = self.fetcher.get_message(folder, id)
                if msg:
                    self.db.save_message(folder, msg)
                    self.index.add_message(id, msg)
                    self.state[folder] = id
                    
                if time.time() - last_clock > 60:                    
                    # Commit our state once a minute
                    self.db.commit()         
                    self.index.commit()           
                    self._save_state()
                    logging.debug("database savepoint")
                    
                    last_clock = time.time()
               
                
        # Update our state
        self.db.commit()
        self._save_state()
