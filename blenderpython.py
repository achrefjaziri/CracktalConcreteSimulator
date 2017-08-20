import bpy
import math
import os
import sys
import numpy as np
import colorsys
from scipy import misc
import random
# Find out if system has GPU and if it has at least one GPU, it is going to be set
# Note: Blender seems to automatically use all GPUs in a system. If you want to avoid
# this behavior you can modify the GPUs index to "use=False": 
# bpy.context.user_preferences.addons['cycles'].preferences.devices[gpu_idx].use = False
if len(list(bpy.context.user_preferences.addons['cycles'].preferences.devices)) > 0:
    bpy.context.scene.cycles.device = 'GPU'

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# import custom scripts for map generation
from lib.fractalcracks import generate_fractal_cracks

# Crack possibilities as a list. 0: no crack. 1: crack. Randomly chosen inside sampleandrender function
crack = [0,1]

batchsize = 2 #will be something less than 6 GB 

# if you wish to save images in a folder set this flag to true
saveimages = True


# Three place-holder lists for rendered image, normal map and ground-truth
result_imgs = []
result_normals = []
result_gt = []

# concrete dictionary list for different maps to randomly render. Randomly chosen inside mastershader function
concretemaps = [1,2] #currently we have 2 maps for concrete albedo, roughness and normal.

# default image resolution to render
resolution = 2048
# if directory not found download from online for concrete maps
if os.path.isdir("concretedictionary"):
    print ("\n Concrete dictionary maps folder found")
else:
    flagres1 = os.system('wget -O concretedictionary.zip "https://drive.google.com/uc?export=download&id=0B81H1jpchFZQNjhSTjBzUUItbEU"')
    flagres2 = os.system('unzip concretedictionary.zip')
    flagres3 = os.system('rm concretedictionary.zip')

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


