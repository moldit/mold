[![Build Status](https://secure.travis-ci.org/iffy/mold.png)](http://travis-ci.org/iffy/mold)

Docs: http://mold.rtfd.org/


# mold #

It really grows on you.

``mold`` is yet another configuration management tool.


Mold has 3 goals:

1. use standards

2. allow extensions to be written in the language best suited to the problem

3. stay out of the way -- provide *all* logging information.


# Quickstart #

## Install ##

The virtual environment isn't necessary, but is nice:

    virtualenv moldtest
    source moldtest/bin/activate
    pip install --upgrade Twisted Jinja2
    git clone https://github.com/iffy/mold.git mold.git
    cd mold.git
    python setup.py install

## Set up directory ##

XXX


# Running the tests #

After getting the code (see above):

    trial mold

# Building the docs #

Install ``sphinx``:

    pip install --upgrade sphinx


Build the docs

    cd docs && make html


The Mold Standard is separately maintained in the [moldspec project](https://github.com/iffy/moldspec).


