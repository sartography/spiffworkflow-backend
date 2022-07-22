Spiffworkflow Backend
==========

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/spiffworkflow-backend.svg
   :target: https://pypi.org/project/spiffworkflow-backend/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/spiffworkflow-backend.svg
   :target: https://pypi.org/project/spiffworkflow-backend/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/spiffworkflow-backend
   :target: https://pypi.org/project/spiffworkflow-backend
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/spiffworkflow-backend
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/spiffworkflow-backend/latest.svg?label=Read%20the%20Docs
   :target: https://spiffworkflow-backend.readthedocs.io/
   :alt: Read the documentation at https://spiffworkflow-backend.readthedocs.io/
.. |Tests| image:: https://github.com/sartography/spiffworkflow-backend/workflows/Tests/badge.svg
   :target: https://github.com/sartography/spiffworkflow-backend/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/sartography/spiffworkflow-backend/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/sartography/spiffworkflow-backend
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Features
--------

* Backend API portion of the spiffworkflow engine webapp


Running Locally
---------------

* Install libraries using poetry:
.. code:: console
   $ poetry install

* Setup the database - currently requires mysql:
.. code:: console
   $ ./bin/recreate_db

* Run the server:
.. code:: console
   $ ./bin/run_server_locally


Requirements
------------

* Python 3.9+
* Poetry


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `MIT license`_,
*Spiffworkflow Backend* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.

.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT license: https://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _file an issue: https://github.com/sartography/spiffworkflow-backend/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://spiffworkflow-backend.readthedocs.io/en/latest/usage.html
