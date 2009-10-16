import matplotlib.pyplot as plt
import pyregion

region = """
image
circle(10, 10, 8)
box(24, 18, 8, 6, 0)
"""

r = pyregion.parse(region)
m = r.get_mask(shape=(30,30))
plt.imshow(m, origin="lower", interpolation="nearest")
plt.show()

