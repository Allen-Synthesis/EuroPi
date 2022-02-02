.PHONY: docs

clean_docs:
	$(MAKE) -C docs clean

docs:
	$(MAKE) -C docs html SPHINXOPTS="-W -n"

clean:
	find . -type d -name __pycache__ -print -exec rm -r {} \+

deploy_firmware: clean
	# requires rshell  https://github.com/dhylands/rshell
	 rshell rsync software/firmware /pyboard/lib
	 rshell 'repl ~ import machine ~ machine.soft_reset()~'

