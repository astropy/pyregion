
cdef extern from "stdio.h":
    pass

cdef extern from "stdlib.h":
    pass


# cdef extern from "geom2.h":
#     ctypedef struct Metric:
#         double g_x
#         double g_y

#     ctypedef struct RegionContext:
#         int (*init_metric)(Metric *m, double x0, double y0)

#     #cdef extern RegionContext metric_wcs



cimport  c_numpy
from c_numpy cimport npy_bool
cimport c_python


c_numpy.import_array()
#c_numpy.import_ufunc()

ctypedef int Py_ssize_t

class NotYetImplemented(Exception):
    pass

class RegionFilterException(Exception):
    pass



cdef struct Metric:
    double x0
    double y0
    double g_x
    double g_y


cdef int MetricSetOrigin(Metric *m, double x0, double y0):
    m.x0 = x0
    m.y0 = y0
    #m.g_x = 1.
    #m.g_y = 1.


cdef struct _RegionContext:
    int (*update_metric)(Metric *m)

cdef class RegionContext:
    #cdef int (*init_metric)(Metric *m, double x0, double y0)
    cdef _RegionContext c

    def __init__(self):
        pass

    cdef set_update_func(self, int (*update_metric)(Metric *m)):
        self.c.update_metric = update_metric


cdef int _update_metric_default(Metric *m):
    m.g_x = 1.
    m.g_y = 1.


cdef int _update_metric_wcs(Metric *m):
    cdef double theta
    theta = m.y0/180.*3.1415926;

    m.g_x = cos(theta)
    m.g_y = 1.



#cdef RegionContext metric_default
#metric_default._set(_init_metric_default)

cdef RegionContext metric_wcs
metric_wcs = RegionContext()
metric_wcs.set_update_func(_update_metric_wcs)



class BaseClassInitException(Exception):
    pass


