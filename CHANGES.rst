2.0 (unreleased)
----------------

API Changes
^^^^^^^^^^^

- ``pyregion.ds9_region_parser``

  - ``RegionParser.sky_to_image`` now calls its first parameter ``shape_list``
    instead of ``l``.

- ``pyregion.extern``

  - ``kapteyn_celestial`` removed.

-  ``pyregion.wcs_converter``

  - ``convert_to_imagecoord`` changed signature with the switch to Astropy
    and takes a ``Shape`` object.

  - ``convert_physical_to_imagecoord`` changed signature to accept a ``Shape``
    object.

- ``pyregion.wcs_helper``

  - All public methods and constants removed. They are replaced by Astropy,
    or replaced by private methods.


Other Changes and Additions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Astropy is used for all sky to image coordinate conversions.


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
