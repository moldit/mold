[![Build Status](https://secure.travis-ci.org/moldit/mold.png)](http://travis-ci.org/moldit/mold)

Docs: http://mold.rtfd.org/


# mold #

It really grows on you.


# What mold is #

``mold`` is yet another configuration management tool.


Mold goals:

1. use standards (like stdin, stdout, stderr) and already-made wheels (bash)

2. allow functions to be written in the language best suited to the problem

3. stay out of the way (e.g. provide raw logging information)

4. local should be easy to run

5. smallest code-print possible (forego features)

6. control-C should stop the process always

7. be verbose by default (hide verbosity in logs if you must)

8. telling > asking http://iffycan.blogspot.com/2013/10/tell-don-ask.html


# Quickstart #

Install it:

    pip install https://github.com/moldit/mold/tarball/master


# Building the docs #

Install ``sphinx``:

    pip install --upgrade sphinx


Build the docs

    cd docs && make html



