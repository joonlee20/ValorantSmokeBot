import os
import matplotlib.pyplot as plt
import numpy as np
import cv2 
import imutils
import math

RED_TUP = (1.0, 0.0, 0.0)
GREEN_TUP = (0.0, 1.0, 0.0)
BLUE_TUP = (0.0, 0.0, 1.0)
PURPLE_TUP = (0.6, 0.0, 1.0)

def euclidean(pt1, pt2):
	'''
	Helper function to calculate the euclidean distance between two points
	'''
	return math.sqrt((pt2[0] - pt1[0])**2.0 + (pt2[1] - pt1[1])**2.0)

def find_corners(img_name):
	'''
	Function that finds all corners in an image. Relies on cv2's corner Harris
	algorithm
	'''
	root= img_name.split(".")[0]
	ext = "." + img_name.split(".")[1]

	corner_list = []

	# This code taken from tutorial on detecting corners
	# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
	img = cv2.imread(img_name)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	gray = np.float32(gray)
	dst = cv2.cornerHarris(gray, 2, 3, 0.04)

	img[dst>0.01*dst.max()] = [0, 0, 255]
	# End cited code

	# For each corner, append to corner list
	for i in range(len(img)):
		for j in range(len(img[0])):
			if img[i][j][0] == 0 and img[i][j][1] == 0 and img[i][j][2] == 255:
				corner_list.append((i, j))

	# cv2.imshow('dst', img)
	# cv2.imwrite(root + '_corners' + ext, img)

	return corner_list

def clean_up_corners(corner_list, img_name):
	'''
	The corner Harris algorithm detects all corners, regardless of whether the
	corner is part of the map or part of a shape marking a point of interest. 
	This function removes all non-map corners.
	'''
	cleaned_corners_dict = {}
	
	wall_corner_list = []

	for corner in corner_list:
		if not next_to_point(corner, img_name):
			wall_corner_list.append(corner)

	# Sometimes, two different pixels close to each other are both marked as 
	# corners. Bucket the locations for corners so we don't have this issue
	for corner in wall_corner_list:
		x = int(corner[0] / 10) * 10
		y = int(corner[1] / 10) * 10

		key = (x, y)

		if key not in cleaned_corners_dict:
			cleaned_corners_dict[key] = corner

	ret_corners = list(cleaned_corners_dict.values())
	return list(cleaned_corners_dict.values())

def find_unique_colors(pixels, w, h):
	'''
	Debugging function used to find all unique colors in the image
	'''
	unique_colors = []
	for i in range(w):
		for j in range(h):
			pixel_tup = tuple(pixels[i * h + j])
			if pixel_tup not in unique_colors:
				unique_colors.append(pixel_tup)

	return unique_colors

def compare_color(pixel, color):
	'''
	Given a pixel in the image and a desired color, test if the color of the
	pixel matches that of the desired color
	'''
	same_color = True

	for i in range(3):
		if not(pixel[i] >= color[i] - 0.01 and pixel[i] <= color[i] + 0.01):
			same_color = False
	
	return same_color

# OBSOLETE FUNCTION REPLACED BY ONE BELOW
# def test_color(center, img_name):
# 	'''
# 	Given a pixel in an image, examine all pixels around the center pixel
# 	to see if they are part of a point of interest or not
# 	'''
# 	img = plt.imread(img_name)[:,:,:3]

# 	h,w,d = img.shape
# 	pixels = img.reshape((w * h, d))

# 	cX = center[0]
# 	cY = center[1]

# 	left = pixels[cY * w + cX - 1]
# 	right = pixels[cY * w + cX + 1]
# 	bottom = pixels[(cY + 1) * w + cX]
# 	top = pixels[(cY - 1) * w + cX]

# 	if compare_color(left, GREEN_TUP) and compare_color(right, GREEN_TUP) and compare_color(bottom, GREEN_TUP) and compare_color(top, GREEN_TUP):
# 		return "GREEN"
# 	elif compare_color(left, RED_TUP) and compare_color(right, RED_TUP) and compare_color(bottom, RED_TUP) and compare_color(top, RED_TUP):
# 		return "RED"
# 	else:
# 		return "UNKNOWN"

def check_pixels_around(pt, color, img_name):
	'''
	Given a pixel in an image, examine all pixels around the center pixel
	to see if they are part of a point of interest or not
	'''
	img = plt.imread(img_name)[:,:,:3]

	h,w,d = img.shape
	pixels = img.reshape((w * h, d))

	cX = pt[1]
	cY = pt[0]

	left = pixels[cY * w + cX - 1]
	right = pixels[cY * w + cX + 1]
	bottom = pixels[(cY + 1) * w + cX]
	top = pixels[(cY - 1) * w + cX]

	diag_nw = pixels[(cY - 1)* w + cX - 1]
	diag_ne = pixels[(cY - 1)* w + cX + 1]
	diag_sw = pixels[(cY + 1)* w + cX - 1]
	diag_se = pixels[(cY + 1)* w + cX + 1]

	if  (
			compare_color(left,    color) or
			compare_color(right,   color) or
			compare_color(bottom,  color) or
			compare_color(top,     color) or
			compare_color(diag_nw, color) or
			compare_color(diag_ne, color) or
			compare_color(diag_sw, color) or
			compare_color(diag_se, color)
		):
		return True
	else:
		return False

