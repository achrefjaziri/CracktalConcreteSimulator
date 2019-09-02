import numpy
import cv2


def kochenize(first_p, second_p, i):
    mu = 0.0
    sigma = numpy.pi/6.0 # 45°

    angle_check = False
    while angle_check == False:
        theta = numpy.random.normal(mu, sigma)
        if theta >= (-1.0 * numpy.pi / 4.0) and theta <= numpy.pi / 4.0:
            angle_check = True

    dist_x = second_p[0] - first_p[0]
    dist_y = second_p[1] - first_p[1]

    randomsplit_x = numpy.random.uniform(2,6)
    randomsplit_y = numpy.random.uniform(2,6)
    p1 = (first_p[0] + dist_x / randomsplit_x, first_p[1] + dist_y / randomsplit_y)
    p3 = (second_p[0] - dist_x / randomsplit_x, second_p[1] - dist_y / randomsplit_y)

    d = numpy.sqrt(pow(dist_x, 2.0) + pow(dist_y, 2.0))
    h = (d / 6) * numpy.tan(theta)

    p2 = (first_p[0] + dist_x / 2.0 + h * (second_p[1] - first_p[1]) / d,
          first_p[1] + dist_y / 2.0 - h * (second_p[0] - first_p[0]) / d)

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
            n1 = st + stepwidth//4
            n2 = st + 2*stepwidth//4
            n3 = st + 3*(stepwidth//4)
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
    # make sure to convert image to float otherwise numpy clips gradient to positive values.
    Grad = numpy.gradient(img.astype(float))
    # numpy gradient has y,x indexing
    GradX = Grad[0]
    GradY = Grad[1]

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
    Blur_scales = numpy.array((3, 5, 7, 9))  # need to be odd
    Random_Blur = Blur_scales[numpy.random.randint(0, len(Blur_scales))]
    img = cv2.GaussianBlur(img, (Random_Blur, Random_Blur), 0)
    # re-normalize the image to maximum range
    if img.max() != 0:
        img = 255 * (img.astype(float) / img.max())
    else:
        print ( "img.max in widen_line of fractalcracks.py is: " + str(img.max()) )

    return img


def construct_matrix(TOTALWIDTH, points):
    max_y = numpy.max(points[:, 1])
    min_x = numpy.min(points[:, 0])
    min_y = numpy.min(points[:, 1])

    img = numpy.zeros((TOTALWIDTH, TOTALWIDTH), numpy.uint8)

    pad = (TOTALWIDTH - (max_y - min_y)) / 2
    # TODO: think of function that varies 255 in height map across the length of the crack. Point set should be ordered.
    for pidx, p in enumerate(points[:-1]):
        strength = int((255/len(points))*(pidx+1)) # TODO: replace with something more complex
        cv2.line(img,
                 (int(p[0] - min_x), int(pad + p[1] - min_y)),
                 (int((points[pidx + 1, 0] - min_x)), int(pad + points[pidx + 1, 1] - min_y)),
                 (max(50, strength)), # at least 20% visibility
                 1)

    return img


def invert_matrix(img):
    img[:, :, 0:3] = 1 - img[:, :, 0:3]
    return img


def add_alpha_channel(img):
    # convert grayscale to BGRA
    img = numpy.repeat(img[:, :, numpy.newaxis], 4, axis=2)
    return img


def generate_fractal_cracks(TOTALWIDTH, DEPTH):
    points = koch(DEPTH, TOTALWIDTH)

    # construct a square matrix and fill it with lines between points
    img = construct_matrix(TOTALWIDTH, points)

    # random rotation and translation
    img = random_rotate(img)
    img = random_translate(img, TOTALWIDTH)

    # widen the line with a random gaussian blur
    img = widen_line(img)

    # normal calculation
    normals = calculate_normals(img)

    # normalize to 0-1 range as blender expects this range for RGBA
    img = img.astype(dtype=float) / 255.0

    # alpha channel addition
    img = add_alpha_channel(img)

    height_img = numpy.copy(img) # copy so it will not be inverted
    # invert the matrix so the crack is black and the background is white
    img = invert_matrix(img)

    # This returns ground truth, roughness, normal and height maps.
    return img, img, normals, height_img
