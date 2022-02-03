## Building the Docs

The [EuroPi documentation](https://allen-synthesis.github.io/EuroPi/) is built by [Sphinx](https://www.sphinx-doc.org)
and deployed to [GitHub Pages](https://pages.github.com) upon pushes to the ``main`` branch using
[GitHub Actions](https://github.com/features/actions).

If you've made changes to the documentation you'll want to build the docs locally in order ot verify that the build runs
without errors and that your changes are rendered as you expect.

In order to build the documentation locally you'll need to install Sphinx and the related dependencies in a virtual
environment. Our deployment uses Python 3.8. Install the requirements with:

```console
$ pip install -r docs/requirements.txt
```

You can then build the documentation locally with:

 ```console
 $ make docs
 ```

If successful, the built docs will end up in ``docs/_build/html/``, and the docs can be viewed by opening
the ``index.html`` file in your browser.


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
the requirements in ``docs/requirements.in``. Be sure that any newly added requirements are pinned to a specific version.
Then, regenerate the ``docs/requirements.txt`` file by executing the tool ``pip-compile``:

```console
$ pip-compile docs/requirements.in
```
``pip-compile`` is part of the ``pip-tools`` package and can be installed with the other development requirements by
following the instructions in the [software README](../software/README.md).

Both the ``docs/requirements.in`` and the generated ``docs/requirements.txt`` files should be committed.
