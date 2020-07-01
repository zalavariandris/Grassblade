import cv2
import numpy as np
class ThinPlateSpline:
	def __init__(self):
		self.tps=cv2.createThinPlateSplineShapeTransformer()

	def __call__(self, src, sourcePoints, targetPoints):
		""" reference: https://qiita.com/SousukeShimoyama/items/2bf8defb2d057bb8b742"""
		""" warp image """
		# prepare source and target points
		sshape = sourcePoints.reshape (1, -1, 2)
		tshape = targetPoints.reshape (1, -1, 2)
		matches = []
		for i in range(sshape.shape[1]):
			matches.append (cv2.DMatch (i, i, 0))

		self.tps.estimateTransformation(tshape.copy(), sshape.copy(), matches)
		return self.tps.warpImage(src)