# EuroPi Software

See the EuroPi firmware API documentation here: https://allen-synthesis.github.io/EuroPi/generated/europi.html

## Testing

In order to run the automated tests locally you'll need to install the development dependencies in a virtual
environment. Our deployment uses Python 3.8. Install the development requirements with:

```console
$ pip install -r software/requirements_dev.txt
```

You can then run the tests locally with:

 ```console
 $ pytest
 ```

 ### Updating the development requirements

Occasionally, a new requirement is added, or an existing requirement needs to be updated. To do so, first add or update
the requirements in ``software/requirements_dev.in``. Be sure that any newly added requirements are pinned to a specific
version. Then, regenerate the ``requirements_dev.txt`` by executing the tool ``pip-compile``:

```console
$ pip-compile software/requirements_dev.in
```

Both the ``software/requirements_dev.in`` and the generated ``software/requirements_dev.txt`` files should be committed.
