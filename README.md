# Blender python basic scene generation

The blenderpython.py script generates a basic concrete with image textures for albedo, roughness and normal maps. 

Running the code:

1. The code was scripted in blender version 2.78c in a Linux OS. It might run in latest versions of blender, but just to be safe please download this specific version from http://download.blender.org/release/Blender2.78/
2. Ensure you are inside blenderpython folder in commandline by using cd command. 
3. Type in command line:  /path/to/blender --background --python blenderpython.py -- [--arguments] 
4. Example: /path/to/blender --background --python blenderpython.py -- --save-images True --num-images 10 --samples 10 --crack True --resolution 1024
5. The above command will render and save 10 images(rendered and their respective groundtruths and normalmaps) with crack in tmp/ folder rendered at 10 samples and with a resolution of 1024x1024. For more options please check cmdparser.py in lib/ folder or use --help in the arguments.

The concrete dictionary folder which contains all the concrete maps will be downloaded from dropbox link if you do not already have it in blenderpython folder. The python script uses console commands wget and unzip to download and unzip the required folder. Install 'wget' and 'unzip' using command line prompt if you do not already have them in your linux system.

If you do not want to download the google drive file using the python script, here is the google drive link:
[Drop box link for concrete maps](https://www.dropbox.com/s/y1j6hc42sl6uidi/concretedictionary.zip?dl=1)

Download and unzip it inside blenderpython folder. You should see concretedictionary folder after you unzip the downloaded file.


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
