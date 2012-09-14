FLAGS   =
GAE_SDK = /usr/local/google_appengine
PYTHON  = PYTHONPATH=.:$(GAE_SDK) python

default: test

TESTS=`find ./tests -name [a-z]\*_test.py`
test t:
	@for i in $(TESTS); do \
		echo $$i; \
		$(PYTHON) $$i $(FLAGS); \
	done

dist:
	$(PYTHON) setup.py $(FLAGS)

VER=
update_example:
	appcfg.py --oauth2 update example/ -V $(VER) $(FLAGS)

clean:
	find . -name '*.pyc' -exec rm -f \{} ';'
	rm -rf dist
