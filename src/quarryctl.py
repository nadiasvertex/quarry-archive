'''
Created on Dec 10, 2009

@author: cnelson
@summary: Front end driver for the quarry module
'''

import email
import hashlib
import logging
import os

from optparse import OptionParser
from quarry.archive import Archive
from quarry.search import Engine

def archive(global_options, global_args):
    "Run the archive update operation."
    a=Archive(global_options.config_filename)
    a.update()
    
def search(global_options, global_args):
    "Run the search operation"
    parser = OptionParser()
    
    parser.add_option("-f", "--filter", dest="filters",
                      action="append", help="search using FILTER_EXPRESSION", metavar="FILTER_EXPRESSION")
    
    parser.add_option("-t", "--text", dest="text_search", default=None,
                      help="search full text for words", metavar="WORDS")
    
    parser.add_option("-e", "--export", dest="export", default=None,
                      help="export the e-mails to FOLDER", metavar="FOLDER")
    
    parser.add_option("-p", "--print", dest="display", default=False,
                      action="store_true", help="print a summary of the message to stdout")    
    
    (l_options, l_args) = parser.parse_args(global_args)
        
    e=Engine(global_options, l_options)
    msgs=e.search()
    
    if len(msgs)==0:
        logging.error("No messages matched the search criteria.")
    else:
        if l_options.export:
            logging.info("Writing messages to '%s' as flat mime files", l_options.export)
            if not os.path.exists(l_options.export):
                logging.warning("The export folder did not exist, so it was created.")
                os.makedirs(l_options.export)
                
            for msg in msgs:
                flat_msg = msg.as_string()
                digest = hashlib.sha1(flat_msg).hexdigest()
                open(os.path.join(l_options.export, digest + ".email"), "wt").write(flat_msg)
    
        if l_options.display:
            for msg in msgs:
                for attr in msg.keys():
                    print attr, ":", msg[attr]
                    
                print msg.get_payload()
                    
                print "\n\n"
                
            #print "Message display ends."
                

parser = OptionParser()
parser.disable_interspersed_args()

parser.add_option("-c", "--config", dest="config_filename",
                  help="use configfile FILE", metavar="FILE")

parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

# Setup logging in accord with the options on the command line
logging.basicConfig(level=logging.DEBUG if options.verbose else logging.ERROR)    

cmd_map = { "archive" : archive,
            "search"  : search }

cmd = args.pop(0).lower()

if cmd in cmd_map:
    cmd_map[cmd](options, args)
else:
    logging.critical("The command '{cmd}' is unknown to me.".format(**locals()))
    logging.critical("Valid commands are: %s", "\n\t".join(cmd_map.keys()))
     