cdef class RegionBase:
    #cdef double sin_theta
    #cdef double cos_theta

    cdef Metric m
    cdef RegionContext c

    #cdef __new__(self):
    #    MetricInit(&(self.m), xc, yc)

    def __init__(self):
        #selc.c = metric_default
        #self.update_context(metric_default)
        #MetricInit(&(self.m), x0, y0)
        raise BaseClassInitException()

    cdef update_metric(self):
        if self.c:
            self.c.c.update_metric(&(self.m))
        else:
            _update_metric_default(&(self.m))

    def set_context(self, RegionContext cnt):
        self.c = cnt
        self.update_metric()


    cdef metric_set_origin(self, double xc, double yc,
                           RegionContext cnt):

        MetricSetOrigin(&(self.m), xc, yc)
        if cnt:
            self.set_context(cnt)
        else:
            self.update_metric()



    def __invert__(self):
        return RegionNot(self)

    def __and__(self, RegionBase o):
        return RegionAnd(self, o)

    def __or__(self, RegionBase o):
        return RegionOr(self, o)

    cdef npy_bool _inside(self, double x, double y):
        return (0)

    def mask(self, img):
        """
        Create a mask ( a 2-d image whose pixel value is 1 if the
        pixel is inside the filter, otherwise 0). It takes a single
        argument which is numpy 2d array (or any python object with
        *shape* attribute) or a tuple of two integer representing the
        image shape.
        """

        cdef int l, nx, ny

        if hasattr(img, "shape"):
            shape = img.shape
        elif isinstance(img, tuple):
            shape = img

        if c_python.PySequence_Length(shape) != 2:
            raise RegionFilterException("shape of the inut image must be 2d: %s is given" % (str(shape)))

        ny = c_python.PySequence_GetItem(shape, 0)
        nx = c_python.PySequence_GetItem(shape, 1)

        return self._mask(nx, ny)

    cdef c_numpy.ndarray _mask(self, c_numpy.npy_intp nx, c_numpy.npy_intp ny):

        cdef c_numpy.npy_intp ny_nx[2]
        cdef c_numpy.ndarray ra
        cdef npy_bool *rd
        cdef int iy, ix

        ny_nx[0] = ny
        ny_nx[1] = nx

        ra = c_numpy.PyArray_EMPTY(2, ny_nx,
                                   c_numpy.NPY_BOOL, 0)

        rd = <npy_bool *> c_numpy.PyArray_DATA(ra)

        for iy from 0 <= iy < ny:
            for ix from 0 <= ix < nx:
                #rd[iy*nx + ix] = self._inside(i, j)
                # altenatively more optimized
                #rd[0] = self._inside(ix+1, iy+1) # +1 for (1,1) based..
                rd[0] = self._inside(ix, iy)
                rd = rd + 1

        return ra

    def inside1(self, double x, double y):
        """
        inside1(float, float) : returns True if the point (x,y) is inside the filter.
        """
        return self._inside(x, y)


    def inside(self, x, y):
        """
        inside(x, y) : given the numpy array of x and y, returns an
        array b of same shape, where b[i] = inside1(x[i], y[i])
        """
        cdef c_numpy.ndarray xa
        cdef c_numpy.ndarray ya
        cdef c_numpy.ndarray ra
        cdef double *xd
        cdef double *yd
        cdef npy_bool *rd
        cdef int i
        cdef int n
        #cdef c_numpy.npy_bool ((*_inside_ptr)(RegionBase, double ,double ))

        # FIX : check if two input has identical shape

        xa = c_numpy.PyArray_ContiguousFromAny(x, c_numpy.NPY_DOUBLE, 1, 0)
        ya = c_numpy.PyArray_ContiguousFromAny(y, c_numpy.NPY_DOUBLE, 1, 0)

        ra = c_numpy.PyArray_EMPTY(xa.nd, xa.dimensions,
                                   c_numpy.NPY_BOOL, 0)

        xd = <double *> c_numpy.PyArray_DATA(xa)
        yd = <double *> c_numpy.PyArray_DATA(ya)
        rd = <npy_bool *> c_numpy.PyArray_DATA(ra)

        n = c_numpy.PyArray_SIZE(xa)
        #_inside_ptr = self._inside
        for i from 0 <= i < n:
            #self._inside(xd[0], yd[0])
            #rd[i] = _inside_ptr(self, xd[i], yd[i])
            rd[i] = self._inside(xd[i], yd[i])
            #rd[i] = _inside_ptr(self, xd[i], yd[i])
            #print xd[i], yd[i], rd[i]
        return ra


#     def inside2(self, x, y):
#         cdef c_numpy.ndarray xa
#         cdef c_numpy.ndarray ya
#         cdef c_numpy.ndarray ra
#         cdef double *xd
#         cdef double *yd
#         cdef npy_bool *rd
#         cdef int i
#         cdef int ((*_inside_ptr)(RegionBase, double ,double ))
#         cdef int n

#         # This approach fails!

#         cobj = c_python.PyObject_GetAttrString(self, "__pyx_vtable__")

#         _inside_ptr = <int ((*)(RegionBase, double, double))>  c_python.PyCObject_AsVoidPtr(cobj)

#         xa = c_numpy.PyArray_ContiguousFromAny(x, c_numpy.NPY_DOUBLE, 1, 0)
#         ya = c_numpy.PyArray_ContiguousFromAny(y, c_numpy.NPY_DOUBLE, 1, 0)

#         ra = c_numpy.PyArray_EMPTY(xa.nd, xa.dimensions,
#                                    c_numpy.NPY_BOOL, 0)

#         xd = <double *> c_numpy.PyArray_DATA(xa)
#         yd = <double *> c_numpy.PyArray_DATA(ya)
#         rd = <npy_bool *> c_numpy.PyArray_DATA(ra)

#         n = c_numpy.PyArray_SIZE(xa)
#         for i from 0 <= i < n:
#             #self._inside(xd[0], yd[0])
#             #rd[i] = _inside_ptr(self, xd[i], yd[i])
#             rd[i] = self._inside(xd[i], yd[i])

