# Ambroise Decouttere & Raphael Tournafond
import math
import time

import numpy as np
import cv2


def get_random_direction():
    """
    Generates a random 3D unit vector (direction) with a uniform spherical distribution
    Algo from http://stackoverflow.com/questions/5408276/python-uniform-spherical-distribution
    :return:
    """
    phi = np.random.uniform(0, np.pi * 2)
    costheta = np.random.uniform(-1, 1)

    theta = np.arccos(costheta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])


def project_on_direction(direction, image):
    # (R, G, B) . (Ur, Ug, Ub) = Rur + Gug + Bub
    projection = []
    h, w, channels = image.shape
    for i in range(h):
        for j in range(w):
            res = np.dot(direction, image[i, j])
            tup = (res, i, j)
            projection.append(tup)
    return projection


def sort_and_project(source, destination):
    direction = get_random_direction()
    source_projection = project_on_direction(direction, source)
    destination_projection = project_on_direction(direction, destination)
    sorted_source_projection = sorted(source_projection, key=lambda tup: tup[0])
    sorted_destination_projection = sorted(destination_projection, key=lambda tup: tup[0])
    return sorted_source_projection, sorted_destination_projection, direction


def convertToFloat(image):
    image = np.float32(image)
    return image * 1.0/255.0


class OPTransporter:

    def __init__(self, source_path, destination_path):
        source = cv2.imread(source_path, cv2.IMREAD_COLOR)
        self.source = convertToFloat(source)
        destination = cv2.imread(destination_path, cv2.IMREAD_COLOR)
        self.destination = convertToFloat(destination)

    def opt_transport_v1(self):
        if self.source.shape == self.destination.shape:
            sorted_source_projection, sorted_destination_projection, direction = sort_and_project(self.source, self.destination)
            output = self.source.copy()
            for i in range(len(sorted_destination_projection)):
                d_pix = sorted_destination_projection[i]
                s_pix = sorted_source_projection[i]
                output[d_pix[1], d_pix[2]] = self.source[s_pix[1], s_pix[2]]
            cv2.imwrite('output.png', output)
            return True
        return False

    def opt_transport_v2(self, gamma, iteration):
        if self.source.shape == self.destination.shape:
            output = self.source.copy()
            t0 = time.time()
            for k in range(iteration):
                print(k)
                sorted_source_projection, sorted_destination_projection, direction = sort_and_project(output, self.destination)
                for i in range(len(sorted_destination_projection)):
                    d_pix = sorted_destination_projection[i]
                    s_pix = sorted_source_projection[i]
                    diff = d_pix[0] - s_pix[0]
                    b_c = output[d_pix[1], d_pix[2]]
                    n_c = b_c + gamma * diff * direction
                    output[d_pix[1], d_pix[2]] = n_c
            cv2.imwrite('output.png', output * 255.0)
            t1 = time.time()
            print(t1-t0)
            return True
        return False