def mastershader(albedoval=[0.5, 0.5, 0.5], locationval=[0, 0, 0], rotationval=[0, 0, 0], scaleval=[1, 1, 1], concrete=1, cracked=1):
    # add a base primitive mesh. in this case a plane mesh is added at origin
    bpy.ops.mesh.primitive_plane_add(location=(0.0, -2.0, 5.5))
    # default object name is 'Plane'. or index 2 in this case
    # set scale and rotation
    bpy.data.objects['Plane'].scale = [6.275, 6.275, 6.275]
    bpy.data.objects['Plane'].rotation_euler = [105*math.pi/180, 0.0, 0.0]

    #add material to the object. first create a new material
    bpy.ops.material.new()
    # give a name to material if needed. new material default name 'Material' or access 0 index
    bpy.data.materials['Material'].name = 'concrete'
    # link material to the plane mesh
    bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete']

    # now in order to design the master shader for our material with concrete maps we need to use node editor.
    bpy.data.materials['concrete'].use_nodes = True

    # MASTER SHADER
    # material usually has diffuse bsdf connected to its surface input. check node editor by pressing shift+f3
    # master shader for general material is based on "PBR workflows in Cycles Render Engine" by Joonas Sairiala
    # with concrete being mainly dielectric with little or no metallic property,
    # it requires a base diffuse bsdf and glossy bsdf
    nodetree = bpy.data.materials['concrete'].node_tree  # required for linking
    nodes = bpy.data.materials['concrete'].node_tree.nodes
    nodes.new('ShaderNodeBsdfGlossy')
    # give names for nodes for easy understanding
    nodes['Diffuse BSDF'].name = 'basebsdf'
    nodes['Glossy BSDF'].name = 'specbsdf'
    nodes.new('ShaderNodeMixShader')
    nodes['Mix Shader'].name = 'mixbasespec'

    nodes['basebsdf'].inputs['Roughness'].default_value = 0.601 # based on curet database https://wiki.blender.org/index.php/User:Guiseppe/Oren_Nayar

    # you can modify nodes location from the script. useful for viewing in node editor. This is mainly for viewing easily.
    nodes['Material Output'].location = [650, 300]
    nodes['mixbasespec'].location = [450, 100]
    nodes.new('ShaderNodeFresnel')
    nodes['Fresnel'].name = 'fresnel1'
    nodes['fresnel1'].location = [200, 500]

    # Now to link node inputs and outputs
    nodetree.links.new(nodes['basebsdf'].outputs['BSDF'], nodes['mixbasespec'].inputs[1])  # index 1 corresponds to mix shader's shader input 1
    nodetree.links.new(nodes['specbsdf'].outputs['BSDF'], nodes['mixbasespec'].inputs[2])
    nodetree.links.new(nodes['fresnel1'].outputs[0], nodes['mixbasespec'].inputs[0])
    nodetree.links.new(nodes['mixbasespec'].outputs[0], nodes['Material Output'].inputs['Surface'])
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name = 'albedoconcrete' #albedo concrete
    nodes['albedoconcrete'].location = [-600, 600]
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name = 'roughnessconcrete' #roughness concrete
    nodes['roughnessconcrete'].location = [-600, 0]
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name = 'normalconcrete' #normal concrete
    nodes['normalconcrete'].location = [-600, -600]

    #link images to imagetexture node
    bpy.ops.image.open(filepath=os.path.join('concretedictionary/concrete'+str(concrete)+'/albedo'+str(concrete)+'.png')) #first open image to link
    nodes['albedoconcrete'].image = bpy.data.images[os.path.join('albedo'+str(concrete)+'.png')]
    bpy.ops.image.open(filepath=os.path.join('concretedictionary/concrete' + str(concrete) + '/roughness' + str(concrete) + '.png'))
    nodes['roughnessconcrete'].image = bpy.data.images[os.path.join('roughness' + str(concrete) + '.png')]
    bpy.ops.image.open(filepath=os.path.join('concretedictionary/concrete' + str(concrete) + '/normal' + str(concrete) + '.png'))
    nodes['normalconcrete'].image = bpy.data.images[os.path.join('normal' + str(concrete) + '.png')]

    # random albedo and other map rgb and mix nodes for random sampling
    nodes.new('ShaderNodeRGB')
    nodes['RGB'].name = 'samplingalbedorgb'
    nodes['samplingalbedorgb'].location = [-600, 900]
    nodes.new('ShaderNodeMapping')
    nodes['Mapping'].name = 'samplingmap'
    nodes['samplingmap'].location = [-1200, 0]
    nodes['samplingmap'].vector_type = 'VECTOR'
    nodes.new('ShaderNodeVectorMath')
    nodes['Vector Math'].operation = 'ADD'
    nodes['Vector Math'].name = 'addtranslation'
    nodes['addtranslation'].location = [-1500, 0]
    nodes.new('ShaderNodeRGB')
    nodes['RGB'].name = 'samplingtranslationrgb'
    nodes['samplingtranslationrgb'].location = [-1800, 0]
    nodes.new('ShaderNodeTexCoord')
    nodes['Texture Coordinate'].name = 'texcoord1'
    nodes['texcoord1'].location = [-1800, -300]
    nodes.new('ShaderNodeMixRGB')
    nodes['Mix'].location = [-300, 750]
    nodes['Mix'].name = 'samplingalbedomix'
    nodes['samplingalbedomix'].inputs['Fac'].default_value = 0.85

    # links for sampling nodes
    nodetree.links.new(nodes['samplingalbedomix'].inputs['Color1'], nodes['samplingalbedorgb'].outputs['Color'])
    nodetree.links.new(nodes['samplingalbedomix'].inputs['Color2'], nodes['albedoconcrete'].outputs['Color'])

    nodetree.links.new(nodes['samplingmap'].outputs['Vector'], nodes['albedoconcrete'].inputs['Vector'])
    nodetree.links.new(nodes['samplingmap'].outputs['Vector'], nodes['roughnessconcrete'].inputs['Vector'])
    nodetree.links.new(nodes['samplingmap'].outputs['Vector'], nodes['normalconcrete'].inputs['Vector'])
    nodetree.links.new(nodes['addtranslation'].outputs['Vector'], nodes['samplingmap'].inputs['Vector'])
    nodetree.links.new(nodes['addtranslation'].inputs[0], nodes['samplingtranslationrgb'].outputs['Color'])
    nodetree.links.new(nodes['addtranslation'].inputs[1], nodes['texcoord1'].outputs['UV'])

    # sampling values passed to the function
    nodes['samplingmap'].scale = [scaleval[0], scaleval[1], scaleval[2]]
    nodes['samplingmap'].rotation = [rotationval[0] * math.pi / 180, rotationval[1] * math.pi / 180,
                                     rotationval[2] * math.pi / 180]
    # rgb values for albedo change. need to convert hsv to rgb to use it here.
    rgbval = colorsys.hsv_to_rgb(albedoval[0], albedoval[1], albedoval[2])
    nodes['samplingalbedorgb'].outputs[0].default_value[0] = rgbval[0]
    nodes['samplingalbedorgb'].outputs[0].default_value[1] = rgbval[1]
    nodes['samplingalbedorgb'].outputs[0].default_value[2] = rgbval[2]

    # translation sampling
    nodes['samplingtranslationrgb'].outputs[0].default_value[0] = locationval[0]
    nodes['samplingtranslationrgb'].outputs[0].default_value[1] = locationval[1]
    nodes['samplingtranslationrgb'].outputs[0].default_value[2] = locationval[2]

    ## crack nodes
    if cracked:
        nodes.new('ShaderNodeTexImage')
        nodes['Image Texture'].name = 'albedocrack' #albedo crack
        nodes['albedocrack'].location = [-600, 300]
        nodes.new('ShaderNodeTexImage')
        nodes['Image Texture'].name = 'roughnesscrack' #roughness crack
        nodes['roughnesscrack'].location = [-600, -300]
        nodes.new('ShaderNodeTexImage')
        nodes['Image Texture'].name = 'normalcrack' #normal crack
        nodes['normalcrack'].location = [-600, -900]

        generated_maps = []
        # generate crack maps
        generated_maps[0:2] = (generate_fractal_cracks(resolution, 7))
        # order is: albedo, roughness, normals
        # for each map check whether it already has an alpha channel, i.e. the albedo map should have one
        # for all other maps add an alpha channel that is filled with ones
        for i in range(0, len(generated_maps)):
            # last shape index is amount of color channels
            if generated_maps[i].shape[-1] != 4:
                tmp = np.zeros((generated_maps[i].shape[0], generated_maps[i].shape[1], 4)) #place-holder
                tmp[:,:,0:3] = generated_maps[i] # copy old 3 channels
                tmp[:,:,3] = 1 # fill 4. alpha channel
                generated_maps[i] = tmp # copy back

        # initialize empty texture structures of corresponding size
        imgT_albedo = bpy.data.images.new("albedo_image", width=resolution, height=resolution)
        imgT_roughness = bpy.data.images.new("roughness_image", width=resolution, height=resolution)
        imgT_normals = bpy.data.images.new("normals_image", width=resolution, height=resolution)

        # flatten the arrays and assign them to the place-holder textures
        imgT_albedo.pixels = generated_maps[0].flatten().tolist()
        imgT_roughness.pixels = generated_maps[1].flatten().tolist()
        imgT_normals.pixels = generated_maps[2].flatten().tolist()

        # feed new texture into appropriate nodes
        nodes['albedocrack'].image = imgT_albedo
        nodes['roughnesscrack'].image = imgT_roughness
        nodes['normalcrack'].image = imgT_normals

        # create mix rgb nodes to mix crack maps and original image pbr maps
        nodes.new('ShaderNodeMixRGB')
        nodes['Mix'].name = 'albedomix'
        nodes['albedomix'].location = [-400, 450]
        nodes.new('ShaderNodeMixRGB')
        nodes['Mix'].name = 'roughnessmix'
        nodes['roughnessmix'].location = [-400, -150]
        nodes.new('ShaderNodeMixRGB')
        nodes['Mix'].name = 'normalmix'
        nodes['normalmix'].location = [-400, -750]

        # link crack and original map nodes to mixrgb
        nodetree.links.new(nodes['albedoconcrete'].outputs['Color'], nodes['albedomix'].inputs[1])
        nodetree.links.new(nodes['albedocrack'].outputs['Color'], nodes['albedomix'].inputs[2])
        nodetree.links.new(nodes['roughnessconcrete'].outputs['Color'], nodes['roughnessmix'].inputs[1])
        nodetree.links.new(nodes['roughnesscrack'].outputs['Color'], nodes['roughnessmix'].inputs[2])
        nodetree.links.new(nodes['normalconcrete'].outputs['Color'], nodes['normalmix'].inputs[1])
        nodetree.links.new(nodes['normalcrack'].outputs['Color'], nodes['normalmix'].inputs[2])

        # add appropriate factors for scaling mixrgb nodes
        nodetree.links.new(nodes['albedocrack'].outputs['Alpha'], nodes['albedomix'].inputs[0])
        # value for albedomix comes for crack map alpha
        nodes['roughnessmix'].inputs[0].default_value = 0.25
        nodes['normalmix'].inputs[0].default_value = 0.75

        #link albedo, roughness and normal mixrgb maps to color, roughness displacement.
        nodetree.links.new(nodes['albedomix'].outputs['Color'], nodes['basebsdf'].inputs['Color'])
        nodetree.links.new(nodes['roughnessmix'].outputs['Color'], nodes['specbsdf'].inputs['Roughness'])
        nodetree.links.new(nodes['normalmix'].outputs['Color'], nodes['Material Output'].inputs['Displacement'])
        nodetree.links.new(nodes['samplingalbedomix'].outputs['Color'], nodes['albedomix'].inputs['Color1'])
    else:
        nodetree.links.new(nodes['samplingalbedomix'].outputs['Color'], nodes['basebsdf'].inputs['Color'])
        nodetree.links.new(nodes['roughnessconcrete'].outputs['Color'], nodes['specbsdf'].inputs['Roughness'])
        nodetree.links.new(nodes['normalconcrete'].outputs['Color'], nodes['Material Output'].inputs['Displacement'])

    #now we need to uv unwrap over the entire mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
