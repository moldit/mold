# Makefile for mold

.PHONY: help predoc clean test

test-with-coverage:
	$(MAKE) test
	coverage report --fail-under 100

test-sans-coverage:
	$(MAKE) test
	coverage report

test:
	pyflakes mold
	coverage run $$(which trial) mold functest
	coverage combine

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
