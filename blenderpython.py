import bpy
import numpy as np
import math
from PIL import Image

def removeexistingmesh():
    # remove pre-existing cube from blender
    for object in bpy.data.objects:
        if object.type == 'MESH':
            object.select = True
        else:
            object.select = False
    bpy.ops.object.delete()
    # clear mesh and material data. removing objects alone is not necessary
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
        
def camerasettings():
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
    # changed default light source from point to sun based on application.
    # 0 index for predefined light source which is present as part of blender and of type='POINT'
    bpy.data.lamps[0].type = 'SUN'
    # change sun location. 
    bpy.data.objects['Lamp'].location = [0.0,-5.0,5.0]
    
    
    # note the default object name for lamps is 'Lamp'. This can be modified. similarly default lamps name is also 'Lamp'
    # you can modify objects or lamps name. example for lamp or object name change given below. uncomment if needed. 
    # if uncommented upcoming commands should also be modified accordingly
    #bpy.data.lamps[0].name = 'Sun'
    #bpy.data.objects['Lamp'].name = 'Sun'
    # you can add more light sources. uncomment below line for example light source 
    #bpy.ops.object.lamp_add(type='POINT')
    
    
    # change rotation of sun's direction vector. 
    bpy.data.objects['Lamp'].rotation_euler=[59*math.pi/180,0.0,0.0]
    # in order to change color, strength of sun, we have to use nodes. also node editing is quite useful for designing layers to your rendering
    bpy.data.lamps['Lamp'].use_nodes=True
    # in the above statement we used 'Lamp' instead of index 0. The default name of lamps is 'Lamp' as described in the above comments.
    
    # set color and strength value of sun using nodes.
    bpy.data.lamps['Lamp'].node_tree.nodes['Emission'].inputs['Color'].default_value = [1.0,1.0,1.0,1.0]
    bpy.data.lamps['Lamp'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 3.0

def mastershader():
    # add a base primitive mesh. in this case a plane mesh is added at origin 
    bpy.ops.mesh.primitive_plane_add(location=(0,0,0))
    # default object name is 'Plane'. or index 2 in this case
    # set scale and rotation
    bpy.data.objects['Plane'].scale=[10.0,10.0,10.0]
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
    nodes['Diffuse BSDF'].name = 'basebsdf1'
    nodes['Glossy BSDF'].name = 'specbsdf1'
    nodes.new('ShaderNodeMixShader')
    nodes['Mix Shader'].name='mixshader1'
    
    nodes['basebsdf1'].inputs['Roughness'].default_value = 0.601 # based on curet database https://wiki.blender.org/index.php/User:Guiseppe/Oren_Nayar
    
    # you can modify nodes location from the script. useful for viewing in node editor. This is mainly for viewing easily.
    nodes['Material Output'].location=[650,300]
    nodes['mixshader1'].location=[450,100]
    nodes.new('ShaderNodeFresnel')
    nodes['Fresnel'].name='fresnel1'
    nodes['fresnel1'].location=[200,500]
    
    # Now to link node inputs and outputs
    nodetree.links.new(nodes['basebsdf1'].outputs['BSDF'],nodes['mixshader1'].inputs[1]) # index 1 corresponds to mix shader's shader input 1
    nodetree.links.new(nodes['specbsdf1'].outputs['BSDF'],nodes['mixshader1'].inputs[2])
    nodetree.links.new(nodes['fresnel1'].outputs[0],nodes['mixshader1'].inputs[0])
    nodetree.links.new(nodes['mixshader1'].outputs[0],nodes['Material Output'].inputs['Surface'])
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name='imagetex1' #albedo map1
    nodes['imagetex1'].location=[-400,300]
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name='imagetex2' #roughness map1
    nodes['imagetex2'].location=[-400,0]
    nodes.new('ShaderNodeTexImage')
    nodes['Image Texture'].name='imagetex3' #normal map1
    nodes['imagetex3'].location=[-400,-300]
    
    #link images to imagetexture node
    bpy.ops.image.open(filepath='/home/sreenivas/Downloads/pockedconcrete1/albedo.png') #first open image to link
    nodes['imagetex1'].image=bpy.data.images['albedo.png']
    bpy.ops.image.open(filepath='/home/sreenivas/Downloads/pockedconcrete1/roughness.png')
    nodes['imagetex2'].image=bpy.data.images['roughness.png']
    bpy.ops.image.open(filepath='/home/sreenivas/Downloads/pockedconcrete1/normal.png')
    nodes['imagetex3'].image=bpy.data.images['normal.png']
    
    #link albedo, roughness and normal maps to color, roughness displacement.
    nodetree.links.new(nodes['imagetex1'].outputs['Color'],nodes['basebsdf1'].inputs['Color'])
    nodetree.links.new(nodes['imagetex1'].outputs['Color'],nodes['specbsdf1'].inputs['Color'])
    nodetree.links.new(nodes['imagetex2'].outputs['Color'],nodes['specbsdf1'].inputs['Roughness'])
    nodetree.links.new(nodes['imagetex3'].outputs['Color'],nodes['Material Output'].inputs['Displacement'])
    
    ## for cracks add more nodes and combine it with the above existing normal map.  
    
    #now we need to uv unwrap over the entire mesh
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    
def render(filepath, frames=1, samples=10):
	bpy.data.scenes['Scene'].frame_end =frames
	bpy.data.scenes['Scene'].render.filepath = filepath
	bpy.data.scenes['Scene'].cycles.samples = samples
	bpy.ops.render.render(animation=True)
    
    
        
if __name__ == "__main__":
    # ensure that cycles engine is set for the basic scene. predefined object name for scene is 'Scene'. Also can be accesed by index 0.
    bpy.data.scenes['Scene'].render.engine='CYCLES'
    # remove existing mesh present in the scene
    removeexistingmesh()
    # modify existing camera
    camerasettings()
    # modify existing light source
    lightsource()
    # master shader for material with mesh
    mastershader()
    # render the engine
    render(filepath='/home/sreenivas/renderedimagesnew/', frames=1, samples=10)
    