#         return ra


cdef class RegionNot(RegionBase):
    """
    >>> r = RegionNot(r2)
    """
    cdef RegionBase child_region

    def __init__(self, RegionBase child_region):
        self.child_region = child_region

    cdef npy_bool _inside(self, double x, double y):
        return not(self.child_region._inside(x, y))


cdef class RegionList(RegionBase):
    cdef object child_regions

    def _check_type_of_list(self, kl):
        for k in kl:
            if not isinstance(k, RegionBase):
                raise TypeError("All elements should be subclass of RegionBase type: %s" % k)

    def __init__(self, *kl):
        self._check_type_of_list(kl)
        self.child_regions = list(kl)

    def __len__(self):
        return len(self.child_regions)

    def __getitem__(self, Py_ssize_t x):
        return self.child_regions[x]

    def __setitem__(self, Py_ssize_t x, RegionBase y):
        self.child_regions[x] = y

    def __delitem__(self, Py_ssize_t x):
        del self.child_regions[x]

    def __getslice__(self, Py_ssize_t i, Py_ssize_t j):
        return self.__class__(*self.child_regions[i:j])

    def __setslice__(self, Py_ssize_t i, Py_ssize_t j, x):
        self._check_type_of_list(y)
        self.child_regions[i:j] = x

    def __delslice__(self, Py_ssize_t i, Py_ssize_t j):
        del self.child_regions[i:j]

    def __contains__(self, RegionBase x):
        return x in self.child_regions

    def __repr__(self):
        return repr(self.child_regions)

    def asList(self):
        return self.child_regions


cdef class RegionOrList(RegionList):
    """
    >>> r = RegionOrList(r1, r2, r3, r4, ...)
    """
    cdef npy_bool _inside(self, double x, double y):
        cdef c_python.PyListObject *child_regions
        cdef int i, n

        child_regions = <c_python.PyListObject *> self.child_regions
        n = c_python.PyList_GET_SIZE(child_regions)
        for i from 0 <= i < n:
            if (<RegionBase> c_python.PyList_GET_ITEM(child_regions, i))._inside(x, y):
                return 1
        return 0


    def __repr__(self):
        return "Or"+repr(self.child_regions)


cdef class RegionAndList(RegionList):

    """
    >>> r = RegionAndList(r1, r2, r3, r4, ...)
    """

    cdef npy_bool _inside(self, double x, double y):
        cdef c_python.PyListObject *child_regions
        cdef int i, n

        child_regions = <c_python.PyListObject *> self.child_regions
        n = c_python.PyList_GET_SIZE(child_regions)
        for i from 0 <= i < n:
            if not (<RegionBase> c_python.PyList_GET_ITEM(child_regions, i))._inside(x, y):
                return 0
        return 1


    def __repr__(self):
        return "And"+repr(self.child_regions)


def RegionAnd(RegionBase region1, RegionBase region2):
    """
    >>> r = RegionAnd(reg1, reg2)
    """
    if isinstance(region1, RegionAndList):
        region1_list = region1.asList()
    else:
        region1_list = [region1]

    if isinstance(region2, RegionAndList):
        region2_list = region2.asList()
    else:
        region2_list = [region2]

    return RegionAndList(*(region1_list + region2_list))


def RegionOr(RegionBase region1, RegionBase region2):
    """
    >>> r = RegionOr(reg1, reg2)
    """
    if isinstance(region1, RegionOrList):
        region1_list = region1.asList()
    else:
        region1_list = [region1]

    if isinstance(region2, RegionOrList):
        region2_list = region2.asList()
    else:
        region2_list = [region2]

    return RegionOrList(*(region1_list + region2_list))


# cdef class RegionAnd_OLD(RegionBase):
#     cdef RegionBase child_region1
#     cdef RegionBase child_region2

#     def __init__(self, RegionBase child_region1, RegionBase child_region2):
#         self.child_region1 = child_region1
#         self.child_region2 = child_region2

