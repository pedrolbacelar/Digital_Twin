===============
Release Process
===============

This process describes the steps to execute in order to release a new version
of SimPy.


Preparations
============

#. Close all `tickets for the next version
   <https://gitlab.com/team-simpy/simpy/-/issues>`_.

#. Update the *minium* required versions of dependencies in :file:`setup.cfg`.
   Update the development dependencies in :file:`requirements-dev.txt`.

#. Run :command:`tox` from the project root. All tests for all supported
   versions must pass:

   .. code-block:: console

    $ tox
    [...]
    ________ summary ________
    py36: commands succeeded
    py37: commands succeeded
    py38: commands succeeded
    pypy3: commands succeeded
    docs: commands succeeded
    flake8: commands succeeded
    mypy: commands succeeded
    congratulations :)

#. Build the docs (HTML is enough). Make sure there are no errors and undefined
   references.

   .. code-block:: console

    $ make -C docs html

#. Check if all authors are listed in :file:`AUTHORS.txt`.

#. Update the change log (:file:`CHANGES.rst`). Only keep changes for the
   current major release in :file:`CHANGES.rst` and reference the history page
   from there.

#. Write a draft for the announcement mail with a list of changes,
   acknowledgements and installation instructions. Everyone in the team should
   agree with it.


Build and release
=================

#. Make *local* tag for new release. This tag will be pushed *later*, after
   checking the build artifacts. If anything is not right, this tag can be
   deleted and recreated locally *before* pushing to GitLab.

   .. code-block:: bash

      $ git tag -a -m "Tag a.b.c release" a.b.c


#. Test the build process. Build a source distribution and a `wheel
   <https://pypi.python.org/pypi/wheel>`_ package and test them:

   .. code-block:: bash

      $ python setup.py sdist bdist_wheel
      $ ls dist/
      simpy-a.b.c-py2.py3-none-any.whl simpy-a.b.c.tar.gz

   Try installing them:

   .. code-block:: bash

      $ rm -rf /tmp/simpy-sdist  # ensure clean state if ran repeatedly
      $ virtualenv /tmp/simpy-sdist
      $ /tmp/simpy-sdist/bin/pip install dist/simpy-a.b.c.tar.gz

   and

   .. code-block:: bash

      $ rm -rf /tmp/simpy-wheel  # ensure clean state if ran repeatedly
      $ virtualenv /tmp/simpy-wheel
      $ /tmp/simpy-wheel/bin/pip install dist/simpy-a.b.c-py2.py3-none-any.whl

   It is also a good idea to inspect the contents of the distribution files:

   .. code-block:: bash

      $ tar tzf dist/simpy-a.b.c.tar.gz

   .. code-block:: bash

      $ unzip -l dist/simpy-a.b.c-py2.py3-none-any.whl


#. Create or check your accounts for the `test server <https://test.pipi.org/>`_
   and `PyPI <https://pypi.org/>`_. Update your :file:`~/.pypirc` with your
   current credentials:

   .. code-block:: ini

      [distutils]
      index-servers =
          pypi
          testpypi

      [pypi]
      username = <your pypi username>

      [testpypi]
      repository = https://test.pypi.org/legacy/
      username = <your testpypi username>

#. Upload the distributions for the new version to the test server and test the
   installation again:

   .. code-block:: bash

      $ twine upload -r testpypi dist/simpy*a.b.c*
      $ pip install -i https://test.pypi.org/simple/ simpy

#. Check if the package is displayed correctly on the test PyPI:
   https://test.pypi.org/project/simpy/

#. Push tag for a.b.c release to GitLab. Upon successful build and test, the
   GitLab CI pipeline will deploy the tagged release to the production PyPI
   service.

   .. code-block:: bash

      $ git push origin master a.b.c

#. Check the status of the GitLab CI pipeline:
   https://gitlab.com/team-simpy/simpy/pipelines

#. Check if the package is displayed correctly on PyPI:
   https://pypi.org/project/simpy/

#. Finally, test installation from PyPI:

   .. code-block:: bash

      $ pip install -U simpy


Post release
============

#. Activate the `documentation build
   <https://readthedocs.org/dashboard/simpy/versions/>`_ for the new version.

#. Send the prepared release announcement to the `SimPy group
   <https://groups.google.com/forum/#!forum/python-simpy>`__.

#. Update `Wikipedia <http://en.wikipedia.org/wiki/SimPy>`_ entries.
