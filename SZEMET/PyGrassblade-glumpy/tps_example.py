import cv2
import numpy as np
import matplotlib.pyplot as plt




img = cv2.imread ('stinkbug.png', 1)
tps = cv2.createThinPlateSplineShapeTransformer()

k=0
while True:
	k+=1
	print(k)
	
	sshape = np.array ([[67, 90], [206, 90], [67, 228], [206, 227]], np.float32)
	tshape = np.array ([[64, 63], [205, 122], [67, 263], [207, 192]], np.float32)


	sshape+=np.random.uniform(-1, 1, sshape.shape)

	sshape = sshape.reshape (1, -1, 2)
	tshape = tshape.reshape (1, -1, 2)
	matches = list ()
	matches.append (cv2.DMatch (0, 0, 0))
	matches.append (cv2.DMatch (1,1,0))
	matches.append (cv2.DMatch (2, 2, 0))
	matches.append (cv2.DMatch (3, 3, 0))

	tps.estimateTransformation (tshape, sshape, matches)
	# ret, tshape  = tps.applyTransformation (sshape)

	out_img = tps.warpImage (img)
	cv2.imshow("hello", cv2.cvtColor(out_img, cv2.COLOR_BGR2RGB))
	key = cv2.waitKey(1)
	if key==27:
		break