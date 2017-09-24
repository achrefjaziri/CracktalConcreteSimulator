import bpy
import math
import os
import sys
import numpy as np
import colorsys
from scipy import misc
import random

import cv2

# Find out if system has GPU and if it has at least one GPU, it is going to be set
# Note: Blender seems to automatically use all GPUs in a system. If you want to avoid
# this behavior you can modify the GPUs index to "use=False": 
# bpy.context.user_preferences.addons['cycles'].preferences.devices[gpu_idx].use = False

#Use flag for deep learning to know whether system has a GPU
UseGPU = False
if len(list(bpy.context.user_preferences.addons['cycles'].preferences.devices)) > 0:
    bpy.context.scene.cycles.device = 'GPU'
    UseGPU = True

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# import custom scripts for map generation
from lib.fractalcracks import generate_fractal_cracks
from lib.cmdparser import parse
from lib.mastershader import MasterShader
from lib.crackshader import CrackShader



def removeexistingobjects():
    check = bpy.data.objects is not None
    # remove pre-existing objects from blender
    if check == True:
        for object in bpy.data.objects:
            object.select = True
            bpy.ops.object.delete()
            # clear mesh and material data. removing objects alone is not necessary
            for mesh in bpy.data.meshes:
                bpy.data.meshes.remove(mesh, do_unlink=True)
            for material in bpy.data.materials:
                bpy.data.materials.remove(material, do_unlink=True)
            for camera in bpy.data.cameras:
                bpy.data.cameras.remove(camera, do_unlink=True)
            for lamp in bpy.data.lamps:
                bpy.data.lamps.remove(lamp, do_unlink=True)


def camerasettings():
    # add camera
    bpy.ops.object.camera_add()
    # location of camera
    bpy.data.objects['Camera'].location = (0.0, -15.0, 2.0)
    # rotation of camera. x axis rotation is 105.125 degrees in this example
    bpy.data.objects['Camera'].rotation_euler = [105.125*math.pi/180, 0.0, 0.0]
    # scale of camera usually unaltered.
    bpy.data.objects['Camera'].scale = [1.0, 1.0, 1.0]
    # by default camera type is perspective. uncomment below line for changing camera to orthographic.
    #bpy.data.cameras['Camera'].type='ORTHO'     #PERSP for perspective. default orthographic scale is 7.314
    # focal length of camera
    bpy.data.cameras['Camera'].lens = 35.00
    # focal length unit
    bpy.data.cameras['Camera'].lens_unit = 'MILLIMETERS' #FOV for field of view
    # note: you can add camera presets like samsung galaxy s4.
    # look at documentation and uncomment below line and modify accordinly. below line not tested
    #bpy.ops.script.execute_preset(filepath="yourpathlocation")


def lightsource():
    # add lamp
    bpy.ops.object.lamp_add(type='SUN')
    # change sun location.
    bpy.data.objects['Sun'].location = [0.0,-5.0,5.0]
    bpy.data.objects['Sun'].rotation_euler = [59*math.pi/180, 0.0, 0.0]

    # you can modify object names. example given below. uncomment if needed.
    # if uncommented upcoming commands should also be modified accordingly
    #bpy.data.lamps[0].name = 'Sun'
    #bpy.data.objects['Sun'].name = 'Sun'
    # you can add more light sources. uncomment below line for example light source
    #bpy.ops.object.lamp_add(type='POINT')

    # change rotation of sun's direction vector.
    bpy.data.objects['Sun'].rotation_euler = [59*math.pi/180, 0.0, 0.0]
    # in order to change color, strength of sun, we have to use nodes.
    # also node editing is quite useful for designing layers to your rendering
    bpy.data.lamps['Sun'].use_nodes = True
    # in the above statement we used 'Lamp' instead of index 0.
    # The default name of lamps is 'Lamp' as described in the above comments.

    # set color and strength value of sun using nodes.
    bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Color'].default_value = [1.0, 1.0, 1.0, 1.0]
    bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 3.0


def setScene():
    pass;

