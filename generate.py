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

# import custom scripts for map generation
from lib.fractalcracks import generate_fractal_cracks
from lib.cmdparser import parse

from scenes.concretescene import ConcreteScene

from lib.rendermanager import RenderManager

# Find out if system has GPU and if it has at least one GPU, it is going to be set
# Note: Blender seems to automatically use all GPUs in a system. If you want to avoid
# this behavior you can modify the GPUs index to "use=False": 
# bpy.context.user_preferences.addons['cycles'].preferences.devices[gpu_idx].use = False

#Use flag for deep learning to know whether system has a GPU
UseGPU = False
if len(list(bpy.context.user_preferences.addons['cycles'].preferences.devices)) > 0:
    bpy.context.scene.cycles.device = 'GPU'
    UseGPU = True


def run(num_images, s, path='tmp/tmp.png', f=1):
    for i in range(num_images):
        # alternatively choose crack or noncrack structure
        if i % 2 == 0:
            cracked = crack[0]
        else:
            cracked = crack[1]
        # randomly chooses based on uniform distribution as to which concrete mapset to use between index 0 and n_concrete-1
        concrete = random.randint(0,n_concrete-1)

        concrete_name = concrete_list[concrete].split('_Base_Color')
        # sample textures
        albedoPath = os.path.join(concrete_name[0] + '_Base_Color' + concrete_name[1])
        roughnessPath = os.path.join(concrete_name[0] + '_Roughness' + concrete_name[1])
        normalPath = os.path.join(concrete_name[0] + '_Normal' + concrete_name[1])
        heightPath = os.path.join(concrete_name[0] + '_Height' + concrete_name[1])
        aoPath = os.path.join(concrete_name[0] + '_Ambient_Occlusion' + concrete_name[1])
        metallicPath = os.path.join(concrete_name[0] + '_Metallic' + concrete_name[1])
       
        print("Load new texture to shader...");
        # TODO: storing height texture path returned from master shader. needs to be fixed
        heighttexpath = scene.shaderDict["concrete"].load_texture(albedoPath, roughnessPath, normalPath, heightPath);
        # TODO: heigh texture path passed to concretescene. This needs to be fixed.
        scene.update(heighttexpath);
        print("Done...");

        print("Rendering...");
        renderManager.render();
        print("Done...");

        # save images to temporary folder if required for viewing later on
        if args.save_images:
            res_string = os.path.join('tmp/render'+str(i)+'.png')
            gt_string = os.path.join('tmp/gt' + str(i) + '.png')
            normal_string = os.path.join('tmp/normal' + str(i) + '.png')
            misc.imsave(res_string, renderManager.result_imgs[-1])
            print("image save done...")
            misc.imsave(normal_string, renderManager.result_normals[-1])
            print("normal map save done...")
            misc.imsave(gt_string, renderManager.result_gt[-1])
            print("ground truth save done...")
            print("");

        if i > 0: # additional check as 0 % anything = 0
            if i % args.batch_size == 0:
                # feed the deep network
                if args.deep_learning:
                    # convert the list into numpy arrays and convert from float64 to float32
                    tmp_imgs = np.array(renderManager.result_imgs).astype(np.float32)
                    tmp_gts = np.array(renderManager.result_gt).astype(np.float32)

                    # torch expects image size[1] to be the channels
                    tmp_imgs = np.transpose(tmp_imgs, (0, 3, 1, 2))
                    tmp_gts = np.transpose(tmp_gts, (0, 3, 1, 2))

                    # convert to torch tensor
                    image_tensor = torch.from_numpy(tmp_imgs)
                    gt_tensor = torch.from_numpy(tmp_gts)

                    print("Training deep net!")
                    train(image_tensor, gt_tensor, model, criterion, optimizer)

                # clear the lists of stored results
                del renderManager.result_imgs[:]
                del renderManager.result_normals[:]
                del renderManager.result_gt[:]


##################
##### PROGRAM
##################

# parse command line arguments
args = parse(sys.argv)
print("Command line options:")
for arg in vars(args):
    print(arg, getattr(args, arg))

# Crack possibilities as a list. 0: no crack. 1: crack. Randomly chosen inside sampleandrender function
crack = [0, 1]


# if directory not found download from online for concrete maps
if os.path.isdir("concretedictionary"):
    print ("Concrete dictionary maps folder found")
else:
    flagres1 = os.system('wget -O concretedictionary.zip "https://www.dropbox.com/s/y1j6hc42sl6uidi/concretedictionary.zip?dl=1"')
    flagres2 = os.system('unzip concretedictionary.zip')
    flagres3 = os.system('rm concretedictionary.zip')

# check root path and find all the concrete maps based on _Base_Color
if (args.path=='/concretedictionary'):  # check for default path as mentioned in concrete dictionary
    root_path = os.getcwd()+args.path
else:
    root_path = args.path
pattern = "*_Base_Color*"

concrete_list = []
for path, subdirs, files in os.walk(root_path):
    for name in files:
        if fnmatch(name, pattern):
            concrete_list.append(os.path.join(path,name))

concrete_list = sorted(concrete_list)

# number of concrete maps is stored in n_concrete
n_concrete = len(concrete_list)
# the below is to set a default map which is altered during run time in run function. Please check run function.
concrete_name = concrete_list[0].split('_Base_Color')

print("Base texture maps have been loaded...");
# only initialize a deep network if the save option to generate
# TODO: Deepnet stuff desperately needs a refactor
if args.deep_learning:
    print("Importing deep learning modules...");
    import torch
    import torch.nn.parallel
    import torch.backends.cudnn as cudnn
    import lib.deep_architectures
    from lib.train import train, validate

    # create deep network model
    net_init_method = getattr(lib.deep_architectures, args.architecture)
    model = net_init_method()
    if UseGPU:
        model = torch.nn.DataParallel(model).cuda()

    print("Neural Network architecture: \n", model)
    # CUDNN
    cudnn.benchmark = True

    if UseGPU:
        criterion = torch.nn.MSELoss().cuda()
    else:
        criterion = torch.nn.MSELoss()

    optimizer = torch.optim.SGD(model.parameters(), args.learning_rate,
                                momentum=args.momentum,
                                weight_decay=args.weight_decay)

#ensure that cycles engine is set for the basic scene.
#predefined object name for scene is 'Scene'. Also can be accesed by index 0 for the first scene.
print("Setting rendering engine to Cycles render")
bpy.data.scenes['Scene'].render.engine = 'CYCLES'
print("Done...");

# check if mode is object mode else set it to object mode
print("Selecting object mode...");
checkmode = bpy.context.active_object.mode
if checkmode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
print("Done...");

# set samples to 1 for debugging. 6 to 10 samples are usually sufficient for visually pleasing render results
print("Setting up scene...");
scene = ConcreteScene(args.resolution, args.crack, concrete_name);
print("Done...");

print("Init render manager...");
renderManager = RenderManager(path="tmp/tmp.png", frames=1, samples=args.samples, tilesize=args.tile_size, resolution=args.resolution, cracked=1);
renderManager.setScene(scene);
print("Done...");

print("Rendering...")
run(args.num_images, args.samples, path='tmp/tmp.png', f=1)
print("Done...");
