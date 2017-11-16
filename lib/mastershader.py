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

        self._nodes['Material Output'].location = [650, 300]

        self._nodes.new('ShaderNodeBsdfPrincipled')
        self._nodes['Principled BSDF'].name = 'pbr'
        self._nodes['pbr'].location = [450,600]

        
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'albedoconcrete' #albedo concrete
        self._nodes['albedoconcrete'].location = [-600, 600]

        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'roughnessconcrete' #roughness concrete
        self._nodes['roughnessconcrete'].location = [-600, 0]
        self._nodes['roughnessconcrete'].color_space = 'NONE'

        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'normalconcrete' #normal concrete
        self._nodes['normalconcrete'].location = [-600, -600]
        self._nodes['normalconcrete'].color_space = 'NONE'

        self._nodes.new('ShaderNodeNormalMap')
        self._nodes['Normal Map'].name = 'normalmapconcrete'
        self._nodes['normalmapconcrete'].location = [-200,-300]
        #self._loadImagesToTextureNodes();


        # Emmission Shader Node for displaying ground truth and normal maps
        self._nodes.new('ShaderNodeEmission')
        self._nodes['Emission'].name = 'emit1'
        self._nodes['emit1'].location = [450, -100]


        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['pbr'].inputs[0])
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'],
                                 self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'],
                                 self._nodes['normalmapconcrete'].inputs[1])
        self._nodetree.links.new(self._nodes['normalmapconcrete'].outputs[0], self._nodes['pbr'].inputs['Normal'])

    def setShaderModeGT(self):
        pass;


    def setShaderModeNormalMap(self):
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'], self._nodes['Material Output'].inputs['Surface'])
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['normalconcrete'].outputs['Color'])
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)





    def _loadImagesToTextureNodes(self):
        # ALBEDO MAP
        bpy.data.images.load(filepath=self.albedoTexPath);
        self._nodes['albedoconcrete'].image = bpy.data.images[self.albedoTexPath.split("/")[-1]]
        # ROUGHNESS MAP
        bpy.data.images.load(filepath=self.roughnessTexPath)
        self._nodes['roughnessconcrete'].image = bpy.data.images[self.roughnessTexPath.split("/")[-1]]
        # NORMAL MAP
        bpy.data.images.load(filepath=self.normalTexPath)
        self._nodes['normalconcrete'].image = bpy.data.images[self.normalTexPath.split("/")[-1]]


        

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
        self._loadImagesToTextureNodes();

    def setShaderModeColor(self):
        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['pbr'].inputs[0])
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'],
                                 self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'],
                                 self._nodes['normalmapconcrete'].inputs[1])
        self._nodetree.links.new(self._nodes['normalmapconcrete'].outputs[0], self._nodes['pbr'].inputs['Normal'])