def next_to_point(center, img_name):
	return check_pixels_around(center, GREEN_TUP, img_name) or check_pixels_around(center, RED_TUP, img_name)

def find_centers(img_name):
	'''
	We assume the image passed in has two contours representing the two points
	of interest. This function detects the two centers of the contours
	'''
	green_center = (0, 0)
	red_center = (0, 0)

	root= img_name.split(".")[0]
	ext = "." + img_name.split(".")[1]

	img = cv2.imread(img_name)
	img_inv = cv2.bitwise_not(img)

	# This code taken from tutorial on finding contour centers
	# https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
	gray = cv2.cvtColor(img_inv, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
	
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	for c in cnts:
		# compute the center of the contour
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])

		# These two if statements added to tutorial code to check for centers
		# of two points of interest
		if test_color((cX, cY), img_name) == "GREEN":
			green_center = (cX, cY)
		elif test_color((cX, cY), img_name) == "RED":
			red_center = (cX, cY)

		# draw the contour and center of the shape on the image
		# cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
		# cv2.circle(img, (cX, cY), 3, (0, 0, 0), -1)
	# End cited code

	# cv2.imwrite(root + "_gray" + ext, img)

	return green_center, red_center

def smoke(img_name):
	'''
	Function that incorporates many of the other functions in this file to
	determine the best location to place a smoke on the map given two points
	of interest, one being the friendly position and the other being an enemy
	position.
	'''
	green_center, red_center = find_centers(img_name)
	redundant_corner_list = find_corners(img_name)
	corner_list = clean_up_corners(redundant_corner_list, img_name)
	dist_list = []

	# Compute all euclidean distances of corners from enemy
	for i in range(len(corner_list)):
		corner = corner_list[i]
		dist = round(euclidean(red_center, corner))
		dist_list.append(dist)

	nearest_corner_ind = 0
	second_nearest_corner_ind = 0

	# Compute which two corners are nearest to the enemy
	for i in range(len(corner_list)):
		if dist_list[i] < dist_list[nearest_corner_ind]:
			second_nearest_corner_ind = nearest_corner_ind
			nearest_corner_ind = i
		elif dist_list[i] < dist_list[second_nearest_corner_ind]:
			second_nearest_corner_ind = i

	nearest_corner = corner_list[nearest_corner_ind]
	second_nearest_corner = corner_list[second_nearest_corner_ind]

	# Smoke the point that is in the middle of the two nearest corners
	smoke_spot = (round((nearest_corner[1] + second_nearest_corner[1]) / 2), round((nearest_corner[0] + second_nearest_corner[0]) / 2))
	
	root= img_name.split(".")[0]
	ext = "." + img_name.split(".")[1]

	img = cv2.imread(img_name)

	# Draw the corners and the smoke spot on the map
	cv2.circle(img, smoke_spot, 10, (0, 0, 0), -1)
	cv2.circle(img, (nearest_corner[1], nearest_corner[0]), 10, (0, 0, 0), -1)
	cv2.circle(img, (second_nearest_corner[1], second_nearest_corner[0]), 10, (0, 0, 0), -1)
	
	# for corner in corner_list:
	# 	cv2.circle(img, (corner[1], corner[0]), 10, (0, 0, 0), -1)
	
	cv2.imwrite(root + "_smoked" + ext, img)

def invert(img_name):
	'''
	Simple function to invert an image
	'''
	root= img_name.split(".")[0]
	ext = "." + img_name.split(".")[1]
	
	img_name2 = root + "_inverted" + ext
	img = plt.imread(img_name)[:,:,:3]

	h,w,d = img.shape
	pixels = img.reshape((w * h, d))	

	pixels2 = np.zeros((w * h, d))
	
	for i in range(w):
		for j in range(h):
			pixels2[i * h + j] = 1 - pixels[i * h + j]

	np.clip(pixels2, 0, 1, out=pixels2)
	img2 = pixels2.reshape(img.shape) 
	plt.imsave(img_name2, img2, vmin=0, vmax=1)

	return img_name2

# invert("red_green_test.png")
# smoke("test_map_red_green_3.png")
# test_list = [(0, 0), (0, 1)]
# print(clean_up_corners(test_list))
# test_list = [(0, 4), (0, 2), (0, 6)]
# print(find_center(test_list))
# analyze2("purple_test_2.png")
# find_corners("test_map.png")
# print(find_center([(1,0, 0), (0, 1, 2)]))