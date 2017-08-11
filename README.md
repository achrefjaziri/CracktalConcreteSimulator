# Blender python basic scene generation

The blenderpython.py script generates a basic concrete with image textures for albedo, roughness and normal maps. 

Options to run it

1. Open Blender. Run the script from text editor
2. Type in command line:  blender default.blend --background --python blenderpython.py 

## Details regarding the code implementation

The code is fully commented. In order to run, you need pbr maps from freepbr website and update the code with the correct location for albedo, roughness and normal maps. The code will not work if you run some other rendering and you try to run this script from text editor of blender afterwards. It is built on the basic blender scene with predefined cube,lamp and camera. It removes the cube along with material and mesh. The command given above for the command line will work.

Blender version used: 2.78c

Free pbr website: https://freepbr.com/ (Working: Last checked 11/08/2017)


## Installing external modules

To install external python packages like scipy do the following:

1. Blender's python executable, e.g. python3.5m is located at 
~~~
/path/to/blender-version/python/bin/ 
~~~

2. Pip is not part of python and thus not part of blender's python. So download it from https://pip.pypa.io/en/stable/installing/ (state: 11/08/2017) and install it
~~~
./path/to/blender-version/python/bin/python3.5m /path/to/downloaded/pipinstaller/getpip.py
~~~
Note that this is independent of your system's pip

3. Install any packages with pip analogous to regular pip using blender's python version
~~~
./path/to/blender-version/python/bin/python3.5m pip install package
~~~

For any questions contact: murali@fias.uni-frankfurt.de
