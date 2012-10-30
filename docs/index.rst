mold
===============================================================================

The idea is to use existing standards and to stay out of the way.  To that end,
the master and minion consist of normal scripts that read stdin and write to
stdout and stderr.


Master
===============================================================================

On a master machine, there will be a root master directory with a layout
similar to this:

.. code-block:: text

    master/
        certs/
        actors/
            


Minion
===============================================================================

On a minion machine, there will be a root minion directory with a layout
similar to this:

.. code-block:: text

    minion/
        certs/
        resources/
            file
            cron
            user


Resource scripts
-------------------------------------------------------------------------------

The executable scripts in ``minion/resources/`` each define the way a resource
is handled.  They must accept as a first command line argument the action to
be performed for that resource.  For instance, to inspect the state of the
file ``/tmp/foo`` you would do something like:

.. code-block:: bash

    $ echo '{"name":"/tmp/foo"}' | minion/resources/file inspect
    {
        "kind": "file",
        "name": "/tmp/foo",
        "exists": false
    }

And to make ``/tmp/foo`` conform to an expected state, you could do:

.. code-block:: bash

    $ cat | minion/resources/file conform
    {
        "name": "/tmp/foo",
        "user": "joe",
        "src": "http://www.example.com/foo.png"
    }
    ^D


Script interface
===============================================================================

All scripts are expected to use the standard input/output file
descriptors plus an optional logging control file descriptor (fd 3):

- STDIN (0): input comes from stdin.  Usually this will be a JSON 
  document.

- STDOUT (1): output is written to stdout.  Usually this will be
  a JSON document.

- STDERR (2): errors and debugging are written to stderr.  The script may 
  write to stderr and still be considered successful.  Success is 
  determined solely by the exit code.  Things written to stderr do NOT
  need to be JSON documents.

- LOGCTL (3): (XXX protocol to be determined).  Things written to this
  channel are passed through to the historian.  It is expected that this 
  channel will be used to upload log files, indicate steps in a process, 
  label stdin/out/err for each spawned process, etc...
  
  A script should not depend on this file descriptor being available.  So
  these two calls should have the same stdin, stdout, stderr and exit code:
  
  .. code-block:: bash
     
      /bin/bash some_script
      /bin/bash some_script 3>/dev/null

Scripts must return 0 to indicate success and any other exit code to indicate failure.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

