# Blender python basic scene generation

The blenderpython.py script generates a basic concrete with image textures for albedo, roughness and normal maps. 

Options to run it


1.  Ensure you are inside blenderpython folder in commandline by using cd command. Type in command line:  blender default.blend --background --python blenderpython.py 
2. Open blender. Open text editor. Load blenderpython.py. Open pythonconsole. Use os.chdir and change directory to blenderpython folder. Run blenderpython.py from text editor.

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
Note that depending on your OS and Blender version the shortcut "pip" could not exist and will then be "pip3.5" or any other version suffix.


For any questions contact: murali@fias.uni-frankfurt.de
