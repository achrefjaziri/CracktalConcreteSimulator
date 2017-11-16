import bpy
import colorsys
import math
import numpy as np

from lib.mastershader import MasterShader
from lib.fractalcracks import generate_fractal_cracks

import cv2


class CrackShader(MasterShader):
    def __init__(self, materialName, albedoTexPath, roughnessTexPath, normalTexPath, resolution):
        super(CrackShader, self).__init__(materialName, albedoTexPath, roughnessTexPath, normalTexPath)

        self.resolution = resolution

        self._setup()


    def _setup(self):
        print("Crackshader Setup");
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'albedocrack' #albedo crack
        self._nodes['albedocrack'].location = [-600, 300]
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'roughnesscrack' #roughness crack
        self._nodes['roughnesscrack'].location = [-600, -300]
        self._nodes['roughnesscrack'].color_space = 'NONE'
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'normalcrack' #normal crack
        self._nodes['normalcrack'].color_space = 'NONE'
        self._nodes['normalcrack'].location = [-600, -900]

        imgT_albedo, imgT_roughness, imgT_normals = self._generateFractalCrackMaps();

        # feed new texture into appropriate nodes
        self._nodes['albedocrack'].image = imgT_albedo
        self._nodes['roughnesscrack'].image = imgT_roughness
        self._nodes['normalcrack'].image = imgT_normals

        # create mix rgb nodes to mix crack maps and original image pbr maps
        self._nodes.new('ShaderNodeMixRGB')
        self._nodes['Mix'].name = 'roughnessmix'
        self._nodes['roughnessmix'].location = [-400, -150]
        self._nodes.new('ShaderNodeMixRGB')
        self._nodes['Mix'].name = 'normalmix'
        self._nodes['normalmix'].location = [-400, -750]


        # add appropriate factors for scaling mixrgb nodes
        self._nodes['roughnessmix'].inputs[0].default_value = 0.5
        self._nodes['normalmix'].inputs[0].default_value = 0.5

        # linking various nodes
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'],
                                 self._nodes['roughnessmix'].inputs[1])
        self._nodetree.links.new(self._nodes['roughnesscrack'].outputs['Color'], self._nodes['roughnessmix'].inputs[2])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmix'].inputs[1])
        self._nodetree.links.new(self._nodes['normalcrack'].outputs['Color'], self._nodes['normalmix'].inputs[2])

        # link albedo, roughness and normal mixrgb maps to color, roughness displacement.
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['pbr'].inputs[0])
        self._nodetree.links.new(self._nodes['roughnessmix'].outputs['Color'], self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalmix'].outputs['Color'], self._nodes['normalmapconcrete'].inputs[1])
        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])



    def _generateFractalCrackMaps(self):
        generated_maps = []
        # generate crack maps
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

        return imgT_albedo, imgT_roughness, imgT_normals;

    def _sampleCrack(self):
        imgT_albedo, imgT_roughness, imgT_normals = self._generateFractalCrackMaps();

        # feed new texture into appropriate nodes
        self._nodes['albedocrack'].image = imgT_albedo
        self._nodes['roughnesscrack'].image = imgT_roughness
        self._nodes['normalcrack'].image = imgT_normals


    def set_shader_mode_gt(self):
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['albedocrack'].outputs['Color'])
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'], self._nodes['Material Output'].inputs['Surface'])

        # remove displacement links
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)

    def set_shader_mode_normal(self):
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['albedocrack'].outputs['Color'])
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'], self._nodes['Material Output'].inputs['Surface'])

        # remove displacement links
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)

        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['normalmix'].outputs['Color'])

    def set_shader_mode_color(self):
        # link crack and original map nodes to mixrgb
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'],
                                 self._nodes['roughnessmix'].inputs[1])
        self._nodetree.links.new(self._nodes['roughnesscrack'].outputs['Color'], self._nodes['roughnessmix'].inputs[2])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmix'].inputs[1])
        self._nodetree.links.new(self._nodes['normalcrack'].outputs['Color'], self._nodes['normalmix'].inputs[2])

        #link albedo, roughness and normal mixrgb maps to color, roughness displacement.
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['pbr'].inputs[0])
        self._nodetree.links.new(self._nodes['roughnessmix'].outputs['Color'], self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalmix'].outputs['Color'], self._nodes['normalmapconcrete'].inputs[1])
        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])

    #Override(MasterShader)
    def sample_texture(self):
        self._sampleCrack();
        
        self._load_images_to_textures_nodes();