def mastershader(albedoval=[0.5, 0.5, 0.5], locationval=[0, 0, 0], rotationval=[0, 0, 0], scaleval=[1, 1, 1], concrete=1, cracked=1):
    print("Setting mastershader...");
    # add a base primitive mesh. in this case a plane mesh is added at origin
    print("Set primitive mesh")
    bpy.ops.mesh.primitive_plane_add(location=(0.0, -2.0, 5.5))
    # default object name is 'Plane'. or index 2 in this case
    # set scale and rotation
    print("Modify mesh")
    bpy.data.objects['Plane'].scale = [6.275, 6.275, 6.275]
    bpy.data.objects['Plane'].rotation_euler = [105*math.pi/180, 0.0, 0.0]

    shadername = "concrete";
    albedoPath = os.path.join('concretedictionary/concrete' + str(concrete) + '/albedo' + str(concrete) + '.png')
    roughnessPath = os.path.join('concretedictionary/concrete' + str(concrete) + '/roughness' + str(concrete) + '.png');
    normalPath = os.path.join('concretedictionary/concrete' + str(concrete) + '/normal' + str(concrete) + '.png')
    
    if(not cracked):
        print("Init mastershader");
        shader = MasterShader(shadername, albedoPath, roughnessPath, normalPath);
        print("Done...");
        print("Link shader to plane object");
        bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete'];
        print("Done...");

        # TODO: sample shader image sources!

        print("Sample shader values");
        shader.sampleTexture();
        print("Done...");
        
        print("Apply shader to obj mesh");
        shader.applyTo("Plane");
        print("Done...");
    elif(cracked):
        print("Init crackshader");
        shader = CrackShader(shadername, albedoPath, roughnessPath, normalPath, args.resolution);
        print("Done...");
        print("Link shader to plane object");
        bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete'];
        print("Done...");

        # TODO: sample shader image sources!

        print("Sample shader values");
        shader.sampleTexture();
        print("Done...");
        
        print("Apply shader to obj mesh");
        shader.applyTo("Plane");
        print("Done...");


def render(path, f, s, cracked):
    bpy.data.scenes['Scene'].frame_end = f
    bpy.data.scenes['Scene'].render.filepath = path
    bpy.data.scenes['Scene'].cycles.samples = s
    bpy.data.scenes['Scene'].render.resolution_x = args.resolution
    bpy.data.scenes['Scene'].render.resolution_y = args.resolution
    bpy.data.scenes['Scene'].render.resolution_percentage = 100
    # before rendering, set the sceen camera to the camera that you created
    bpy.data.scenes['Scene'].camera = bpy.data.objects['Camera']

    #set render tile sizes
    bpy.data.scenes['Scene'].render.tile_x = args.tile_size
    bpy.data.scenes['Scene'].render.tile_y = args.tile_size

    render_img(filepath=path, frames=f, samples=s)
    # render groundtruth
    rendergt(filepath=path, frames=f, samples=s, crackflag=cracked)
    # render normalmap
    rendernp(filepath=path, frames=f, samples=s, crackflag=cracked)


def render_img(filepath, frames, samples):
    # Commented code can later potentially be used to get the result directly from the CompositorLayer 
    # in principle this works fine, however it needs a GUI to work....
    # and pipe convert and reshape it into a numpy array
    # switch on nodes
    '''
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    
    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = 185, 285
    
    # create output node
    v = tree.nodes.new('CompositorNodeViewer')
    v.name = 'ImageViewerNode'
    v.location = 750, 210
    v.use_alpha = False

    # create another output node for surface normals
    n = tree.nodes.new('CompositorNodeViewer')
    n.location = 750, 390
    n.use_alpha = False
    
    # for the normals
    bpy.data.scenes['Scene'].render.layers["RenderLayer"].use_pass_normal = True

    # Links
    links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input
    links.new(rl.outputs['Normal'], n.inputs[0])  # link Normal output to Viewer input
    '''

    bpy.ops.render.render(write_still=True)
    # as it seems impossible to access rendered image directly due to some blender internal
    # buffer freeing issues, we save the result to a tmp image and load it again.
    res = misc.imread(filepath)
    # if used for deep learning, down-sample and exclude alpha channel before feeding into list
    if args.deep_learning:
        res = misc.imresize(res, size=(args.patch_size,args.patch_size),  interp='nearest').astype(float)/255 #imresize automatically converts to uint8
        res = res[:,:,0:3]
    result_imgs.append(res)

    '''
    # get viewer pixels
    img_pixels = bpy.data.images['Viewer Node'].pixels
    normal_pixels = bpy.data.images['Viewer Node'].pixels

    # copy buffer to numpy array for faster manipulation
    # size is always width * height * 4 (rgba)
    arr = np.array(img_pixels)
    arr = arr.reshape((resolution, resolution, 4))
    misc.imsave('outputfile.png', arr)

    arr = np.array(normal_pixels)
    arr = arr.reshape((resolution, resolution, 4))
    misc.imsave('normaloutputfile.png', arr)
    '''