def render(path, f, s, cracked):
    bpy.data.scenes['Scene'].frame_end = f
    bpy.data.scenes['Scene'].render.filepath = path
    bpy.data.scenes['Scene'].cycles.samples = s
    bpy.data.scenes['Scene'].render.resolution_x = resolution
    bpy.data.scenes['Scene'].render.resolution_y = resolution
    bpy.data.scenes['Scene'].render.resolution_percentage = 100
    # before rendering, set the sceen camera to the camera that you created
    bpy.data.scenes['Scene'].camera = bpy.data.objects['Camera']

    #set render tile sizes
    bpy.data.scenes['Scene'].render.tile_x = 256
    bpy.data.scenes['Scene'].render.tile_y = 256

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
    result_imgs.append(misc.imread(filepath))

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

        result_gt.append(misc.imread(filepath))
    else:
        gtimage = np.zeros((resolution, resolution, 3))
        result_gt.append(gtimage)

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


def sampleandrender(num_images = 100, path='tmp/tmp.png', f=1, s=1):
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
    for i in range(num_images):
        albedoval = [hval[i], sval[i], vval[i]]
        locationval = [locationx[i], locationy[i], locationz[i]]
        rotationval = [rotationx[i], rotationy[i], rotationz[i]]
        scaleval = [scalex[i], scaley[i], scalez[i]]
        # randomly choose crack or noncrack structure
        cracked = random.choice(crack)
        # randomly choose which concrete mapset to use
        concrete = random.choice(concretemaps)
        # remove existing objects present in the scene
        removeexistingobjects()
        # modify existing camera
        camerasettings()
        # modify existing light source
        lightsource()
        # master shader for material with mesh
        mastershader(albedoval, locationval, rotationval, scaleval, concrete, cracked)
        # render the engine
        render(path, f, s, cracked)

        # save images to temporary folder if required for viewing later on
        if saveimages:
            res_string = os.path.join('tmp/render'+str(i)+'.png')
            gt_string = os.path.join('tmp/gt' + str(i) + '.png')
            normal_string = os.path.join('tmp/normal' + str(i) + '.png')
            misc.imsave(res_string,result_imgs[len(result_imgs)-1])
            misc.imsave(normal_string, result_normals[len(result_imgs) - 1])
            misc.imsave(gt_string, result_gt[len(result_imgs) - 1])

        # clear the lists of stored results
        if i % batchsize == 0: 
            del result_imgs[:]
            del result_normals[:]
            del result_gt[:]


if __name__ == "__main__": 
    #ensure that cycles engine is set for the basic scene.
    #predefined object name for scene is 'Scene'. Also can be accesed by index 0.
    bpy.data.scenes['Scene'].render.engine = 'CYCLES'
    # check if mode is object mode else set it to object mode
    checkmode = bpy.context.active_object.mode
    if checkmode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # set samples to 1 for debugging. 6 to 10 samples are usually sufficient for visually pleasing render results
    sampleandrender(num_images=8, path='tmp/tmp.png', f=1, s=1)