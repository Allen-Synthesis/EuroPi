.PHONY: docs

clean_docs:
	$(MAKE) -C docs clean

docs:
	$(MAKE) -C docs html SPHINXOPTS="-W -n"
