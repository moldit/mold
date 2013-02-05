[![Build Status](https://secure.travis-ci.org/iffy/mold.png)](http://travis-ci.org/iffy/mold)

Docs: http://mold.rtfd.org/


# mold #

It really grows on you.


# What mold is #

``mold`` is yet another configuration management tool.


Mold has 3 goals:

1. use standards (like stdin, stdout, stderr and JSON)

2. allow functions to be written in the language best suited to the problem

3. stay out of the way (e.g. provide all raw logging information)


# Quickstart #

Install it:

    pip install -e git://github.com/moldit/mold.git

Create a minion:

    mold create-minion /tmp/minion

Inspect the state of a file:

    echo '{"path": "/tmp/minion"}' | /tmp/minion/resources/file inspect

And see the state of the resource:

    {"kind": "file", "group": "wheel", "ctime": 1351889197, "exists": true, "perms": "0557", "filetype": "dir", "mtime": 1351889197, "owner": "moldit", "path": "/tmp/minion", "atime": 1351896286}


# Running the tests #

After getting the code (see above):

    trial mold

# Building the docs #

Install ``sphinx``:

    pip install --upgrade sphinx


Build the docs

    cd docs && make html


The Mold Standard is separately maintained in the [moldspec project](https://github.com/iffy/moldspec).


