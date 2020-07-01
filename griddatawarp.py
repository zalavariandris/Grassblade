import scipy.interpolate
import cv2
import numpy as np

class GriddataWarp:
    def __call__(self, src, sourcePoints, targetPoints):
        height, width, channels = src.shape

        # interpolate STMap from vectors
        grid_x, grid_y = np.mgrid[0:1:height+1j, 0:1:width+1j]
        data = scipy.interpolate.griddata(targetPoints/(width, height), (sourcePoints-targetPoints)/(width, height), (grid_y, grid_x), method='cubic')
        
        stmap = np.zeros((data.shape[0], data.shape[1], 3))
        stmap[:,:,:2] = data        

        # create fragCoord st map
        r, g = cv2.split(np.mgrid[0:1:width+1j, 0:1:height+1j].astype(np.float32).T)
        b = np.zeros(r.shape).astype(np.float32)
        st = cv2.merge([r,g,b])

        # deform src image with stmap
        mapx, mapy, mapz = cv2.split( (st+stmap)*(width, height, 1))
        return cv2.remap(src, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)