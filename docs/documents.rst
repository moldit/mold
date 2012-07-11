State Documents
===============

Each resource has three state documents:

    1. *Inspection document*
    2. *Observation document*
    3. *Prescription document*

All documents are JSON serializable and conform to resource-specific `Resource Schema Definitions`_.


Inspection document
-------------------

An inspection document is used by *Inspectors*.  For example, a ``file`` inspection document looks like this:

.. code-block:: javascript

    {
        "kind": "file",
        "name": "/etc/hosts"
    }


Observation document
--------------------

Observation documents are returned as the result of inspections.  For example, a ``file`` observation document might look like this:

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


Prescription document
---------------------

Prescription documents are given to `Conformers`_ which will make the changes necessary to match the prescription.  For example, if we want to make sure the file ``/tmp/foo`` does not exist, we could prescribe that with this document:

.. code-block:: javascript

    {
        "kind": "file",
        "name": "/tmp/foo",
        "exists": false
    }