def rendergt(filepath, frames, samples, crackflag):
    if crackflag:
        nodetree = bpy.data.materials['concrete'].node_tree  # required for linking
        nodes = bpy.data.materials['concrete'].node_tree.nodes
        nodes.new('ShaderNodeEmission')
        nodes['Emission'].name = 'emit1'
        nodes['emit1'].location = [450, -100]
        nodetree.links.new(nodes['emit1'].inputs['Color'], nodes['albedocrack'].outputs['Color'])
        nodetree.links.new(nodes['emit1'].outputs['Emission'], nodes['Material Output'].inputs['Surface'])

        # remove displacement links
        for l in nodes['Material Output'].inputs['Displacement'].links:
            nodetree.links.remove(l)
        bpy.ops.render.render(write_still=True)
        gt = misc.imread(filepath)
        # binarize the ground-truth map
        gt = gt > 0
        gt = gt.astype(int)
        misc.imsave(filepath, gt)

        # if used for deep learning, down-sample and exclude alpha channel before feeding into list
        if args.deep_learning:
            gt = misc.imread(filepath)
            gt = misc.imresize(gt, size=(args.patch_size, args.patch_size),  interp='nearest').astype(float) / 255  # imresize automatically converts to uint8
            gt = gt[:, :, 0:3]
        result_gt.append(gt)
    else:
        gt = np.zeros((args.resolution, args.resolution, 3))
        if args.deep_learning:
            gt = misc.imresize(gt, size=(args.patch_size, args.patch_size),  interp='nearest').astype(
                float) / 255  # imresize automatically converts to uint8
        result_gt.append(gt)

def rendernp(filepath, frames, samples, crackflag):
    nodetree = bpy.data.materials['concrete'].node_tree  # required for linking
    nodes = bpy.data.materials['concrete'].node_tree.nodes
    if crackflag:
        nodetree.links.new(nodes['emit1'].inputs['Color'], nodes['normalmix'].outputs['Color'])
    else:
        nodes.new('ShaderNodeEmission')
        nodes['Emission'].name = 'emit1'
        nodes['emit1'].location = [450, -100]
        nodetree.links.new(nodes['emit1'].outputs['Emission'], nodes['Material Output'].inputs['Surface'])
        nodetree.links.new(nodes['emit1'].inputs['Color'], nodes['normalconcrete'].outputs['Color'])
        for l in nodes['Material Output'].inputs['Displacement'].links:
            nodetree.links.remove(l)
    bpy.ops.render.render(write_still=True)

    result_normals.append(misc.imread(filepath))

    res = misc.imread(filepath)
    # if used for deep learning, down-sample and exclude alpha channel before feeding into list
    if args.deep_learning:
        res = misc.imresize(res, size=(args.patch_size, args.patch_size), interp='nearest').astype(float) / 255  # imresize automatically converts to uint8
        res = res[:, :, 0:3]
    result_normals.append(res)


