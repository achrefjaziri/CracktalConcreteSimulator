import bpy
import colorsys
import math
import numpy as np
import time

class MasterShader():

    def __init__(self, materialName, albedoTexPath, roughnessTexPath, normalTexPath, albedoval=[0.5, 0.5, 0.5], locationval=[0, 0, 0], rotationval=[0, 0, 0], scaleval=[1, 1, 1]):
        self.name = materialName;
        self.albedoTexPath = albedoTexPath;
        self.roughnessTexPath = roughnessTexPath;
        self.normalTexPath = normalTexPath;

        self.scalevals = scaleval;
        self.locationvals = locationval;
        self.rotationvals = rotationval;

        self.albedovals = albedoval;


        self._nodetree = None;
        self._nodes = None;

        self.__setup();


    def __setup(self):
        print("mastershader setup")
        bpy.ops.material.new()
        
        bpy.data.materials['Material'].name = self.name
        # TODO: do this with extra functionality!!!!!
        # link material to the plane mesh
        #bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete']

        # SETUP SHADER STRUCTURE WITH NODES
        bpy.data.materials[self.name].use_nodes = True

        self._nodetree = bpy.data.materials[self.name].node_tree  # required for linking
        self._nodes = bpy.data.materials[self.name].node_tree.nodes

        self._nodes.new('ShaderNodeBsdfGlossy') # give names for nodes for easy understanding
        self._nodes['Diffuse BSDF'].name = 'basebsdf'
        self._nodes['Glossy BSDF'].name = 'specbsdf'

        self._nodes.new('ShaderNodeMixShader')
        self._nodes['Mix Shader'].name = 'mixbasespec'
        self._nodes['basebsdf'].inputs['Roughness'].default_value = 0.601 # based on curet database https://wiki.blender.org/index.php/User:Guiseppe/Oren_Nayar
        self._nodes['Material Output'].location = [650, 300]
        self._nodes['mixbasespec'].location = [450, 100]
       
        self._nodes.new('ShaderNodeFresnel')
        self._nodes['Fresnel'].name = 'fresnel1'
        self._nodes['fresnel1'].location = [200, 500]

        self._nodetree.links.new(self._nodes['basebsdf'].outputs['BSDF'], self._nodes['mixbasespec'].inputs[1])  # index 1 corresponds to mix shader's shader input 1
        self._nodetree.links.new(self._nodes['specbsdf'].outputs['BSDF'], self._nodes['mixbasespec'].inputs[2])
        self._nodetree.links.new(self._nodes['fresnel1'].outputs[0], self._nodes['mixbasespec'].inputs[0])
        self._nodetree.links.new(self._nodes['mixbasespec'].outputs[0], self._nodes['Material Output'].inputs['Surface'])
        
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'albedoconcrete' #albedo concrete
        self._nodes['albedoconcrete'].location = [-600, 600]

        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'roughnessconcrete' #roughness concrete
        self._nodes['roughnessconcrete'].location = [-600, 0]
        
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'normalconcrete' #normal concrete
        self._nodes['normalconcrete'].location = [-600, -600]

        #self._loadImagesToTextureNodes();

        # random albedo and other map rgb and mix nodes for random sampling
        self._nodes.new('ShaderNodeRGB')
        self._nodes['RGB'].name = 'samplingalbedorgb'
        self._nodes['samplingalbedorgb'].location = [-600, 900]
        
        self._nodes.new('ShaderNodeMapping')
        self._nodes['Mapping'].name = 'samplingmap'
        self._nodes['samplingmap'].location = [-1200, 0]
        self._nodes['samplingmap'].vector_type = 'VECTOR'
        
        self._nodes.new('ShaderNodeVectorMath')
        self._nodes['Vector Math'].operation = 'ADD'
        self._nodes['Vector Math'].name = 'addtranslation'
        self._nodes['addtranslation'].location = [-1500, 0]
        
        self._nodes.new('ShaderNodeRGB')
        self._nodes['RGB'].name = 'samplingtranslationrgb'
        self._nodes['samplingtranslationrgb'].location = [-1800, 0]
        
        self._nodes.new('ShaderNodeTexCoord')
        self._nodes['Texture Coordinate'].name = 'texcoord1'
        self._nodes['texcoord1'].location = [-1800, -300]
        
        self._nodes.new('ShaderNodeMixRGB')
        self._nodes['Mix'].location = [-300, 750]
        self._nodes['Mix'].name = 'samplingalbedomix'
        self._nodes['samplingalbedomix'].inputs['Fac'].default_value = 0.80

        # links for sampling nodes
        self._nodetree.links.new(self._nodes['samplingalbedomix'].inputs['Color1'], self._nodes['samplingalbedorgb'].outputs['Color'])
        self._nodetree.links.new(self._nodes['samplingalbedomix'].inputs['Color2'], self._nodes['albedoconcrete'].outputs['Color'])

        self._nodetree.links.new(self._nodes['samplingmap'].outputs['Vector'], self._nodes['albedoconcrete'].inputs['Vector'])
        self._nodetree.links.new(self._nodes['samplingmap'].outputs['Vector'], self._nodes['roughnessconcrete'].inputs['Vector'])
        self._nodetree.links.new(self._nodes['samplingmap'].outputs['Vector'], self._nodes['normalconcrete'].inputs['Vector'])
        self._nodetree.links.new(self._nodes['addtranslation'].outputs['Vector'], self._nodes['samplingmap'].inputs['Vector'])
        self._nodetree.links.new(self._nodes['addtranslation'].inputs[0], self._nodes['samplingtranslationrgb'].outputs['Color'])
        self._nodetree.links.new(self._nodes['addtranslation'].inputs[1], self._nodes['texcoord1'].outputs['UV'])

        #self._loadParametersToSamplingNodes();

        self._nodetree.links.new(self._nodes['samplingalbedomix'].outputs['Color'], self._nodes['basebsdf'].inputs['Color'])
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'], self._nodes['specbsdf'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['Material Output'].inputs['Displacement'])

        # Emmission Shader Node
        self._nodes.new('ShaderNodeEmission')
        self._nodes['Emission'].name = 'emit1'
        self._nodes['emit1'].location = [450, -100]


    def setShaderModeGT(self):
        pass;


    def setShaderModeNormalMap(self):
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'], self._nodes['Material Output'].inputs['Surface'])
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['normalconcrete'].outputs['Color'])
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)


    def setShaderModeColor(self):
        self._nodetree.links.new(self._nodes['samplingalbedomix'].outputs['Color'], self._nodes['basebsdf'].inputs['Color'])
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'], self._nodes['specbsdf'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['Material Output'].inputs['Displacement'])
        
        self._nodetree.links.new(self._nodes['mixbasespec'].outputs[0], self._nodes['Material Output'].inputs['Surface'])


    def _loadImagesToTextureNodes(self):
        # ALBEDO MAP
        bpy.ops.image.open(filepath=self.albedoTexPath);
        self._nodes['albedoconcrete'].image = bpy.data.images[self.albedoTexPath.split("/")[-1]]
        # ROUGHNESS MAP
        bpy.ops.image.open(filepath=self.roughnessTexPath)
        self._nodes['roughnessconcrete'].image = bpy.data.images[self.roughnessTexPath.split("/")[-1]]
        # NORMAL MAP
        bpy.ops.image.open(filepath=self.normalTexPath)
        self._nodes['normalconcrete'].image = bpy.data.images[self.normalTexPath.split("/")[-1]]


    def _loadParametersToSamplingNodes(self):
        # sampling values passed to the function
        self._nodes['samplingmap'].scale = [self.scalevals[0], self.scalevals[1], self.scalevals[2]]
        self._nodes['samplingmap'].rotation = [self.rotationvals[0] * math.pi / 180, self.rotationvals[1] * math.pi / 180,
                                            self.rotationvals[2] * math.pi / 180]
        # rgb values for albedo change. need to convert hsv to rgb to use it here.
        rgbval = colorsys.hsv_to_rgb(self.albedovals[0], self.albedovals[1], self.albedovals[2])
        self._nodes['samplingalbedorgb'].outputs[0].default_value[0] = rgbval[0]
        self._nodes['samplingalbedorgb'].outputs[0].default_value[1] = rgbval[1]
        self._nodes['samplingalbedorgb'].outputs[0].default_value[2] = rgbval[2]

        # translation sampling
        self._nodes['samplingtranslationrgb'].outputs[0].default_value[0] = self.locationvals[0]
        self._nodes['samplingtranslationrgb'].outputs[0].default_value[1] = self.locationvals[1]
        self._nodes['samplingtranslationrgb'].outputs[0].default_value[2] = self.locationvals[2]
        

    def applyTo(self, blenderObjName):
        currObj = bpy.context.scene.objects[blenderObjName]
        currObj.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        

    def loadTexture(self, albedoPath, roughnessPath, normalPath):
        self.albedoTexPath = albedoPath;
        self.roughnessTexPath = roughnessPath;
        self.normalTexPath = normalPath;


    def sampleTexture(self):
        self._sampleAlbedo();
        self._sampleLocationParameters();

        self._loadImagesToTextureNodes();
        self._loadParametersToSamplingNodes();


    def _sampleAlbedo(self):
        hval = np.random.normal(0.5, 0.3)
        sval = np.random.normal(0.5, 0.3)
        hval = np.clip(hval, 0, 1)
        sval = np.clip(sval, 0, 1)
        vval = np.empty(1, dtype='float64')
        vval.fill(0.529)

        self.albedovals = [hval, sval, vval];


    def _sampleLocationParameters(self):
        # location sampling has to be between 0 and 1 because we are using RGB mixer node for translation
        locationx = np.random.uniform(0, 1)
        locationy = np.random.uniform(0, 1)
        locationz = np.random.uniform(0, 1)
        rotationx = np.random.uniform(0, 15)
        rotationy = np.random.uniform(0, 15)
        rotationz = np.random.uniform(0, 15)
        scalex = np.random.uniform(0.75, 1.25)
        scaley = np.random.uniform(0.75, 1.25)
        scalez = np.random.uniform(0.75, 1.25)

        self.locationvals = [locationx, locationy, locationz]
        self.rotationvals = [rotationx, rotationy, rotationz]
        self.scalevals = [scalex, scaley, scalez]
