.. _install:

************
Installation
************

Instructions
============

*pyregion* is registered in pypi, thus you can install it by ::

 pip install pyregion

This will also install pyparsing if not installed.

The source file can be downloaded directly from the following page.

* `PyPI page <https://pypi.python.org/pypi/pyregion>`__

To install with necessary dependency (pyparsing, see below), you may do

* in Python 2 ::

    pip install "pyparsing<2"
    pip install pyregion

* in Python 3 ::

    pip install "pyparsing>=2"
    pip install pyregion

The development version of pyregion can be found on the github page.

* `Download <http://github.com/astropy/pyregion>`__

To fetch the source
code by cloning my git repository for any recent bug fix. ::

    git clone git://github.com/astropy/pyregion.git
    cd pyregion
    python setup.py install

For any bug reporting or any suggestion, please use the github issue
tracker.

Dependencies
============

**Requirements**

Being based on pyparsing module, pyparsing need to be installed to use
pyregion. Optionally, you also requires pywcs
module installed for coordinate
conversion. Displaying regions is supported for matplotlib.  Some
example uses wcsaxes.

By default, pyregion build a filtering module, which requires a C compiler.
If you don't want, edit "setup.py" ::

  WITH_FILTER = False


pyparsing
---------
* REQUIRED
* `Homepage <http://pyparsing.wikispaces.com/>`__
* `PyPI page <https://pypi.python.org/pypi/pyparsing>`__
* pyparsing version >= 2.0 suports Python 3. But it seems that it does
  not support Python 2.
* For Python 2, install older version (v1.5.7).

astropy
-------
* OPTIONAL
* `Astropy <https://github.com/astropy/astropy/>`__

matplotlib
----------
* OPTIONAL
* `Homepage <http://matplotlib.org/>`__

wcsaxes
-------
* OPTIONAL
* `Homepage <https://github.com/astrofrog/wcsaxes>`__