def sampleandrender(num_images, s, path='tmp/tmp.png', f=1):
    print("Sampling render called...");
    hval = np.random.normal(0.5, 0.3, size=num_images)
    sval = np.random.normal(0.5, 0.3, size=num_images)
    hval = np.clip(hval, 0, 1)
    sval = np.clip(sval, 0, 1)
    vval = np.empty(num_images, dtype='float64')
    vval.fill(0.529)
    # location sampling has to be between 0 and 1 because we are using RGB mixer node for translation
    locationx = np.random.uniform(0, 1, size=num_images)
    locationy = np.random.uniform(0, 1, size=num_images)
    locationz = np.random.uniform(0, 1, size=num_images)
    rotationx = np.random.uniform(0, 15, size=num_images)
    rotationy = np.random.uniform(0, 15, size=num_images)
    rotationz = np.random.uniform(0, 15, size=num_images)
    scalex = np.random.uniform(0.75, 1.25, size=num_images)
    scaley = np.random.uniform(0.75, 1.25, size=num_images)
    scalez = np.random.uniform(0.75, 1.25, size=num_images)
    print("init complete...");
    for i in range(num_images):
        albedoval = [hval[i], sval[i], vval[i]]
        locationval = [locationx[i], locationy[i], locationz[i]]
        rotationval = [rotationx[i], rotationy[i], rotationz[i]]
        scaleval = [scalex[i], scaley[i], scalez[i]] 
        print("maps loaded...");
        # alternatively choose crack or noncrack structure
        if i % 2 == 0:
            cracked = crack[1]
        else:
            cracked = crack[1]
        # randomly choose which concrete mapset to use
        concrete = random.randint(1,concretemaps)
        # remove existing objects present in the scene
        print("remove existing objects...");
        removeexistingobjects()
        print("Done...")
        # modify existing camera
        print("modify camera settings...");
        camerasettings()
        print("Done...");
        # modify existing light source
        print("modify lightsources...");
        lightsource()
        print("Done...")
        # master shader for material with mesh
        print("Setting master shader...");
        mastershader(albedoval, locationval, rotationval, scaleval, concrete, cracked)
        print("Done...");
        # render the engine
        print("Rendering...");
        render(path, f, s, cracked)
        print("Done...");

        # save images to temporary folder if required for viewing later on
        if args.save_images:
            res_string = os.path.join('tmp/render'+str(i)+'.png')
            gt_string = os.path.join('tmp/gt' + str(i) + '.png')
            normal_string = os.path.join('tmp/normal' + str(i) + '.png')
            misc.imsave(res_string,result_imgs[len(result_imgs)-1])
            misc.imsave(normal_string, result_normals[len(result_normals) - 1])
            misc.imsave(gt_string, result_gt[len(result_gt) - 1])


        if i > 0: # additional check as 0 % anything = 0
            if i % args.batch_size == 0:
                # feed the deep network

                if args.deep_learning:
                    # convert the list into numpy arrays and convert from float64 to float32
                    tmp_imgs = np.array(result_imgs).astype(np.float32)
                    tmp_gts = np.array(result_gt).astype(np.float32)

                    # torch expects image size[1] to be the channels
                    tmp_imgs = np.transpose(tmp_imgs, (0, 3, 1, 2))
                    tmp_gts = np.transpose(tmp_gts, (0, 3, 1, 2))

                    # convert to torch tensor
                    image_tensor = torch.from_numpy(tmp_imgs)
                    gt_tensor = torch.from_numpy(tmp_gts)

                    print("Training deep net!")
                    train(image_tensor, gt_tensor, model, criterion, optimizer)

                # clear the lists of stored results
                del result_imgs[:]
                del result_normals[:]
                del result_gt[:]


if __name__ == "__main__":
    

    # parse command line arguments
    args = parse(sys.argv)
    print("Command line options:")
    for arg in vars(args):
        print(arg, getattr(args, arg))

    # Crack possibilities as a list. 0: no crack. 1: crack. Randomly chosen inside sampleandrender function
    crack = [0,1]

    # Three place-holder lists for rendered image, normal map and ground-truth
    result_imgs = []
    result_normals = []
    result_gt = []

    # concrete dictionary list for different maps to randomly render. Randomly chosen inside mastershader function
    concretemaps = 3 #currently we have 3 maps for concrete albedo, roughness and normal. so give any number in the range of [1,3]

    # if directory not found download from online for concrete maps
    if os.path.isdir("concretedictionary"):
        print ("Concrete dictionary maps folder found")
    else:
        flagres1 = os.system('wget -O concretedictionary.zip "https://www.dropbox.com/s/y1j6hc42sl6uidi/concretedictionary.zip?dl=1"')
        flagres2 = os.system('unzip concretedictionary.zip')
        flagres3 = os.system('rm concretedictionary.zip')

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
    #predefined object name for scene is 'Scene'. Also can be accesed by index 0.
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
    print("Do sampling render...");
    sampleandrender(args.num_images, args.samples, path='tmp/tmp.png', f=1)
    print("Done...");
