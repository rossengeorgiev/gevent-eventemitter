define HELPBODY
Available commands:

	make help       - this thing.
	make init       - install python dependancies
	make test       - run tests and coverage
	make pylint     - code analysis
	make build      - pylint + test

endef

export HELPBODY
help:
	@echo "$$HELPBODY"

init:
	pip install -r requirements.txt

test:
	coverage erase
	PYTHONHASHSEED=0 nosetests --verbosity 1 --with-coverage --cover-package=eventemitter

pylint:
	pylint -r n -f colorized eventemitter || true

build: pylint test

clean:
	rm -rf dist eventemitter.egg-info eventemitter/*.pyc

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel --universal

register:
	python setup.py register -r pypi

upload: dist register
	twine upload -r pypi dist/*
