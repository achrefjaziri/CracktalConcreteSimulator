import bpy
import math
import os
import numpy as np
import colorsys

# Change this later into either properly sampled parameters or an argument parser
cracked = True

def removeexistingobjects():
    check = bpy.data.objects is not None
    # remove pre-existing objects from blender
    if check == True:
        for object in bpy.data.objects:
            object.select = True
            bpy.ops.object.delete()
            # clear mesh and material data. removing objects alone is not necessary
            for mesh in bpy.data.meshes:
                bpy.data.meshes.remove(mesh,do_unlink=True)
            for material in bpy.data.materials:
                bpy.data.materials.remove(material,do_unlink=True)
            for camera in bpy.data.cameras:
                bpy.data.cameras.remove(camera,do_unlink=True)
            for lamp in bpy.data.lamps:
                bpy.data.lamps.remove(lamp,do_unlink=True)
        
def camerasettings():
    # add camera
    bpy.ops.object.camera_add()
    # location of camera
    bpy.data.objects['Camera'].location = (0.0,-15.0,2.0)
    # rotation of camera. x axis rotation is 105.125 degrees in this example
    bpy.data.objects['Camera'].rotation_euler=[105.125*math.pi/180,0.0,0.0]
    # scale of camera usually unaltered.
    bpy.data.objects['Camera'].scale=[1.0,1.0,1.0]
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
    bpy.data.objects['Sun'].rotation_euler=[59*math.pi/180,0,0]

    # you can modify object names. example given below. uncomment if needed.
    # if uncommented upcoming commands should also be modified accordingly
    #bpy.data.lamps[0].name = 'Sun'
    #bpy.data.objects['Sun'].name = 'Sun'
    # you can add more light sources. uncomment below line for example light source
    #bpy.ops.object.lamp_add(type='POINT')


    # change rotation of sun's direction vector.
    bpy.data.objects['Sun'].rotation_euler=[59*math.pi/180,0.0,0.0]
    # in order to change color, strength of sun, we have to use nodes. also node editing is quite useful for designing layers to your rendering
    bpy.data.lamps['Sun'].use_nodes=True
    # in the above statement we used 'Lamp' instead of index 0. The default name of lamps is 'Lamp' as described in the above comments.

    # set color and strength value of sun using nodes.
    bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Color'].default_value = [1.0,1.0,1.0,1.0]
    bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 3.0

