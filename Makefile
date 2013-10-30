# Makefile for mold

.PHONY: help predoc clean test

help:
	cat Makefile

clean:
	-find . -name "*.pyc" -exec rm {} \;
	-rm -rf _trial_temp
	-rm MANIFEST
	-rm -r build

# Generate the rst files from the json schema files

predoc:
	python extract_schema.py

test:
	coverage run $$(which trial) mold
	pyflakes mold
	coverage report --fail-under 100

coverage:
	-coverage run $$(which trial) mold
	coverage report --fail-under 100