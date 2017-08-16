#!/bin/env python
# coding: utf-8
import numpy
import cv2

def kochenize(first_p, second_p, i):
    mu = 0.0
    sigma = numpy.pi/6.0 #45°

    AngleCheck = False
    while AngleCheck == False:
        theta = numpy.random.normal(mu, sigma)
        if theta >= (-1.0 * numpy.pi/4.0) and theta <= numpy.pi/4.0:
            AngleCheck = True

    dist_x = second_p[0] - first_p[0]
    dist_y = second_p[1] - first_p[1]

    randomsplit_x = numpy.random.uniform(2,6)
    randomsplit_y = numpy.random.uniform(2,6)
    p1 = (first_p[0] + dist_x / randomsplit_x, first_p[1] + dist_y / randomsplit_y)
    p3 = (second_p[0] - dist_x / randomsplit_x, second_p[1] - dist_y / randomsplit_y)

    d = numpy.sqrt(pow(dist_x, 2.0) + pow(dist_y, 2.0))
    h = (d / 6) * numpy.tan(theta)

    p2 = (first_p[0] + dist_x / 2.0 + h * (second_p[1] - first_p[1]) / d, first_p[1] + dist_y / 2.0 - h * (second_p[0] - first_p[0]) / d)

    return p1, p2, p3


def koch(depth, width):
    numlines = 4**depth + 1

    points = numpy.zeros((numlines, 2), dtype=float)
    points[0] = (-width/2., numpy.random.uniform(0.0, 0.5*width))
    points[-1] = (width/2., numpy.random.uniform(0.0, 0.5*width))
    stepwidth = numlines - 1

    for n in range(depth):
        segment = int((numlines-1)/stepwidth)
        for s in range(segment):
            st = s*stepwidth
            a = (points[st][0], points[st][1])
            b = (points[st+stepwidth][0], points[st+stepwidth][1])
            n1 = int(st + (stepwidth)/4)
            n2 = int(st + 2*(stepwidth)/4)
            n3 = int(st + 3*((stepwidth)/4))
            points[n1], points[n2], points[n3] = kochenize(a,b, depth)

        stepwidth /= 4
        stepwidth = int(stepwidth)
    return points

def random_rotate(img):
    cols, rows = img.shape
    RandomAngle = numpy.random.uniform(0, 180, 1)
    MRot = cv2.getRotationMatrix2D((cols / 2, rows / 2), RandomAngle, 1)
    img = cv2.warpAffine(img, MRot, (cols, rows))

    return img

def random_translate(img, TOTALWIDTH):
    cols, rows = img.shape
    RandomTranslation = numpy.random.uniform(-TOTALWIDTH / 2, TOTALWIDTH / 2)
    MTrans = numpy.float32([[1, 0, RandomTranslation], [0, 1, RandomTranslation]])
    img = cv2.warpAffine(img, MTrans, (cols, rows))

    return img

def calculate_normals(img):
    Grad = numpy.gradient(img)
    # numpy gradient has y,x indexing
    GradX = Grad[1]
    GradY = Grad[0]

    # usually *-1, but given that we want the normals to point inside the surface it is omitted
    NormX = GradX
    NormY = GradY
    NormZ = 1

    length = numpy.sqrt(NormX ** 2 + NormY ** 2 + NormZ ** 2)
    NormX = NormX / length
    NormY = NormY / length
    NormZ = NormZ / length

    Normals = numpy.concatenate([NormX[:, :, numpy.newaxis], NormY[:, :, numpy.newaxis], NormZ[:, :, numpy.newaxis]], 2)
    Normals = Normals * 0.5 + 0.5

    return Normals

def widen_line(img):
    Blur_scales = numpy.array((1, 3, 5))  # need to be odd
    Random_Blur = Blur_scales[numpy.random.randint(0, len(Blur_scales))]
    img = cv2.GaussianBlur(img, (Random_Blur, Random_Blur), 0)
    # re-normalize the image
    img = 255 * (img.astype(float) / img.max())
    return img

def construct_matrix(TOTALWIDTH, points):
    max_y = max(points[:, 1])
    min_x = min(points[:, 0])
    min_y = min(points[:, 1])

    img = numpy.zeros((int(TOTALWIDTH), int(TOTALWIDTH)), numpy.uint8)

    pad = (TOTALWIDTH - (max_y - min_y)) / 2
    for pidx, p in enumerate(points[:-1]):
        cv2.line(img,
                 (int(p[0] - min_x), int(pad + p[1] - min_y)),
                 (int((points[pidx + 1, 0] - min_x)), int(pad + points[pidx + 1, 1] - min_y)),
                 (255),
                 1)

    return img

def add_alpha_channel(img):
    # convert grayscale to BGRA
    img = numpy.repeat(img[:, :, numpy.newaxis], 4, axis=2)

    return img

def generate_fractal_cracks():
    TOTALWIDTH = 2048.
    DEPTH = 7

    points = koch(DEPTH, TOTALWIDTH)

    # construct a square matrix and fill it with lines between points
    img = construct_matrix(TOTALWIDTH, points)

    # widen the line with a random gaussian blur
    img = widen_line(img)

    # random rotation and translation
    img = random_rotate(img)
    img = random_translate(img, TOTALWIDTH)

    # normal calculation
    normals = calculate_normals(img)

    # alpha channel addition
    img = add_alpha_channel(img)

    return img, img, normals