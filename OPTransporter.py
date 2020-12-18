# Ambroise Decouttere & Raphael Tournafond
#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Color transportation module OPTransporter.py

This module is designed for providing a simple to use color transporter.
By using this module you will be able to transport the color of a source image onto a destination image

This module require at least python 3.7, numpy and opencv:

`pip install numpy`
`pip install opencv-python`
"""

# Imports
import time
import numpy as np
import cv2

__author__ = "Ambroise Decouttere and Raphael Tournafond"
__copyright__ = "Copyright 2020, PROJ002-USMB"
__credits__ = ["Ambroise Decouttere", "Raphael Tournafond", "Jacques-Olivier Lachaud", "David Coeurjolly"]
__licence__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Ambroise Decouttere and Raphael Tournafond"
__email__ = "raphael.tournafond@etu.univ-smb.fr"
__status__ = "Beta"


def get_random_direction():
    """
    Generates a random 3D unit vector (direction) with a uniform spherical distribution
    Algo from http://stackoverflow.com/questions/5408276/python-uniform-spherical-distribution
    :return: direction
    """
    phi = np.random.uniform(0, np.pi * 2)
    costheta = np.random.uniform(-1, 1)

    theta = np.arccos(costheta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])


def project_on_direction(direction, image):
    """
    Project all the pixels of an image on a direction vector
    :param direction: 3D array
    :param image: opencv image
    :return: array of scalar products
    """
    # (R, G, B) . (Ur, Ug, Ub) = Rur + Gug + Bub
    b, g, r = cv2.split(image)
    b = np.asarray(b).reshape(-1)
    g = np.asarray(g).reshape(-1)
    r = np.asarray(r).reshape(-1)
    dots = direction[0] * b + direction[1] * g + direction[2] * r
    return dots


def sort_and_project(source, destination):
    """
    Project two images and sort their scalar product
    :param source: source image
    :param destination: destination image
    :return: two sorted array of scalar product sorted pixel indexes
    """
    d = get_random_direction()
    s_p = project_on_direction(d, source)
    d_p = project_on_direction(d, destination)
    s_i = np.argsort(s_p)
    d_i = np.argsort(d_p)
    return s_i, d_i


def get_new_projection(source, destination, gamma):
    """
    Project two images on a random direction and return a matrix containing the
    color direction of every channel of every pixel of the image.
    So adding this matrix to a 3 channels image move their color in the direction of the source image colors
    :param source: source (color) image
    :param destination: destination (shape) image
    :param gamma: fraction of the direction to move the pixels, used to let a chance to reorganise the pixels
    :return: a matrix of the same shape as the destination
    """
    d = get_random_direction()
    # Project the source and destination images on the random direction
    s_p = project_on_direction(d, source)
    d_p = project_on_direction(d, destination)
    # Sort the source and destination scalars lists and remember the destination permutation
    s_p = np.sort(s_p)
    order = np.argsort(d_p)
    d_p = np.array(d_p)[order]
    # Get the difference along the direction
    diff = np.subtract(s_p, d_p)
    # Compute a fraction of the vector length
    g_d = gamma * d
    # Apply the direction on each axis
    diff_x = np.multiply(diff, g_d[0])
    diff_y = np.multiply(diff, g_d[1])
    diff_z = np.multiply(diff, g_d[2])
    # Invert the permutation order
    inv = np.empty_like(order)
    inv[order] = np.arange(len(order), dtype=order.dtype)
    # Reorder the array according to the destination picture
    diff_x = np.array(diff_x)[inv]
    diff_y = np.array(diff_y)[inv]
    diff_z = np.array(diff_z)[inv]
    # Resize them into the image shape
    diff = np.dstack((diff_x, diff_y, diff_z))
    diff = np.reshape(diff, destination.shape)
    return diff


def convertToFloat(image):
    return np.float32(image)


class OPTransporter:
    """
    The transporter class
    """

    LAB = True
    RGB = False

    # Output file basename
    BASENAME = "output"

    def __init__(self, source_path, destination_path, use_lab=False, verbose=False):
        """
        OPTransporter constructor
        :param source_path: image path for the source (color) image
        :param destination_path: image path for the destination (shape) image
        :param use_lab: boolean defining if the lab color space is used (default : RGB)
        :param verbose: boolean defining if the verbose mode should be used (default : False)
        """
        destination = cv2.imread(destination_path, cv2.IMREAD_COLOR)
        self.use_lab = use_lab
        self.verbose = verbose
        if use_lab:
            if self.verbose:
                print("Using LAB color space")
            # Converting to uint8 is requested to go from RBG to LAB
            destination = np.uint8(destination)
            self.destination = cv2.cvtColor(destination, cv2.COLOR_BGR2Lab)
        else:
            # Using float32 increase the computation speed
            self.destination = np.float32(destination)
        source = cv2.imread(source_path, cv2.IMREAD_COLOR)
        if use_lab:
            source = np.uint8(source)
            source = cv2.cvtColor(source, cv2.COLOR_BGR2Lab)
        else:
            source = np.float32(source)
        h, w, c = self.destination.shape
        # Resize to the shape of the destination so we can use different shape of images
        # Also use the linear interpolation to do the resizing the the colors are still coherent with the source
        self.source = cv2.resize(source, (w, h), interpolation=cv2.INTER_LINEAR)
        if self.verbose:
            print("Color image (source) resized to h:" + str(h) + ", w:" + str(w) + ", c:" + str(c))

    def save_image(self, image, version):
        """
        Used to construct the output path according to the color space and the algorithm version
        :param image: image to save
        :param version: version of the algorithm used
        :return:
        """
        filename = self.BASENAME
        if self.use_lab:
            filename += "_lab"
        else:
            filename += "_rgb"
        filename += "_v" + str(version) + ".png"
        # Save the image using opencv
        cv2.imwrite(filename, image)

    def opt_transport_v1(self):
        """
        Do the color transportation using the association of the sorted scalar products
        of the source and destination images on a random direction
        :return: True if no error
        """
        t0 = time.time()
        if self.source.shape == self.destination.shape:
            h, w, c = self.source.shape
            s_i, d_i = sort_and_project(self.source, self.destination)
            output = self.destination.copy()
            for i in range(len(s_i)):
                s_i_i = s_i[i]
                d_i_i = d_i[i]
                # Retrieve the pixels positions in the matrix
                xd = d_i_i // w
                yd = d_i_i % w
                xs = s_i_i // w
                ys = s_i_i % w
                output[xd, yd] = self.source[xs, ys]
            if self.use_lab:
                # If LAB is used the output file needs to be converted to uint8
                output = cv2.cvtColor(output.astype('uint8'), cv2.COLOR_Lab2BGR)
            self.save_image(output, 1)
            if self.verbose:
                print("Elapsed time : ", time.time() - t0)
            return True
        if self.verbose:
            print("Error : Images are not of the same shape")
        return False

    def opt_transport_v2(self, gamma, iteration):
        """
        Sliced OT Color Transfer
        Do the color transportation by using a projection of colors in direction of the source image
        :param gamma: The fraction of the direction to use
        :param iteration: The number of iteration (projection in a random direction)
        :return: True if no error
        """
        t0 = time.time()
        if self.source.shape == self.destination.shape:
            output = self.destination.copy()
            for k in range(iteration):
                if self.verbose:
                    print('\rIteration ' + str(k+1) + " out of " + str(iteration), end='', flush=True)
                # Get a fraction of the projection of the destination in the source direction
                diff = get_new_projection(self.source, output, gamma)
                # Move the destination image towards the source colors in the random destination
                output = np.add(output, diff)
            if self.use_lab:
                output = cv2.cvtColor(output.astype('uint8'), cv2.COLOR_Lab2BGR)
            self.save_image(output, 2)
            if self.verbose:
                print()
                print("Elapsed time : ", time.time() - t0)
            return True
        if self.verbose:
            print("Error : Images are not of the same shape")
        return False
