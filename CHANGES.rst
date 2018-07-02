2.1 (unreleased)
----------------

Other Changes and Additions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Support for angular units of 'd' and 'r' added.


2.0 (Oct 14, 2017)
------------------

This is a major new release of **pyregion**. There are some API changes
(listed below), but overall our goal was to keep backwards-compatibility
as much as possible while fixing code and installation issues
and refactor the internals to use Astropy more.

We note that we are developing a new **regions** package that is supposed
to become a superset of the functionality that is now in **pyregion** and
might be moved in the Astropy core package as **astropy.regions** in the future.
The main difference is that it represents regions as classes and uses Astropy
angle and coordinate objects, allowing for easier region-based analysis.
It is not feature complete, especially the DS9 region file parser is not a
complete replacement for **pyregion** yet. Still, you are encouraged to try
it out ( http://astropy-regions.readthedocs.io/ ), give feedback or even contribute.

For **pyregion**, the plan is to continue to do bugfixes and releases,
but to keep API changes to a minimum to avoid breaking existing scripts or pipelines.
If you have any questions or issues or requests, please open an issue in the **pyregion**
issue tracker on Github.


API Changes
^^^^^^^^^^^

- Removed ``rot_wrt_axis`` parameter from ``ShapeList`` and internal methods.

- ``ShapeList.as_imagecoord`` no longer accepts a ``asropy.wcs.WCS`` object. The
  conversion from pixel to image coordinates depends on the center of the
  image defined in ``astropy.io.fits.Header`` in order to agree with DS9.

- ``pyregion.ds9_region_parser``

  - ``RegionParser.sky_to_image`` now calls its first parameter ``shape_list``
    instead of ``l``.

- ``pyregion.extern``

  - ``kapteyn_celestial`` removed.

- ``pyregion.wcs_converter``

  - ``convert_to_imagecoord`` changed signature with the switch to Astropy
    and takes a ``Shape`` object.

  - ``convert_physical_to_imagecoord`` changed signature to accept a ``Shape``
    object.

- ``pyregion.wcs_helper``

  - All public methods and constants removed. They are replaced by Astropy,
    or replaced by private methods.


Other Changes and Additions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Astropy is used for all sky to image coordinate conversions. Science results may
  change, as `SIP <http://irsa.ipac.caltech.edu/data/SPITZER/docs/files/spitzer/shupeADASS.pdf>`_
  and `distortion paper <http://www.atnf.csiro.au/people/mcalabre/WCS/dcs_20040422.pdf>`_
  corrections are now used if present in the FITS file.

- Headers with more then 2 axes are now supported; only the celestial axes are
  used.

- Rotation angles are measured from the Y-axis instead of the X-axis, in order
  to agree with DS9 and potentially other astronomy software. This is a change
  from previous behavior, but only affects images with non-orthogonal axes.
  Previously, this behavior was controlled by the ``rot_wrt_axis`` parameter.

- Astropy 1.0 is now required.

- Shape conversion for multi-dimenstional HDU does not raise exceptions.

- Parser supports hex color in attributes

1.2 (Aug 11, 2016)
------------------

- https://pypi.org/project/pyregion/1.2/
- The changelog for this release is incomplete.
- We'll start collecting a complete changelog starting after this release.

- This release brings major changes to the code, docs and test setup,
  the package was converted to an Astropy affiliated package.
- There are only a few bugfixes and there should be no changes
  that break scripts or change results for pyregion users.


1.1.4 (Oct 26, 2014)
--------------------

- https://pypi.org/project/pyregion/1.1.4/
- The changelog for this release is incomplete.
- Change tag attribute from string to list of strings. [#26]

1.1 (March 15, 2013)
--------------------

- https://pypi.org/project/pyregion/1.1/
- No changelog available

1.0 (Sep 14, 2010)
------------------

- https://pypi.org/project/pyregion/1.0/
- First stable release
