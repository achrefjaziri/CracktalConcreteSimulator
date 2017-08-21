# Adapted from
# https://developer.blender.org/diffusion/B/browse/master/release/scripts/templates_py/background_job.py

import argparse

def parse(argv):

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
        "Run blender in background mode with this script:"
        "  blender --background --python " + __file__ + " -- [--options]"
    )

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument("-b", "--batch-size", default=8, type=int,
                        metavar="N", help="mini-batch size (default: 8)")
    parser.add_argument("-save", "--save-images", default=False, type=bool,
                        help="save all images to files on disc (default: False)")
    parser.add_argument("-res", "--resolution", default=4096, type=int,
                        metavar="R", help="image render resolution (default: 4096)")
    parser.add_argument("-tile", "--tile-size", default=256, type=int,
                        metavar="T", help="rendering tile size (default 256)")
    parser.add_argument("-imgs", "--num-images", default=100, type=int,
                        metavar="I", help="number of images to render (default 100)")
    parser.add_argument("-s", "--samples", default=6, type=int,
                        metavar="S", help="number of samples to render (default 6)")

    return parser.parse_args(argv)