def mastershader(albedoval=[0.5,0.5,0.5],locationval=[0,0,0],rotationval=[0,0,0],scaleval=[1,1,1]):
    # add a base primitive mesh. in this case a plane mesh is added at origin
    bpy.ops.mesh.primitive_plane_add(location=(0,-2.0,5.5))
    # default object name is 'Plane'. or index 2 in this case
    # set scale and rotation
    bpy.data.objects['Plane'].scale=[6.275,6.275,6.275]
    bpy.data.objects['Plane'].rotation_euler=[105*math.pi/180,0,0]

    #add material to the object. first create a new material
    bpy.ops.material.new()
    # give a name to material if needed. new material default name 'Material' or access 0 index
    bpy.data.materials['Material'].name='concrete'
    # link material to the plane mesh
    bpy.data.objects['Plane'].active_material=bpy.data.materials['concrete']

    # now in order to design the master shader for our material with concrete maps we need to use node editor.
    bpy.data.materials['concrete'].use_nodes=True

    # MASTER SHADER
    # material usually has diffuse bsdf connected to its surface input. check node editor by pressing shift+f3
    # master shader for general material is based on "PBR workflows in Cycles Render Engine" by Joonas Sairiala
    # with concrete being mainly dielectric with little or no metallic property, it requires a base diffuse bsdf and glossy bsdf
    nodetree = bpy.data.materials['concrete'].node_tree  # required for linking
    nodes = bpy.data.materials['concrete'].node_tree.nodes
    nodes.new('ShaderNodeBsdfGlossy')
    # give names for nodes for easy understanding
    nodes['Diffuse BSDF'].name = 'basebsdf'
    nodes['Glossy BSDF'].name = 'specbsdf'
    nodes.new('ShaderNodeMixShader')
    nodes['Mix Shader'].name='mixbasespec'

    nodes['basebsdf'].inputs['Roughness'].default_value = 0.601 # based on curet database https://wiki.blender.org/index.php/User:Guiseppe/Oren_Nayar

    # you can modify nodes location from the script. useful for viewing in node editor. This is mainly for viewing easily.
    nodes['Material Output'].location=[650,300]
    nodes['mixbasespec'].location=[450,100]
    nodes.new('ShaderNodeFresnel')
    nodes['Fresnel'].name='fresnel1'
    nodes['fresnel1'].location=[200,500]

    # Now to link node inputs and outputs
    nodetree.links.new(nodes['basebsdf'].outputs['BSDF'],nodes['mixbasespec'].inputs[1]) # index 1 corresponds to mix shader's shader input 1
    nodetree.links.new(nodes['specbsdf'].outputs['BSDF'],nodes['mixbasespec'].inputs[2])
    nodetree.links.new(nodes['fresnel1'].outputs[0],nodes['mixbasespec'].inputs[0])
    nodetree.links.new(nodes['mixbasespec'].outputs[0],nodes['Material Output'].inputs['Surface'])
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name='albedoconcrete' #albedo concrete
    nodes['albedoconcrete'].location=[-600,600]
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name='roughnessconcrete' #roughness concrete
    nodes['roughnessconcrete'].location=[-600,0]
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name='normalconcrete' #normal concrete
    nodes['normalconcrete'].location=[-600,-600]

    #link images to imagetexture node
    bpy.ops.image.open(filepath='testimagesblender/concretemaps/albedo.png') #first open image to link
    nodes['albedoconcrete'].image=bpy.data.images['albedo.png']
    bpy.ops.image.open(filepath='testimagesblender/concretemaps/roughness.png')
    nodes['roughnessconcrete'].image=bpy.data.images['roughness.png']
    bpy.ops.image.open(filepath='testimagesblender/concretemaps/normal.png')
    nodes['normalconcrete'].image=bpy.data.images['normal.png']

    '''
    # Possible way of feeding in numpy data into textures 
    imgT = bpy.data.images.new("MyImage", width=2048, height=2048)

    testarray = np.random.randint(0, 255, size=(2048, 2048, 3))
    ostream = []
    for i in range(0, 2048, 1):
        for j in range(0, 2048, 1):
            v = testarray[i][j]

            ostream.append(v[0])  # Red
            ostream.append(v[1])  # Green
            ostream.append(v[2])  # Blue
            ostream.append(1)  # Alpha
    imgT.pixels = ostream

    nodes['albedoconcrete'].image = imgT
    nodes['roughnessconcrete'].image = imgT
    nodes['normalconcrete'].image = imgT
    '''
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
        nodes['Image Texture'].name='albedocrack' #albedo crack
        nodes['albedocrack'].location=[-600,300]
        nodes.new('ShaderNodeTexImage')
        nodes['Image Texture'].name='roughnesscrack' #roughness crack
        nodes['roughnesscrack'].location=[-600,-300]
        nodes.new('ShaderNodeTexImage')
        nodes['Image Texture'].name='normalcrack' #normal crack
        nodes['normalcrack'].location=[-600,-900]

        # link crack map images to the above nodes
        bpy.ops.image.open(filepath='testimagesblender/crackmaps/albedo1.png')
        nodes['albedocrack'].image=bpy.data.images['albedo1.png']
        bpy.ops.image.open(filepath='testimagesblender/crackmaps/roughness1.png')
        nodes['roughnesscrack'].image=bpy.data.images['roughness1.png']
        bpy.ops.image.open(filepath='testimagesblender/crackmaps/normals1.png')
        nodes['normalcrack'].image=bpy.data.images['normals1.png']

        # create mix rgb nodes to mix crack maps and original image pbr maps
        nodes.new('ShaderNodeMixRGB')
        nodes['Mix'].name='albedomix'
        nodes['albedomix'].location=[-400,450]
        nodes.new('ShaderNodeMixRGB')
        nodes['Mix'].name='roughnessmix'
        nodes['roughnessmix'].location=[-400,-150]
        nodes.new('ShaderNodeMixRGB')
        nodes['Mix'].name='normalmix'
        nodes['normalmix'].location=[-400,-750]

        # link crack and original map nodes to mixrgb
        nodetree.links.new(nodes['albedoconcrete'].outputs['Color'],nodes['albedomix'].inputs[1])
        nodetree.links.new(nodes['albedocrack'].outputs['Color'],nodes['albedomix'].inputs[2])
        nodetree.links.new(nodes['roughnessconcrete'].outputs['Color'],nodes['roughnessmix'].inputs[1])
        nodetree.links.new(nodes['roughnesscrack'].outputs['Color'],nodes['roughnessmix'].inputs[2])
        nodetree.links.new(nodes['normalconcrete'].outputs['Color'],nodes['normalmix'].inputs[1])
        nodetree.links.new(nodes['normalcrack'].outputs['Color'],nodes['normalmix'].inputs[2])

        # add appropriate factors for scaling mixrgb nodes
        nodetree.links.new(nodes['albedocrack'].outputs['Alpha'],nodes['albedomix'].inputs[0]) # value for albedomix comes for crack map alpha
        nodes['roughnessmix'].inputs[0].default_value=0.5
        nodes['normalmix'].inputs[0].default_value=0.9

        #link albedo, roughness and normal mixrgb maps to color, roughness displacement.
        nodetree.links.new(nodes['albedomix'].outputs['Color'],nodes['basebsdf'].inputs['Color'])
        #nodetree.links.new(nodes['albedomix'].outputs['Color'],nodes['specbsdf'].inputs['Color'])
        nodetree.links.new(nodes['roughnessmix'].outputs['Color'],nodes['specbsdf'].inputs['Roughness'])
        nodetree.links.new(nodes['normalmix'].outputs['Color'],nodes['Material Output'].inputs['Displacement'])
        nodetree.links.new(nodes['samplingalbedomix'].outputs['Color'], nodes['albedomix'].inputs['Color1'])
    else:
        nodetree.links.new(nodes['samplingalbedomix'].outputs['Color'], nodes['basebsdf'].inputs['Color'])
        nodetree.links.new(nodes['roughnessconcrete'].outputs['Color'], nodes['specbsdf'].inputs['Roughness'])
        nodetree.links.new(nodes['normalconcrete'].outputs['Color'], nodes['Material Output'].inputs['Displacement'])
    #now we need to uv unwrap over the entire mesh
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    
def render(filepath, frames=1, samples=6):
    bpy.data.scenes['Scene'].frame_end =frames
    bpy.data.scenes['Scene'].render.filepath = filepath
    bpy.data.scenes['Scene'].cycles.samples = samples
    bpy.data.scenes['Scene'].render.resolution_x=2048
    bpy.data.scenes['Scene'].render.resolution_y=2048
    bpy.data.scenes['Scene'].render.resolution_percentage=100
    # before rendering, set the sceen camera to the camera that you created
    bpy.data.scenes['Scene'].camera=bpy.data.objects['Camera']

    '''
    # Commented code can later potentially be used to get the result directly from the CompositorLayer 
    # and pipe convert and reshape it into a numpy array
    # switch on nodes
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    
    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = 185, 285
    
    # create output node
    v = tree.nodes.new('CompositorNodeViewer')
    v.location = 750, 210
    v.use_alpha = False
    
    # Links
    links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input
    '''

    bpy.ops.render.render(write_still=True)

    '''
    # get viewer pixels
    pixels = bpy.data.images['Viewer Node'].pixels
    print(len(pixels))  # size is always width * height * 4 (rgba)
    
    # copy buffer to numpy array for faster manipulation
    arr = np.array(pixels)
    print(arr.shape)
    arr = arr.reshape((2048, 2048, 4))
    print(arr.shape)
    
    import scipy.misc
    
    scipy.misc.imsave('outputfile.png', arr)
    '''
	