#     cdef npy_bool _inside(self, double x, double y):
#         return (self.child_region1._inside(x, y)) & (self.child_region2._inside(x, y))


# cdef class RegionOr_OLD(RegionBase):
#     cdef RegionBase child_region1
#     cdef RegionBase child_region2

#     def __init__(self, RegionBase child_region1, RegionBase child_region2):
#         self.child_region1 = child_region1
#         self.child_region2 = child_region2

#     cdef npy_bool _inside(self, double x, double y):
#         return (self.child_region1._inside(x, y)) | (self.child_region2._inside(x, y))



# cdef class Transformed(RegionBase):
#     cdef double T11, T12, T21, T22
#     cdef double TI11, TI12, TI21, TI22
#     cdef double origin_x, origin_y
#     cdef RegionBase child_region

#     def __init__(self,
#                  RegionBase child_region,
#                  double T11, double T12, double T21, double T22,
#                  double origin_x, double origin_y):

#         self.child_region = child_region

#         self.T11 = T11
#         self.T12 = T12
#         self.T21 = T21
#         self.T22 = T22

#         # calculate inverse transform!
#         self.TI11 = T11
#         self.TI12 = T12
#         self.TI21 = T21
#         self.TI22 = T22

#         self.origin_x = origin_x
#         self.origin_y = origin_y


#     cdef int _transform(self, double x, double y, double *xp, double *yp):
#         cdef double x1, x2, y1, y2

#         x1 = x - self.origin_x
#         y1 = y - self.origin_y

#         # FIX IT!
#         x2 = x1
#         y2 = y1

#         xp[0] = x2 + self.origin_x
#         yp[0] = y2 + self.origin_y



#     cdef npy_bool _inside(self, double x, double y):
#         cdef double xp, yp
#         cdef npy_bool r

#         self._transform(x, y, &xp, &yp)
#         r = self.child_region._inside(xp, yp)

#         return r




cdef class Transform(RegionBase):
    cdef RegionBase child_region

    def __init__(self, RegionBase child_region):
        self.child_region = child_region


    property child:
        def __get__(self):
            return self.child_region

        #def __del__(self):
        #    del self.child_region


    cdef int _transform(self, double x, double y, double *xp, double *yp):
        xp[0] = x
        yp[0] = y

    cdef npy_bool _inside(self, double x, double y):
        cdef double xp, yp
        cdef npy_bool r

        self._transform(x, y, &xp, &yp)
        r = self.child_region._inside(xp, yp)

        return r


cdef extern from "math.h":
    double sin(double)
    double cos(double)
    double atan2(double, double)
    double fmod(double, double)
    double M_PI


cdef class Rotated(Transform):
    """
    Rotated

     >>> reg = Rotated(child_region, degree, origin_x, origin_y)


    Rotate the region by degree in anti-colockwise direction.
    """

    cdef double sin_theta
    cdef double cos_theta
    cdef double origin_x, origin_y

    def __init__(self, RegionBase child_region,
                 double degree, double origin_x, double origin_y):
        cdef double theta

        Transform.__init__(self, child_region)

        theta = degree / 180. * M_PI #3.1415926
        self.sin_theta = sin(theta)
        self.cos_theta = cos(theta)

        self.origin_x = origin_x
        self.origin_y = origin_y


    cdef int _transform(self, double x, double y, double *xp, double *yp):
        cdef double x1, x2, y1, y2
        cdef double st, ct, ox, oy

        st = self.sin_theta
        ct = self.cos_theta
        ox = self.origin_x
        oy = self.origin_y

        x1 = x - ox
        y1 = y - oy

        x2 =  ct*x1 + st*y1
        y2 = -st*x1 + ct*y1

        xp[0] = x2 + ox
        yp[0] = y2 + oy


