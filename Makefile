FLAGS   =
GAE_SDK = /usr/local/google_appengine
PYTHON  = PYTHONPATH=.:$(GAE_SDK) python

TESTS   = `find ./tests -name [a-z]\*_test.py`

default: test

test t:
	@for i in $(TESTS); do \
		echo $$i; \
		$(PYTHON) tests/handler_test.py $(FLAGS); \
	done

dist:
	$(PYTHON) setup.py $(FLAGS)
