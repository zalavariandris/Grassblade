import scipy.interpolate
import numpy as np
import cv2

class RbfWarp:
    def __call__(self, src, sourcePoints, targetPoints):
        height, width, channels = src.shape
        x = targetPoints[:,0]
        y = targetPoints[:,1]
        vectors = (sourcePoints-targetPoints) / (width, height)
        z1 = vectors[:,0]
        z2 = vectors[:,1]

        grid_x, grid_y = np.mgrid[0:1:height+1j, 0:1:width+1j]

        z1i = scipy.interpolate.Rbf(x/width,y/height,z1, epsilon=2)(grid_y, grid_x)
        z2i = scipy.interpolate.Rbf(x/width,y/height,z2, epsilon=2)(grid_y, grid_x)

        stvector = cv2.merge([z1i, z2i, np.zeros(z1i.shape)])

        # create fragCoord st map
        r, g = cv2.split(np.mgrid[0:1:width+1j, 0:1:height+1j].astype(np.float32).T)
        b = np.zeros(r.shape).astype(np.float32)
        st = cv2.merge([r,g,b])
        # plt.imshow( st+stvector )

        # deform src image with stmap
        mapx, mapy, mapz = cv2.split( (st+stvector)*(width, height, 1))
        
        return cv2.remap(src, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)