cdef class Translated(Transform):
    """
    Translated region

     >>> Translate(child_region, dx, dy)
    """
    # translated region

    cdef double dx
    cdef double dy

    def __init__(self, RegionBase child_region,
                 double dx, double dy):

        Transform.__init__(self, child_region)

        self.dx = dx
        self.dy = dy

    cdef int _transform(self, double x, double y, double *xp, double *yp):
        xp[0] = x - self.dx
        yp[0] = y - self.dy






# Basic Shapes

cdef class Circle(RegionBase):
    """
    Circle

      >>> cir = Circle(xc, yc, radius, RegionContext c=None)

    """
    cdef double xc
    cdef double yc
    cdef double radius
    cdef double radius2

    #cdef Metric m


    cdef _set_v(self, double xc, double yc, double radius):
        self.xc = xc
        self.yc = yc
        self.radius = radius
        self.radius2 = radius*radius

    cdef _get_v(self):
        return (self.xc, self.yc, self.radius)


    def __init__(self, double xc, double yc, double radius,
                 RegionContext c=None):
        """
        """
        #if c:
        #    self.c = c
        self.metric_set_origin(xc, yc, c)
        self._set_v(xc, yc, radius)


    cdef npy_bool _inside(self, double x, double y):
        cdef double dist2

        dist2 = ((x-self.xc)*self.m.g_x)**2 + ((y-self.yc)*self.m.g_y)**2
        return (dist2 <= self.radius2)

    def __repr__(self):
        return "Circle(%f, %f, %f)" % (self.xc, self.yc, self.radius)



cdef class Ellipse(RegionBase):
    """
    Ellipse

      >>> shape = Ellipse(xc, yc, radius_major, radius_minor)

    """

    cdef double xc
    cdef double yc
    cdef double radius_major
    cdef double radius_major_2
    cdef double radius_minor
    cdef double radius_minor_2
    cdef double radius_major_2_radius_minor_2


    def __init__(self, double xc, double yc,
                 double radius_major, double radius_minor,
                 RegionContext c=None):

        # check inside
        # (x-xc)**2/radius_major**2 + (y-yc)**2/radius_minor**2 < 1
        # radius_minor**2*(x-xc)**2 + radius_major**2*(y-yc)**2 < (radius_major*radius_minor)**2

        self.xc = xc
        self.yc = yc
        self.radius_major = radius_major
        self.radius_minor = radius_minor
        self.radius_major_2 = radius_major**2
        self.radius_minor_2 = radius_minor**2
        self.radius_major_2_radius_minor_2 = self.radius_major_2 * self.radius_minor_2

        self.metric_set_origin(xc, yc, c)
        #MetricInit(&(self.m), xc, yc)


    cdef npy_bool _inside(self, double x, double y):
        cdef double dist2

        dist2 = self.radius_minor_2*(x-self.xc)**2 + self.radius_major_2*(y-self.yc)**2
        return (dist2 <= self.radius_major_2_radius_minor_2)

    def __repr__(self):
        return "Ellipse(%f, %f, %f, %f)" % (self.xc, self.yc, self.radius_major, self.radius_minor)



cdef class Box(RegionBase):
    """
    Box

    >>> shape = Box(xc, yc, width, height)

    """
    cdef double x1
    cdef double x2
    cdef double y1
    cdef double y2


    def __init__(self, double xc, double yc, double width, double height,
                 RegionContext c=None):
        cdef double halfwidth
        cdef double halfheight

        halfwidth = width*.5
        halfheight = height*.5

        self.x1 = xc - halfwidth
        self.x2 = xc + halfwidth
        self.y1 = yc - halfheight
        self.y2 = yc + halfheight

        self.metric_set_origin(xc, yc, c)
        #MetricInit(&(self.m), xc, yc)


    cdef npy_bool _inside(self, double x, double y):
        return (self.x1 <= x) & (x <= self.x2) & (self.y1 <= y) & (y <= self.y2)



