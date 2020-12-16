# Ambroise Decouttere & Raphael Tournafond
import sys
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


def get_new_projection(source, destination, gamma):
    h, w, c = source.shape
    d = get_random_direction()
    s_p = project_on_direction(d, source)
    d_p = project_on_direction(d, destination)
    s_p = np.sort(s_p)
    order = np.argsort(d_p)
    d_p = np.array(d_p)[order]
    diff = np.subtract(s_p, d_p)
    reordered_diff = np.empty((len(diff), 3))
    for i in range(len(diff)):
        reordered_diff[order[i]] = diff[i] * gamma * d
    res = np.reshape(reordered_diff, (h, w, 3))
    return res


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
            h, w, c = self.source.shape
            s_p, d_p, s_i, d_i, d = sort_and_project(self.source, self.destination)
            output = self.destination.copy()
            for i in range(len(s_p)):
                s_i_i = s_i[i]
                d_i_i = d_i[i]
                xd = d_i_i // w
                yd = d_i_i % w
                xs = s_i_i // w
                ys = s_i_i % w
                output[xd, yd] = self.source[xs, ys]
            cv2.imwrite('output.png', output)
            return True
        return False

    def opt_transport_v2(self, gamma, iteration):
        t0 = time.time()
        if self.source.shape == self.destination.shape:
            output = self.destination.copy()
            for k in range(iteration):
                print('\r' + str(k+1) + "/" + str(iteration), end='', flush=True)
                diff = get_new_projection(self.source, output, gamma)
                output = np.add(output, diff)
            cv2.imwrite('output.png', output)
            print()
            print(time.time() - t0)
            return True
        return False
