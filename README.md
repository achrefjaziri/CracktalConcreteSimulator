# Blender python basic scene generation

The blenderpython.py script generates a basic concrete with image textures for albedo, roughness and normal maps. 

Options to run it


1.  Ensure you are inside blenderpython folder in commandline by using cd command. Type in command line:  blender --background --python blenderpython.py 
2. Open blender. Open text editor. Load blenderpython.py. Open pythonconsole. Use os.chdir and change directory to blenderpython folder. Run blenderpython.py from text editor.

The concrete dictionary folder which contains all the concrete maps will be downloaded from google drive if you do not already have it in blenderpython folder. The python script uses console commands wget and unzip to download and unzip the required folder. Install 'wget' and 'unzip' using command line prompt if you do not already have them in your linux system.

If you do not want to download the google drive file using the python script, here is the google drive link:
[Google drive link for concrete maps](https://drive.google.com/uc?export=download&id=0B81H1jpchFZQNjhSTjBzUUItbEU)

Download and unzip it inside blenderpython folder. You should see concretedictionary folder after you unzip


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