def rendergt(filepath, frames=1, samples=6):
    bpy.data.scenes['Scene'].frame_end =frames
    bpy.data.scenes['Scene'].render.filepath = filepath
    bpy.data.scenes['Scene'].cycles.samples = samples
    bpy.data.scenes['Scene'].render.resolution_x=2048
    bpy.data.scenes['Scene'].render.resolution_y=2048
    bpy.data.scenes['Scene'].render.resolution_percentage=100
    # before rendering, set the sceen camera to the camera that you created
    bpy.data.scenes['Scene'].camera=bpy.data.objects['Camera']

    nodetree = bpy.data.materials['concrete'].node_tree  # required for linking
    nodes = bpy.data.materials['concrete'].node_tree.nodes
    nodes.new('ShaderNodeEmission')
    nodes['Emission'].name = 'emit1'
    nodes['emit1'].location=[450,-100]
    nodetree.links.new(nodes['emit1'].inputs['Color'],nodes['albedocrack'].outputs['Color'])
    nodetree.links.new(nodes['emit1'].outputs['Emission'],nodes['Material Output'].inputs['Surface'])

    # remove displacement links
    for l in nodes['Material Output'].inputs['Displacement'].links:
        nodetree.links.remove(l)
    bpy.ops.render.render(write_still=True)
	

