## Building the Docs

The EuroPi documentation is built by [Sphinx](https://www.sphinx-doc.org) and deployed to
[GitHub Pages](https://pages.github.com) upon pushes to the ``main`` branch using
[GitHub Actions](https://github.com/features/actions).

In order to build the documentation locally you'll need to install Sphinx and the related dependencies in a virtual
environment. Our deployment uses Python 3.8. Install the requirements with:

```console
$ pip install -r docs/requirements.txt
```

You can then build the documentation locally with:

 ```console
 $ make docs
 ```

If successful, the built docs will end up in ``$EUROPI_DIR/docs/_build/html/``, and the docs can be viewed by opening
the [index.html file](index) in your browser.


If necessary, you can remove the generated docs with:

 ```console
 $ make clean_docs
 ```

 ### Windows

 Currently there is no root-level bat file equivalent to the Makefile. In order to build the documents on Windows,
 you'll have to execute the batch file in the docs dir directly:

```bat
> cd docs
> make.bat html
```

See the root level Makefile for details on the exact command and options we are using to execute Sphinx.

 ### Updating the doc build process requirements

Occasionally, a new requirement is added, or an existing requirement needs to be updated. To do so, first add or update
the requirement in ``docs/requirements.in``. Be sure that any newly added requirements are pinned to a specific version.
Then, regenerate the ``requirements.txt`` by executing the tool ``pip-compile`` in the ``docs`` directory:

```console
$ cd docs
$ pip-compile requirements.in
```

Both the ``requirements.in`` and the generated ``requirements.txt`` files should be committed.
