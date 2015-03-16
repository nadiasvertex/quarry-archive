# The Config File #

The first thing you need to do is setup a config file.  There is a sample config file called sample.config.  It looks like this:

```
[archive]
# The name will be used to differentiate the message and state databases
name=MYARCHIVE

# The path where you would like the e-mail archive stored.  This defaults
# to $HOME/.quarry on Unix and %APPDATA%/quarry on Windows.
#data_dir=/var/lib/email_archive

# Set the compression level.  This can be 1-9 with 1 being least compression and
# 9 being most.  The default is 6, which is a good balance between speed and packing
#compression_level=6

# This is the filter that will be used to pick messages to archive.  By default it will
# archive all mail that has been seen.  Consult the file imap_filters.txt for the full
# list of acceptable filter commands.  They are quite extensive.
filter=SEEN

# The folders to skip trying to archive. Make sure to specify them using LOWER CASE, because the
# filter deliberately drops the case when it does it's searching.  That way we don't have to worry
# about your client vs. server case on folder names.
skip_folders=contacts, journal, calendar, "junk e-mail", "deleted items", trash, "sync issues/conflicts", "sync issues/server failures"

[log]
# The filename to log to
name=/tmp/hp_archive.log

# Valid levels are CRITICAL, ERROR, WARNING, INFO, DEBUG
level=DEBUG

# The size of the file before it gets rotated in bytes
rotate_size=32768

# The number of backups of the log before it gets deleted
rotate_backups=5


[email]
# The e-mail server must be IMAP.  This program does not support POP or other
# mail server protocols at the moment.

username=user@domain.com
password=mypassword
server=mail.domain.com
port=993
ssl=true
```


You can accept most of the defaults, but you will need to change the NAME parameter under the "[archive](archive.md)" and "[log](log.md)" sections, as well as probably everything in the "[email](email.md)" section.


# Archiving Your E-Mail #

> Once you have a config file setup, you can run the archive command:

```
quarryctl.py -c my.config archive
```

> This will take a while.  Depending on the size of your e-mail inbox, it may also generate a _lot_ of data.  Make sure that your e-mail archive data\_dir is set to a filesystem that can handle it.

> The tool compresses the e-mail before saving it into the database, but the index and the attribute storage are _not_ compressed.

## The archive section ##

### data\_dir ###

By default your e-mails will be archived in your home directory, whatever that mean for your platform.  A subfolder called quarry or .quarry will be created.  You can redirect the data and indexes to a different place by over-riding data\_dir.

Note that you can have many databases and indexes in one directory, and they won't interfere with each other.

### filter ###

This is the IMAP filter used to decide which e-mails to archive.  You should consult the imap\_filters.txt file that comes with the distro, or look at the IMAP4 RFC for more detailed information on the possible options for IMAP search phrases.

### skip\_folders ###

There are some folders that you may not have any interest in archiving.  If that's the case, you may put them in here.  You should use lower case for all folder names.

## The log section ##

Defines some values of interest for the log file.

### name ###

This parameter indicates the name of the log file.

### rotate\_size ###

The log file will only grow to rotate\_size bytes, and will be rotated as soon as it overflows those bounds.

### rotate\_backups ###

There will be older copies of the file up to the count in rotate\_backups.  When a new log fills up, the oldest log copy will be deleted.