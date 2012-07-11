Actors
======

There are three actors in ``mold``:

    1. Inspectors
    2. Prescribers (XXX to be defined)
    3. Conformers


Inspectors
----------

An *Inspector* observes the current state of resources.

It accepts an *Inspection document* conforming to the schema for the given resource type.  It returns an *Observation document* conforming to the schema for the given resource type.

For example, for inspecting the state of the file ``/tmp/foo`` a document such as this would be passed to the appropriate inspector:

.. code-block:: javascript

    {
        "kind": "file",
        "name": "/tmp/foo"
    }

The inspector will return an `Observation document`_ conforming to the file observation schema, such as:

.. code-block:: javascript

    {
        "kind": "file",
        "name": "/tmp/foo",
        "exists": true,
        "size": 3493,
        "sha": "c30a7f7531c41ec102fb5510d58166b502f68437",
        "user": "foo",
        "group": "bar",
        ...
    }

With ``mold``, you can use *Inspectors* from the command line (this is just one way to access *Inspectors*):

.. code-block:: bash

    mold inspect file /tmp/foo

Go ahead and try it!


Prescribers
-----------

XXX to be defined


Conformers
----------

A *Conformer* makes necessary changes to a machine in order to
conform to a prescribed state.

It accepts a *Prescription document* conforming to the schema for a given resource.  XXX what it returns is currently undefined.

For example, you might give it this prescription to ensure that the file at ``/tmp/foo`` exists and has attributes described:

.. code-block:: javascript

    {
        "kind": "file",
        "name": "/tmp/foo",
        "exists": true,
        "user": "jim",
        "group": "jimsgroup",
        "content": "This is the content of the file"
    }


