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

1. Locate blender python folder. Ex: /home/username/blender-2.78c/python/bin/. In this folder the python version executable would be present. Ex:python3.5m
2. Download get-pip.py from pip website: https://pip.pypa.io/en/stable/installing/ (Working: Last checked 11/08/2017)
3. Install pip. Type in command line: /home/username/blender-2.78c/python/bin/python3.5m /home/username/Downloads/getpip.py (getpip.py location might be different)
4. To install pacakges use pip in command line. Example: /home/username/blender-2.78c/python/bin/python3.5m pip install scipy

For any questions contact: murali@fias.uni-frankfurt.de
