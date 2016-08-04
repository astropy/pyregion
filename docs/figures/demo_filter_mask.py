import matplotlib.pyplot as plt
import pyregion

region = """
image
circle(100, 100, 80)
box(200, 150, 150, 120, 0)
"""

r = pyregion.parse(region)
mask_1or2 = r.get_mask(shape=(300, 300))

myfilter = r.get_filter()
mask_1and2 = (myfilter[0] & myfilter[1]).mask((300, 300))

plt.subplot(121).imshow(mask_1or2, origin="lower", interpolation="nearest")
plt.subplot(122).imshow(mask_1and2, origin="lower", interpolation="nearest")
plt.show()
