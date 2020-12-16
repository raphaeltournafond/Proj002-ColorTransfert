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
    b, g, r = cv2.split(image)
    b = np.asarray(b).reshape(-1)
    g = np.asarray(g).reshape(-1)
    r = np.asarray(r).reshape(-1)
    dots = direction[0] * b + direction[1] * g + direction[2] * r
    return dots


def sort_and_project(source, destination):
    d = get_random_direction()
    s_p = project_on_direction(d, source)
    d_p = project_on_direction(d, destination)
    s_i = np.argsort(s_p)
    d_i = np.argsort(s_p)
    return s_p, d_p, s_i, d_i, d


def convertToFloat(image):
    return np.float32(image)


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
            h, w, c = self.source.shape
            output = self.source.copy()
            t0 = time.time()
            for k in range(iteration):
                print(k)
                s_p, d_p, s_i, d_i, d = sort_and_project(output, self.destination)
                for i in range(len(s_p)):
                    diff = d_p[i] - s_p[i]
                    print(diff)
                    x = s_i[i] // w - 1
                    y = s_i[i] % w
                    b_c = output[x, y]
                    n_c = b_c + gamma * diff * d
                    output[x, y] = n_c
            cv2.imwrite('output.png', output)
            print(time.time()-t0)
            return True
        return False
