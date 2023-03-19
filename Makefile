.PHONY: docs

clean_docs:
	$(MAKE) -C docs clean
	rm -rf docs/generated

docs:
	$(MAKE) -C docs html SPHINXOPTS="-W -n"

clean:
	find . -type d -name __pycache__ -print -exec rm -r {} \+

deploy_firmware: clean
	# requires rshell  https://github.com/dhylands/rshell
	rshell -f scripts/deploy_firmware.rshell

deploy_configs:
	# requires rshell  https://github.com/dhylands/rshell
	rshell -f scripts/deploy_configs.rshell