cdef class Polygon(RegionBase):
    """
    Polygon

     >>> shape = Polygon(x, y)

     x, y : list of floats
    """
    cdef c_numpy.ndarray xa
    cdef c_numpy.ndarray ya
    #cdef object xa
    #cdef object ya

    cdef double *x
    cdef double *y
    cdef int n


    def __init__(self, x, y,
                 RegionContext c=None):
        self.xa = c_numpy.PyArray_CopyFromObject(x, c_numpy.NPY_DOUBLE, 1, 1)
        self.ya = c_numpy.PyArray_CopyFromObject(y, c_numpy.NPY_DOUBLE, 1, 1)

        self.n = c_numpy.PyArray_SIZE(self.xa)

        self.x = <double *> c_numpy.PyArray_DATA(self.xa)
        self.y = <double *> c_numpy.PyArray_DATA(self.ya)

        self.metric_set_origin(self.x[0], self.y[0], c)
        #MetricInit(&(self.m), )

    cdef npy_bool _inside(self, double x, double y):
        cdef int i, j
        cdef npy_bool r
        cdef double *xp
        cdef double *yp
        cdef double _t
        cdef double y_yp_i, y_yp_j


        j = self.n - 1
        r = 0
        xp = self.x
        yp = self.y


        # aopted from "http://alienryderflex.com/polygon/"
        # When the point is on the edge, the behavior seems undefined...
#         for i from 0 <= i < self.n:
#             if ((yp[i]<=y) & (yp[j]>y) | (yp[j]<=y) & (yp[i]>y)):
#                 _t = xp[i]+(y-yp[i])/(yp[j]-yp[i])*(xp[j]-xp[i])
#                 if (_t<x):
#                     r = not r
#             j=i

        #stable version, but would require more time
        for i from 0 <= i < self.n:
            y_yp_i = y - yp[i]
            y_yp_j = y - yp[j]

            if (y_yp_i == 0.) & (y_yp_j == 0.): # special case for horizontal line
                if (xp[i]-x)*(xp[j]-x) <= 0.:
                    return 1

            if ((0<=y_yp_i) & (0>y_yp_j) | (0<=y_yp_j) & (0>y_yp_i)):
                _t = xp[i]+y_yp_i/(yp[j]-yp[i])*(xp[j]-xp[i])
                if _t == x: # return true immediately if point over the poly-edge
                    return 1
                # but above does not catch horizontal line
                if (_t<x):
                    r = not r
            j=i



        return r


cdef class AngleRange(RegionBase):
    """
    AngleRange

      >>> shape = Ellipse(xc, yc, degree1, degree2)

    """

    cdef double xc
    cdef double yc
    cdef double degree1
    cdef double degree2
    cdef double radian1
    cdef double radian2


    def __init__(self, double xc, double yc,
                 double degree1, double degree2,
                 RegionContext c=None):

        self.xc = xc
        self.yc = yc
        self.degree1 = degree1
        self.degree2 = degree2

        # theta in [-pi, pi]
        self.radian1 = (fmod(degree1+180, 360.)-180)/180.*M_PI#3.1415926
        self.radian2 = (fmod(degree2+180, 360.)-180)/180.*M_PI#3.1415926
        #self.radian1 = (fmod(degree1, 360))/180.*M_PI#3.1415926
        #self.radian2 = (fmod(degree2, 360))/180.*M_PI#3.1415926
        #self.radian2 = (((degree2+180)%360.)-180)/180.*M_PI#3.1415926

        if self.radian2 < self.radian1:
            self.radian2 += 2.*M_PI #2*3.1415926

        self.metric_set_origin(xc, yc, c)


    cdef npy_bool _inside(self, double x, double y):
        cdef double dx, dy, theta

        dx = x - self.xc
        dy = y - self.yc

        theta = atan2(dy, dx)

        if theta < self.radian1:
            theta += 2.*M_PI
        return (theta < self.radian2)

    def __repr__(self):
        return "AngleRange(%f, %f, %f, %f)" % (self.xc, self.yc, self.degree1, self.degree2)
