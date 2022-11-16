.. _install:

************
Installation
************

Stable version
==============

Installing the latest stable version is possible either using pip or conda.

Using pip
---------

To install pyregion with `pip <http://www.pip-installer.org/en/latest/>`_
from `PyPI <https://pypi.python.org/pypi/pyregion>`_
simply run::

    pip install pyregion

Using conda
-----------

To install regions with `Anaconda <https://www.continuum.io/downloads>`_
from the `conda-forge channel on anaconda.org <https://anaconda.org/conda-forge/pyregion>`__
simply run::

    conda install -c conda-forge pyregion


Testing installation
--------------------

To check if your install is OK, install the test dependencies and run the tests:

.. code-block:: bash

    pip install "pyregion[test]"
    pytest --pyargs pyregion

Development version
===================

Install the latest development version from https://github.com/astropy/pyregion :

.. code-block:: bash

    git clone https://github.com/astropy/pyregion
    cd pyregion
    pip install -e .[test]
    pytest
    cd docs
    make html

Dependencies
============

Python 3.7+ is supported.

``pyregion`` has the following required dependencies:

* `Astropy <http://www.astropy.org/>`__ version 1.0 or later (which requires Numpy)
* ``pyparsing`` version 2.0 or later for parsing the DS9 region files
    * `Homepage <http://pyparsing.wikispaces.com/>`__
    * `PyPI page <https://pypi.python.org/pypi/pyparsing>`__

``pyregion`` has the following optional dependencies for plotting:

* `matplotlib <http://matplotlib.org/>`__

If you are using Astropy version 1.3 or later,
then you have ``astropy.visualization.wcsaxes``.
For older versions of Astropy, you have to install the separate package:
`wcsaxes <https://github.com/astrofrog/wcsaxes>`__

To work with the development version, you'll need Cython and a C compiler,
because the code to generate masks from regions is written in Cython.
