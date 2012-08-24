# Makefile for mold

.PHONY: help predoc clean

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
