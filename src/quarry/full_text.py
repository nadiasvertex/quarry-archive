'''
Created on Dec 10, 2009

@author: Christopher Nelson
@summary: Uses Whoosh for full-text searching.
'''

import logging
import os

import whoosh.index as index
from whoosh.fields import *

class Indexer:
    def __init__(self, index_dir):
        self.index_dir = index_dir
                
        if not os.path.exists(index_dir):
            self._create_index()
        else:
            self.ix = index.open_dir(index_dir)        
        
        self.writer = None
        
    def _create_index(self):
        if not os.path.exists(self.index_dir):
            logging.info("creating index directory: %s", self.index_dir)
            os.makedirs(self.index_dir)
        
        logging.info("creating index")
        self.schema = Schema(path=STORED, subject=TEXT, from_addr=TEXT, to_addr=TEXT, content=TEXT)
        self.ix = index.create_in(self.index_dir, self.schema)
        
    def clear(self):
        "Clears out the previous index."
        del self.ix
        self._create_index() 
        
    def add_message(self, msg_id, msg):
        if not self.writer:
            self.writer = self.ix.writer()
                    
        logging.debug("index.add_message(%s)", msg_id)
        self.writer.add_document(path=unicode(msg_id), 
                                 subject=unicode(msg["Subject"]),
                                 from_addr=unicode(msg["From"]),
                                 to_addr=unicode(msg["To"]), 
                                 content=unicode(msg.get_payload()))
    
    def commit(self):
        self.writer.commit()
        
    def search(self, terms):
        s = self.ix.searcher()
        
        results = s.find("content", terms)
        logging.debug("matching full text search: %d", len(results))
        
        return results
                
    
