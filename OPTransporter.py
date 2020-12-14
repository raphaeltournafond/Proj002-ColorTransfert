# Ambroise Decouttere & Raphael Tournafond

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
    return x, y, z


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


class OPTransporter:

    def __init__(self, source_path, destination_path):
        self.source = cv2.imread(source_path, cv2.IMREAD_COLOR)
        self.destination = cv2.imread(destination_path, cv2.IMREAD_COLOR)

    def opt_transport_v1(self):
        h, w, channels = self.source.shape
        if self.source.shape == self.destination.shape:
            direction = get_random_direction()
            source_projection = project_on_direction(direction, self.source)
            destination_projection = project_on_direction(direction, self.destination)
            sorted_source_projection = sorted(source_projection, key=lambda tup: tup[0])
            sorted_destination_projection = sorted(destination_projection, key=lambda tup: tup[0])
            output = self.source.copy()
            for i in range(len(sorted_destination_projection)):
                d_pix = sorted_destination_projection[i]
                s_pix = sorted_source_projection[i]
                output[d_pix[1], d_pix[2]] = self.source[s_pix[1], s_pix[2]]
            cv2.imwrite('output.png', output)
            return True
        return False
