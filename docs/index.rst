mold
===============================================================================

Actor script interface
===============================================================================

All actor scripts are expected to use the standard input/output file
descriptors plus an optional logging control file descriptor (fd 3):

- STDIN (0): input for the actor comes from stdin.  Usually this will be a JSON 
  document.

- STDOUT (1): output from actor is written to stdout.  Usually this will be
  a JSON document.

- STDERR (2): errors and debugging are written to stderr.  The actor may 
  write to stderr and still be considered successful.  Success is 
  determined solely by the exit code.  Things written to stderr do NOT
  need to be JSON documents.

- LOGCTL (3): (XXX protocol to be determined).  Things written to this
  channel are passed through to the historian.  It is expected that this 
  channel will be used to upload log files, indicate steps in a process, 
  label stdin/out/err for each spawned process, etc...
  
  An actor script should not depend on this file descriptor being
  available.  So these two calls should behave the same:
  
  .. code-block:: bash
     
      /bin/bash actor-script
      /bin/bash actor-script 3>/dev/null

Actor scripts must return 0 to indicate success and any other exit code to indicate failure.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