def rendernp(filepath, frames=1, samples=6):
    bpy.data.scenes['Scene'].frame_end =frames
    bpy.data.scenes['Scene'].render.filepath = filepath
    bpy.data.scenes['Scene'].cycles.samples = samples
    bpy.data.scenes['Scene'].render.resolution_x=2048
    bpy.data.scenes['Scene'].render.resolution_y=2048
    bpy.data.scenes['Scene'].render.resolution_percentage=100
    # before rendering, set the sceen camera to the camera that you created
    bpy.data.scenes['Scene'].camera=bpy.data.objects['Camera']

    nodetree = bpy.data.materials['concrete'].node_tree  # required for linking
    nodes = bpy.data.materials['concrete'].node_tree.nodes
    if cracked:
        nodetree.links.new(nodes['emit1'].inputs['Color'],nodes['normalmix'].outputs['Color'])
    else:
        nodes.new('ShaderNodeEmission')
        nodes['Emission'].name = 'emit1'
        nodes['emit1'].location = [450, -100]
        nodetree.links.new(nodes['emit1'].outputs['Emission'], nodes['Material Output'].inputs['Surface'])
        nodetree.links.new(nodes['emit1'].inputs['Color'], nodes['normalconcrete'].outputs['Color'])
        for l in nodes['Material Output'].inputs['Displacement'].links:
            nodetree.links.remove(l)
    bpy.ops.render.render(write_still=True)


def sampleandrender(nsamples = 100):
    hval = np.random.normal(0.5, 0.3, size=(nsamples))
    sval = np.random.normal(0.5, 0.3, size=(nsamples))
    hval = np.clip(hval, 0, 1)
    sval = np.clip(sval, 0, 1)
    vval = np.empty(nsamples,dtype='float64')
    vval.fill(0.529)
    locationx = np.random.uniform(0, 1, size=(nsamples))
    locationy = np.random.uniform(0, 1, size=(nsamples))
    locationz = np.random.uniform(0, 1, size=(nsamples))
    rotationx = np.random.uniform(0, 20, size=(nsamples))
    rotationy = np.random.uniform(0, 20, size=(nsamples))
    rotationz = np.random.uniform(0, 20, size=(nsamples))
    scalex = np.random.uniform(0.25, 2, size=(nsamples))
    scaley = np.random.uniform(0.25, 2, size=(nsamples))
    scalez = np.random.uniform(0.25, 2, size=(nsamples))
    for i in range(nsamples):
        albedoval = [hval[i],sval[i],vval[i]]
        locationval = [locationx[i],locationy[i],locationz[i]]
        rotationval = [rotationx[i], rotationy[i], rotationz[i]]
        scaleval = [scalex[i], scaley[i], scalez[i]]
        # remove existing objects present in the scene
        removeexistingobjects()
        # modify existing camera
        camerasettings()
        # modify existing light source
        lightsource()
        # master shader for material with mesh
        mastershader(albedoval,locationval,rotationval,scaleval)
        # render the engine
        render(filepath=os.path.join('testimagesblender/results/out'+str(i)+'.png'), frames=1, samples=6)
        # render groundtruth for crack
        if cracked:
            rendergt(filepath=os.path.join('testimagesblender/groundtruth/gt'+str(i)+'.png'), frames=1, samples=6)
        # render normalmap
            rendernp(filepath=os.path.join('testimagesblender/normalmaps/np'+str(i)+'.png'), frames=1, samples=6)
        else:
            rendernp(filepath=os.path.join('testimagesblender/normalmaps/np' + str(i) + '.png'), frames=1, samples=6)


if __name__ == "__main__": 
    #ensure that cycles engine is set for the basic scene. predefined object name for scene is 'Scene'. Also can be accesed by index 0.
    bpy.data.scenes['Scene'].render.engine='CYCLES'
    # check if mode is object mode else set it to object mode
    checkmode = bpy.context.active_object.mode
    if checkmode!='OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # if you are running from blender text editor uncomment below line and link blenderpython folder properly here
    sampleandrender(nsamples=1)

	
	
   
