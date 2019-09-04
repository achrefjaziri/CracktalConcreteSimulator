import bpy
import os
import sys
import random
import numpy as np
from scipy import misc
from fnmatch import fnmatch

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from lib.cmdparser import parse
from scenes.concretescene import ConcreteScene
from lib.rendermanager import RenderManager

# Find out if system has GPU and if it has at least one GPU, it is going to be set
# Note: Blender seems to automatically use all GPUs in a system. If you want to avoid
# this behavior you can modify the GPUs index to "use=False": 
# bpy.context.user_preferences.addons['cycles'].preferences.devices[gpu_idx].use = False

UseGPU = False
if len(list(bpy.context.user_preferences.addons['cycles'].preferences.devices)) > 0:
    bpy.context.scene.cycles.device = 'GPU'
    UseGPU = True


def run(num_images, n_concrete):
    for i in range(num_images):
        # randomly choose concrete texture map set
        concrete = random.randint(0, n_concrete-1)

        concrete_name = concrete_list[concrete].split('_Base_Color')
        # sample textures
        albedoPath = os.path.join(concrete_name[0] + '_Base_Color' + concrete_name[1])
        roughnessPath = os.path.join(concrete_name[0] + '_Roughness' + concrete_name[1])
        normalPath = os.path.join(concrete_name[0] + '_Normal' + concrete_name[1])
        heightPath = os.path.join(concrete_name[0] + '_Height' + concrete_name[1])

        # TODO: In the future include ambient occlusion and metallic textures in the nodes
        aoPath = os.path.join(concrete_name[0] + '_Ambient_Occlusion' + concrete_name[1])
        metallicPath = os.path.join(concrete_name[0] + '_Metallic' + concrete_name[1])
       
        print("Load new texture to shader...")
        scene.shaderDict["concrete"].load_texture(albedoPath, roughnessPath, normalPath, heightPath)
        scene.update()
        print("Done...")

        print("Rendering...")
        renderManager.render(
                            cameraLeft=bpy.data.objects['CameraLeft'], 
                            cameraRight=bpy.data.objects['CameraRight']
                            )
        print("Done...")

        # save images to folder
        if not os.path.isdir("res"):
            os.mkdir("res")

        # set filenames for storing images
        res_string = os.path.join('res/render' + str(i) + '.png')
        gt_string = os.path.join('res/gt' + str(i) + '.png')
        normal_string = os.path.join('res/normal' + str(i) + '.png')

        res_string_right = os.path.join('res/render_right' + str(i) + '.png')
        gt_string_right = os.path.join('res/gt_right' + str(i) + '.png')
        normal_string_right = os.path.join('res/normal_right' + str(i) + '.png')

        # save images to file
        misc.imsave(res_string, renderManager.result_imgs[-1])
        print("image save done...")
        misc.imsave(normal_string, renderManager.result_normals[-1])
        print("normal map save done...")
        misc.imsave(gt_string, renderManager.result_gt[-1])
        print("ground truth save done...")
        
        misc.imsave(res_string_right, renderManager.result_imgs_right[-1])
        print("image save done...")
        misc.imsave(normal_string_right, renderManager.result_normals_right[-1])
        print("normal map save done...")

        print("")

        # clear the lists of stored results
        del renderManager.result_imgs[:]
        del renderManager.result_normals[:]
        del renderManager.result_gt[:]


# parse command line arguments
args = parse(sys.argv)
print("Command line options:")
for arg in vars(args):
    print(arg, getattr(args, arg))


# if directory not found download from online for concrete maps
assert os.path.isdir("concrete_textures"), "no concrete texture folder found"

# check root path and find all the concrete maps based on _Base_Color
if args.path=='/concrete_textures':  # check for default path as mentioned in concrete dictionary
    root_path = os.getcwd()+args.path
else:
    root_path = args.path

pattern = "*_Base_Color*"

concrete_list = []
for path, subdirs, files in os.walk(root_path):
    for name in files:
        if fnmatch(name, pattern):
            concrete_list.append(os.path.join(path, name))

concrete_list = sorted(concrete_list)

# number of concrete maps is stored in n_concrete
n_concrete = len(concrete_list)
# the below is to set a default map which is altered during run time in run function. Please check run function.
concrete_name = concrete_list[0].split('_Base_Color')

print("Base texture maps have been loaded...")

# set scene to use cycles engine.
# predefined object name for scene is 'Scene'. Also can be accesed by index 0 for the first scene.
print("Setting rendering engine to Cycles render")
bpy.data.scenes['Scene'].render.engine = 'CYCLES'
print("Done...")

# check if mode is object mode else set it to object mode
print("Selecting object mode...")
checkmode = bpy.context.active_object.mode
if checkmode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
print("Done...")

# set samples to 1 for debugging. 6 to 10 samples are usually sufficient for visually pleasing render results
print("Setting up scene...")
# print args.crack
scene = ConcreteScene(args.resolution, args.crack, concrete_name)
print("Done...")

print("Init render manager...")
renderManager = RenderManager(path="tmp/tmp.png", frames=1, samples=args.samples, tilesize=args.tile_size,
                              resolution=args.resolution, cracked=args.crack)
renderManager.setScene(scene)
print("Done...")

print("Rendering...")
run(args.num_images, n_concrete)
print("Done...")
