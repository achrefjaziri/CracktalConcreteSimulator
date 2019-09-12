# Blender python basic scene generation:

The generate.py script generates concrete PBR materials from a set of albedo, metallic, roughness and normal maps.
An extra height map is used for displacement of mesh vertices. 

# Installation:

Ubuntu users can find a pre-configured blender version as `.zip` file in this repository. The file uses git LFS, so the following steps are needed to actually clone it into the repository. This step can be skipped by downloading Blender 2.79 and following the config steps explained in the next subsection.

```
# 1. Install and configure Git LFS. This has to be done ONLY ONCE:
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt install git-lfs
git config --global filter.lfs.required true
git config --global filter.lfs.clean "git-lfs clean -- %f"
git config --global filter.lfs.smudge "git-lfs smudge --skip %f"
git config --global filter.lfs.process "git-lfs filter-process --skip"
git config --global lfs.batch "true"

# 2. Once LFS is installed, in this repo:
git lfs install
git lfs fetch
git lfs checkout

# 3. The .zip file containing Blender can now be extracted and pit in any path/to/blender in your filesystem.
```

## Installing external modules

To install external python packages like scipy do the following:

1. Blender's python (here referred to as `<BPY>`) executable, e.g. python3.5m is located at 
~~~
/path/to/blender-version/python/bin/ 
~~~

2. Pip is not part of python and thus not part of blender's python. This can be easily fixed by
~~~
<BPY> -m ensurepip
<BPY> -m pip install --upgrade pip
~~~

Note that this is independent of your system's pip. 

3. The `<BPY -m pip>` command is analogous to the `pip` executable on your regular python. You can then install the requirements in this repo as follows:
~~~
<BPY> -m pip install -r <REQUIREMENTS_FILE_PATH>
~~~


### Required external packages for this repository

see [requirements.txt](requirements.txt)

These may not be necessary:

~~~
sudo apt-get install libopenexr-dev
sudo apt-get install openexr
sudo apt-get install python3-dev
~~~


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
