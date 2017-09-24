import bpy
import colorsys
import math
import numpy as np

from lib.mastershader import MasterShader
from lib.fractalcracks import generate_fractal_cracks

import cv2


class CrackShader(MasterShader):
    def __init__(self, materialName, albedoTexPath, roughnessTexPath, normalTexPath, resolution,
        albedoval=[0.5, 0.5, 0.5], locationval=[0, 0, 0], rotationval=[0, 0, 0], scaleval=[1, 1, 1]):
        super(CrackShader, self).__init__(materialName, albedoTexPath, roughnessTexPath, normalTexPath, albedoval, locationval, rotationval, scaleval);

        self.resolution = resolution;

        self._setup();


    def _setup(self):
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'albedocrack' #albedo crack
        self._nodes['albedocrack'].location = [-600, 300]
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'roughnesscrack' #roughness crack
        self._nodes['roughnesscrack'].location = [-600, -300]
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'normalcrack' #normal crack
        self._nodes['normalcrack'].location = [-600, -900]

        generated_maps = []
        # generate crack maps
        print(cv2.imread(self.albedoTexPath).shape);
        generated_maps[0:2] = (generate_fractal_cracks(self.resolution, 7))
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
        imgT_albedo = bpy.data.images.new("albedo_image", width=self.resolution, height=self.resolution)
        imgT_roughness = bpy.data.images.new("roughness_image", width=self.resolution, height=self.resolution)
        imgT_normals = bpy.data.images.new("normals_image", width=self.resolution, height=self.resolution)

        # flatten the arrays and assign them to the place-holder textures
        imgT_albedo.pixels = generated_maps[0].flatten().tolist()
        imgT_roughness.pixels = generated_maps[1].flatten().tolist()
        imgT_normals.pixels = generated_maps[2].flatten().tolist()

        # feed new texture into appropriate nodes
        self._nodes['albedocrack'].image = imgT_albedo
        self._nodes['roughnesscrack'].image = imgT_roughness
        self._nodes['normalcrack'].image = imgT_normals

        # create mix rgb nodes to mix crack maps and original image pbr maps
        self._nodes.new('ShaderNodeMixRGB')
        self._nodes['Mix'].name = 'albedomix'
        self._nodes['albedomix'].location = [-400, 450]
        self._nodes.new('ShaderNodeMixRGB')
        self._nodes['Mix'].name = 'roughnessmix'
        self._nodes['roughnessmix'].location = [-400, -150]
        self._nodes.new('ShaderNodeMixRGB')
        self._nodes['Mix'].name = 'normalmix'
        self._nodes['normalmix'].location = [-400, -750]

        # link crack and original map nodes to mixrgb
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['albedomix'].inputs[1])
        self._nodetree.links.new(self._nodes['albedocrack'].outputs['Color'], self._nodes['albedomix'].inputs[2])
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'], self._nodes['roughnessmix'].inputs[1])
        self._nodetree.links.new(self._nodes['roughnesscrack'].outputs['Color'], self._nodes['roughnessmix'].inputs[2])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmix'].inputs[1])
        self._nodetree.links.new(self._nodes['normalcrack'].outputs['Color'], self._nodes['normalmix'].inputs[2])

        # add appropriate factors for scaling mixrgb nodes
        self._nodetree.links.new(self._nodes['albedocrack'].outputs['Alpha'], self._nodes['albedomix'].inputs[0])
        # value for albedomix comes for crack map alpha
        self._nodes['roughnessmix'].inputs[0].default_value = 0.25
        self._nodes['normalmix'].inputs[0].default_value = 0.75

        #link albedo, roughness and normal mixrgb maps to color, roughness displacement.
        self._nodetree.links.new(self._nodes['albedomix'].outputs['Color'], self._nodes['basebsdf'].inputs['Color'])
        self._nodetree.links.new(self._nodes['roughnessmix'].outputs['Color'], self._nodes['specbsdf'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalmix'].outputs['Color'], self._nodes['Material Output'].inputs['Displacement'])
        self._nodetree.links.new(self._nodes['samplingalbedomix'].outputs['Color'], self._nodes['albedomix'].inputs['Color1'])