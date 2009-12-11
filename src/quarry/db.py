'''
Created on Dec 9, 2009

@author: Christopher Nelson
@summary: Database interface to store e-mail messages.
'''

import common
import email
import logging
import os
import sqlite3
import sys
import zlib

create_schema = """
CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, contents BLOB);
CREATE TABLE attributes(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value TEXT);
CREATE TABLE attribute_to_message(message_id INTEGER, attribute_id INTEGER);
CREATE TABLE meta(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value TEXT);

INSERT INTO meta(name, value) VALUES('version', '1.0');
"""

class MessageDb:
    "Stores e-mail messages"
    
    def __init__(self, name):
        self.name = name
        self._check_for_db()        
        self.config = common.get_config()
        
    def _create_db(self):
        logging.info("creating new message database")       
        self.con = sqlite3.connect(self.db_path)
        with self.con:
            cur=self.con.cursor()
            cur.executescript(create_schema)
            
    def _open_db(self):
        self.con = sqlite3.connect(self.db_path)
        cur=self.con.cursor()
        
        cur.execute("SELECT value FROM meta WHERE name=?", ("version", ))
        schema_version = cur.fetchone()[0]
        
        logging.debug("database schema version: %s", schema_version)
        # In the future we will do any necessary schema upgrades
        # right here.        
        
    def _check_for_db(self):
        self.home_dir = common.get_home_dir()
            
        self.db_path = os.path.join(self.home_dir, "messages.{name}.sqlite3.db".format(name=self.name))
        logging.debug("message database path: %s", self.db_path)
        
        if not os.path.exists(self.db_path):
            self._create_db()
        else:
            self._open_db()
            
    def recompress(self):
        "Recompresses the entire database with the compression level specified in the config file."
        
        logging.debug("db.recompress()")
        
        # Get the compression level
        compression_level = 6 if not self.config.has_option("archive", "compression_level") else self.config.getint("archive", "compression_level") 
        
        cur=self.con.cursor()
        cur.execute("SELECT id FROM messages")
        msg_ids = cur.fetchall()
        
        with self.con:
            for id, in msg_ids:
                logging.debug("decompress message id: %s", id)
                # Get message and decompress it
                cur.execute("SELECT contents FROM messages WHERE id=?", (id, ))
                msg = cur.fetchone()[0]
                try:
                    msg = zlib.decompress(msg)
                except zlib.error:
                    # We expect this here because the data may not have been compressed.                    
                    logging.exception("This exception may be okay if this is the first time you have run recompress, and this is an old database.")                                        
                
                # Compress the message with the new compression value
                logging.debug("compress message id: %s with level %d", id, compression_level)
                cur.execute("INSERT INTO messages(contents) VALUES(?)", (sqlite3.Binary(zlib.compress(msg, compression_level)), ))
            
    def save_message(self, folder, msg):
        """The message is a message object created from the email module that ships
        with Python 2.6+.  This is a mime-based object and lets us have useful information
        easily accessed with the message."""          
        
        logging.debug("db.save_message()")
        
        # Get the compression level
        compression_level = 6 if not self.config.has_option("archive", "compression_level") else self.config.getint("archive", "compression_level") 
        
        cur = self.con.cursor()
        
        # Save the message            
        cur.execute("INSERT INTO messages(contents) VALUES(?)", (sqlite3.Binary(zlib.compress(msg.as_string(), compression_level)), ))            
        msg_id = cur.lastrowid
        
        # Save the attributes separately so they are searchable
        for attr in msg.keys():
            cur.execute("INSERT INTO attributes(name, value) VALUES(?, ?)", (attr, msg[attr]))
            attr_id = cur.lastrowid
            # Associate the message and the attribute
            cur.execute("INSERT INTO attribute_to_message(message_id, attribute_id) VALUES(?,?)", (msg_id, attr_id))
            
        # Also store the folder name
        cur.execute("INSERT INTO attributes(name, value) VALUES(?, ?)", ("Folder", folder))
        attr_id = cur.lastrowid
        # Associate the message and the attribute
        cur.execute("INSERT INTO attribute_to_message(message_id, attribute_id) VALUES(?,?)", (msg_id, attr_id))
        
        # Close the cursor
        cur.close()

    def commit(self):
        """This MUST be called after one or more save_message() calls to make sure that the database
        does not rollback your changes.  If the program aborts, then your changes will be rolled back."""
        self.con.commit()
        
    def rollback(self):
        "Rolls back any changes made to the database since the last time commit() was called."
        self.con.rollback()
        
    def search(self, query):
        "This expects a query that selects one or more message ids.  The return will be message objects that match the query."
        cur = self.con.cursor()
        cur.execute(query)
        msg_ids = cur.fetchall()
        
        logging.debug("matching message count: %d", len(msg_ids))
        
        msgs = []
        for id in msg_ids:
            cur.execute("SELECT contents FROM messages WHERE id=?", id)
            msg = zlib.decompress(cur.fetchone()[0])
            msg = email.message_from_string(msg)
            
            for name, value in cur.execute("SELECT name, value FROM attributes as attr INNER JOIN attribute_to_message AS atm ON attr.id = atm.attribute_id AND atm.message_id=?", id):
                msg[name] = value
                
            msgs.append(msg)
            
        logging.debug("messages decoded: %d", len(msgs))
        return msgs
        
        