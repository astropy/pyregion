

class PhysicalCoordinate(object):
    def __init__(self, header):
        try:
            cv1,cr1,cd1 = header["CRVAL1P"], header["CRPIX1P"], header[" CDELT1P"]
            cv2,cr2,cd2 = header["CRVAL2P"], header["CRPIX2P"], header[" CDELT2P"]
        except KeyError:
            self._physical_coord_not_defined = True
        else:
            self._physical_coord_not_defined = False
            
            self.cv1_cr1_cd1 = cv1,cr1,cd1
            self.cv2_cr2_cd2 = cv2,cr2,cd2
            self.cdelt = (cd1*cd2)**.5

    def to_physical(self, imx, imy):

        if self._physical_coord_not_defined:
            return imx, imy
        
        cv1,cr1,cd1 = self.cv1_cr1_cd1
        cv2,cr2,cd2 = self.cv2_cr2_cd2

        phyx = cv1 + (imx - cr1) * cd1
        phyy = cv2 + (imy - cr2) * cd2

        return phyx, phyy
    

    def to_image(self, phyx, phyy):

        if self._physical_coord_not_defined:
            return phyx, phyy

        cv1,cr1,cd1 = self.cv1_cr1_cd1
        cv2,cr2,cd2 = self.cv2_cr2_cd2

        imx = cr1 + (phyx - cv1) / cd1
        imy = cr2 + (phyy - cv2) / cd2

        return imx, imy



    def to_physical_distance(self, im_distance):

        if self._physical_coord_not_defined:
            return im_distance

        return im_distance*self.cdelt


    def to_image_distance(self, im_physical):

        if self._physical_coord_not_defined:
            return im_physical

        return im_physical/self.cdelt
    

