'''
Created on Dec 9, 2009

@author: cnelson
@summary: Used to fetch e-mail from an IMAP server.
'''
import email
import imaplib
import logging
import re

list_resp_re = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

class Fetcher:
    def __init__(self, **kw):
        self.username = kw.get("username", None)
        self.password = kw.get("password", None)
        self.server = kw.get("server", None) 
        self.use_ssl = kw.get("ssl", False)
        self.port = kw.get("port", imaplib.IMAP4_SSL_PORT if self.use_ssl else imaplib.IMAP4_PORT)
        
        self.search_filter="SEEN"
        
        if self.use_ssl:
            self.imap = imaplib.IMAP4_SSL(self.server, self.port)
        else:       
            self.imap = imaplib.IMAP4(self.server, self.port)
            
        self._login()
        
    def __del__(self):
        self._logout()
        
    def _login(self):
        logging.debug("logging in to '{server}' as '{user}'".format(server=self.server, user=self.username))
        self.imap.login(self.username, self.password)
        
    def _logout(self):
        self.imap.logout()
        
    def _get_folders(self, directory):
        logging.debug("_get_folders() on '%s'", directory)        
        result, folders = self.imap.list(directory)
        logging.debug("result: %s", result)
        
        out = {}
        
        for folder in folders:
            flags, delimiter, folder_name = list_resp_re.match(folder).groups()
            logging.debug("entering folder: %s", folder_name)
            logging.debug("   folder flags: %s", flags)            
            out[folder_name] = flags          
        
        return out
    
    def set_search_filter(self, filter):
        self.search_filter = filter
                
    def get_folder_names(self):        
        logging.debug("get_folder_names()")
        return self._get_folders("")
        
    def get_message_ids(self, folder):        
        logging.debug("get_message_ids() for %s", folder)
        
        try:
            self.imap.select(folder)
        except imaplib.IMAP4.error:
            logging.exception("Unable to select folder '%s'", folder)
            return None
        
        try:
            typ, msg_ids = self.imap.search(None, self.search_filter)
        except imaplib.IMAP4.error:
            logging.exception("Unable to search folder '%s' using criteria '%s'", folder, self.search_filter)
            return None
        
        logging.debug("type=%s", typ)
                
        if msg_ids:
            msg_ids = msg_ids[0].split(" ")
            logging.debug("number of matching messages=%d", len(msg_ids))
            return msg_ids
        else:
            logging.warning("no messages matched '%s' in folder '%s'", self.search_filter, folder)
            return None
        
    def get_message(self, folder, id):
        "Retrieves a message as an RFC822 entity and returns an email.message object."
        
        logging.debug("get_message(%s, %s)", folder, id)             
        
        logging.debug("selecting folder")
        try:
            self.imap.select(folder, readonly=True)
        except imaplib.IMAP4.error:
            logging.exception("Unable to select folder '%s'", folder)
            return None
        
        logging.debug("getting message")
        try:
            typ, msg_data = self.imap.fetch(id, '(RFC822)')
        except imaplib.IMAP4.error:
            logging.exception("Unable to read the specific message from the folder '%s'", folder)
            return None
            
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])         
                
        return msg
        
     
