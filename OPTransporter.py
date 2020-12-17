# Ambroise Decouttere & Raphael Tournafond
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
    d_i = np.argsort(d_p)
    return s_p, d_p, s_i, d_i, d


def get_new_projection(source, destination, gamma):
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

    LAB = True
    RGB = False

    def __init__(self, source_path, destination_path, use_lab=False):
        destination = cv2.imread(destination_path, cv2.IMREAD_COLOR)
        self.use_lab = use_lab
        if use_lab:
            destination = np.uint8(destination)
            self.destination = cv2.cvtColor(destination, cv2.COLOR_BGR2Lab)
        else:
            self.destination = np.float32(destination)
        source = cv2.imread(source_path, cv2.IMREAD_COLOR)
        if use_lab:
            source = np.uint8(source)
            source = cv2.cvtColor(source, cv2.COLOR_BGR2Lab)
        else:
            source = np.float32(source)
        h, w, c = self.destination.shape
        self.source = cv2.resize(source, (w, h), interpolation=cv2.INTER_LINEAR)

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
                print('\rIteration ' + str(k+1) + " out of " + str(iteration), end='', flush=True)
                diff = get_new_projection(self.source, output, gamma)
                output = np.add(output, diff)
            if self.use_lab:
                output = cv2.cvtColor(output.astype('uint8'), cv2.COLOR_Lab2BGR)
            cv2.imwrite('output.png', output)
            print()
            print("Elapsed time : ", time.time() - t0)
            return True
        return False
