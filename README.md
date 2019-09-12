# Blender python basic scene generation:

The generate.py script generates concrete PBR materials from a set of albedo, metallic, roughness and normal maps.
An extra height map is used for displacement of mesh vertices. 

## Installing external modules

To install external python packages like scipy do the following:

1. Blender's python executable, e.g. python3.5m is located at 
~~~
/path/to/blender-version/python/bin/ 
~~~

2. Pip is not part of python and thus not part of blender's python. So use the version in /getpip/getpip.py and install it
~~~
/path/to/blender-version/python/bin/python3.5m /getpip/getpip.py
~~~
or download it from https://pip.pypa.io/en/stable/installing/ (state: 16/11/2017).
Note that this is independent of your system's pip. 

3. Install any packages with pip analogous to regular pip using blender's python version
~~~
/path/to/blender-version/python/bin/python3.5m /path/to/blender-version/python/bin/pip install package
~~~
Note that depending on your OS and Blender version the shortcut "pip" could not exist and will then be "pip3.5" or any other version suffix.

### Required external packages for this repository
* ```opencv-python```
* ```numpy==1.11```
* ```scipy==1.2```
* ```pillow```
* ```imageio```
* ```fnmatch```
* ```openexr```

~~~
sudo apt-get install libopenexr-dev
sudo apt-get install openexr
sudo apt-get install python3-dev

pip install OpenEXR --user or pip3 install OpenEXR --user
~~~
__Warning:__ OpenEXR did not properly install with python3.5m and is thus not usable within the blender python environment. See section "Converting EXR2NPY". 


## Running the code:
#### The concrete textures can be found in the [AEROBIConcreteTextures](https://git.ccc.cs.uni-frankfurt.de/AEROBI/AEROBIConcreteTextures) repository. You need to download/clone the repository into the current repository (i.e. such that the concrete_textures folder is at the top level)

The code was scripted in blender version 2.79 on a Linux OS. As this version introduced a large change to how PBR rendering works in Blender, previous versions are no longer supported! 

Ensure your are inside the repository folder in the command line. 

Run with:
~~~
/path/to/blender --background --python generate.py -- [--arguments]
~~~ 

Example:
MonoCamera:
~~~
/path/to/blender --background --python generate.py -- --num-images 10 --samples 10 --crack --resolution 1024
~~~
StereoCamera:
~~~
/home/timm/Blender/blender_2.79b/blender --background --python generate.py -- --num-images 10 --samples 10 --crack --resolution 1024 --stereo_camera
~~~

The above command will render and save 10 images (rendered with respective groundtruths and normalmaps) with crack into a /tmp folder, rendered at 10 samples and with a resolution of 1024x1024. For more options please check cmdparser.py in lib/ folder or use --help in the arguments.


## Convertion EXR2NPY
Find __exr2np.py__ in the __/utils__ directory. It contains example code for converting .exr files .npy.
