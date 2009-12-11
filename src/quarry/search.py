'''
Created on Dec 10, 2009

@author: Christopher Nelson
'''

import common
import db
import full_text
import logging
import os

class Engine:        
    def __init__(self, global_options, options):
        self.global_options=global_options
        self.options=options
        
        self.config = common.get_config(config_filename=global_options.config_filename)
        
        self.db = db.MessageDb(self.config.get("archive", "name"))
        self.index = full_text.Indexer(os.path.join(common.get_home_dir(), self.config.get("archive", "name")))
        
    def _filter_to_predicate(self, filter):
        field, op, value = filter.split(" ", 2)
        return "(attr.name LIKE '{field}' AND attr.value {op} '{value}')".format(**locals())
                
    def search(self):
        logging.debug("search()")
        
        if self.options.text_search:
            logging.debug("full text search")
            results = self.index.search(self.options.text_search.lower())   
            restrict_ids = [r["path"] for r in results]
            
            # If the full text search doesn't match anything, abort now.
            if not restrict_ids:
                return []
            
        else:
            restrict_ids = []     
        
        logging.debug("applying filters")
        
        query = """
SELECT DISTINCT atm.message_id 
FROM attribute_to_message as atm
     INNER JOIN attributes as attr ON atm.attribute_id = attr.id """
        
        # Create SQL JOIN predicates for filters
        if self.options.filters:
            preds = [ self._filter_to_predicate(filter) for filter in self.options.filters]        
            query += " AND " + " AND ".join(preds)            
        
        # Restrict results to message ids found by full text search
        if restrict_ids:
            query+="\nWHERE atm.message_id IN ({ids})".format(ids=",".join(restrict_ids))
            
        logging.debug("query:\n%s", query)
        
        return self.db.search(query) 
           
        
