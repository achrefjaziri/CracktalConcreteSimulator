# Blender python basic scene generation

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
* ```numpy```
* ```scipy```
* ```pillow```
* ```fnmatch```

## Running the code:

#### The code was scripted in blender version 2.79 on a Linux OS. As this version introduced a large change to how PBR rendering works in Blender, previous versions are no longer supported! 

Ensure your are inside the repository folder in the command line. 

Run with:
~~~
/path/to/blender --background --python generate.py -- [--arguments]
~~~ 

Example:
~~~
/path/to/blender --background --python generate.py -- --save-images True --num-images 10 --samples 10 --crack True --resolution 1024
~~~

The above command will render and save 10 images (rendered with respective groundtruths and normalmaps) with crack into a /tmp folder, rendered at 10 samples and with a resolution of 1024x1024. For more options please check cmdparser.py in lib/ folder or use --help in the arguments.

The concrete dictionary folder which contains all the concrete maps will be downloaded from a dropbox link if you haven't downloaded it already. The python script uses console commands wget and unzip to download and unzip the required folder. Install 'wget' and 'unzip' using command line prompt if you do not already have them in your linux system.

If you do not want to download the dropbox file using the python script, here is the dropbox link:
[Drop box link for concrete maps](https://www.dropbox.com/s/y1j6hc42sl6uidi/concretedictionary.zip?dl=1)

