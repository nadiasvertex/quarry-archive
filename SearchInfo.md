# Introduction #

quarry has a fairly sophisticated search capability.  It combines filtering and full-text search for maximum flexibility.

To use search run:

```
quarryctl.py -c my.config search 
```

# Filtering #

To specify a filter use the --filter paramter.

The filter expects arguments like this:

--filter="field operation value"

As an example, you could do this:

```
quarryctl.py -c my.config search --filter="subject LIKE %IA64%"
```

Which will find any messages with IA64 in the title.

Acceptable predicates are:

  * LIKE
  * GLOB
  * =
  * <
  * >

The search field name is the RFC822 header property.  Examples include:

  * From
  * To
  * Subject
  * Date

and many, many more.  Some e-mail servers and clients add their own headers, as do spam and antivirus checkers.

# Full Text Search #

To use full text search you specify the --text parameter.  quarry uses the Whoosh pure-python full text search engine.  It is not as fast as some, but it is very portable.

Currently quarry provides the following indexes:

  * subject
  * to\_addr
  * from\_addr
  * content

By default your search will look in the content index, which means the text of the e-mail message.  So, for example,

```
quarryctl.py -c my.config search --text="itanium python"
```

will find messages with itanium AND python in the content.  You can specify an index override by prefixing the index to the term.

```
quarryctl.py -c my.config search --text="itanium from_addr:anne"
```

This will find all messages with itanium in the body, and anne in the from field.

You can use parentheses to group terms, and you can use the operators:
  * AND
  * OR
  * NOT

```
quarryctl.py -c my.config search --text="itanium from_addr:anne (NOT from_addr:paul)"
```

# Using them Together #

When you use them together --text takes precedence over --filter.  The full text search indexes are first checked, and then the filter is applied to those results.  For example, if you wanted to get get messages with itanium in the text, sent from anne, with "commit" in the subject you could do this using only text:

```
quarryctl.py -c my.config search --text="itanium from_addr:anne subject:commit"
```

The same thing can be accomplished using filters AND text:

```
quarryctl.py -c my.config search --text="itanium" --filter="from LIKE %anne%" --filter="subject LIKE %commit%"
```

By default filters are joined with AND.


# Help #

You can get limited help by using the --help parameter after the command.