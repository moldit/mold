# Makefile for mold

.PHONY: help predoc clean test

test-sans-coverage:
	pyflakes mold
	coverage run $$(which trial) mold
	coverage report

test:
	pyflakes mold
	coverage run $$(which trial) mold
	coverage report --fail-under 100

help:
	cat Makefile

clean:
	-find . -name "*.pyc" -exec rm {} \;
	-rm -rf _trial_temp
	-rm MANIFEST
	-rm -r build

coverage:
	-coverage run $$(which trial) mold
	coverage report --fail-under 100
