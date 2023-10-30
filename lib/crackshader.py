import bpy

import numpy as np

from lib.mastershader import MasterShader
from lib.fractalcracks import generate_fractal_cracks

class CrackShader(MasterShader):
    def __init__(self, material_name, albedo_tex_path, roughness_tex_path, normal_tex_path,
                 height_tex_path, resolution):
        super(CrackShader, self).__init__(material_name, albedo_tex_path, roughness_tex_path,
                                          normal_tex_path, height_tex_path)

        self.resolution = resolution

        self._setup()

    def _setup(self):
        print("Crackshader Setup")
        self._nodes.new('ShaderNodeTexImage')
        # TODO: Rename all albedo crack to groundtruth crack
        self._nodes['Image Texture'].name = 'albedocrack'  # albedo crack
        self._nodes['albedocrack'].location = [-600, 300]
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'roughnesscrack'  # roughness crack
        self._nodes['roughnesscrack'].location = [-600, -300]
        self._nodes['roughnesscrack'].color_space = 'NONE'
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'normalcrack'  # normal crack
        self._nodes['normalcrack'].color_space = 'NONE'
        self._nodes['normalcrack'].location = [-600, -900]
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'heightcrack'
        self._nodes['heightcrack'].color_space = 'NONE'
        self._nodes['heightcrack'].location = [-600, -1200]

        img_tex_albedo, img_tex_roughness, img_tex_normals, img_tex_heights = self._generate_fractal_crack_maps()

        # feed new texture into appropriate nodes
        self._nodes['albedocrack'].image = img_tex_albedo
        self._nodes['roughnesscrack'].image = img_tex_roughness
        self._nodes['normalcrack'].image = img_tex_normals
        self._nodes['heightcrack'].image = img_tex_heights

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

        # self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmix'].inputs[1])
        # self._nodetree.links.new(self._nodes['normalcrack'].outputs['Color'], self._nodes['normalmix'].inputs[2])

        # link albedo, roughness and normal mixrgb maps to color, roughness displacement.
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['pbr'].inputs[0])
        self._nodetree.links.new(self._nodes['roughnessmix'].outputs['Color'], self._nodes['pbr'].inputs['Roughness'])
        # self._nodetree.links.new(self._nodes['normalmix'].outputs['Color'], self._nodes['normalmapconcrete'].inputs[1])

        # TODO: Check if roughness maps and normal maps need to be mixed when we use height maps
        # self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'], self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmapconcrete'].inputs[1])

        self._nodetree.links.new(self._nodes['normalmapconcrete'].outputs[0], self._nodes['pbr'].inputs['Normal'])
        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])

    def _generate_fractal_crack_maps(self):
        generated_maps = []
        # generate crack maps
        # TODO: uncomment below line and comment line after if fractal crack generation code is parallelized in GPU
        # fractal_depth = int(np.log2(self.resolution) + 1)
        # TODO: hardcoded
        fractal_depth = 7
        generated_maps[0:3] = (generate_fractal_cracks(self.resolution, fractal_depth))
        # order is: ground truth, roughness, normals and height map
        # for each map check whether it already has an alpha channel, i.e. the albedo map should have one
        # for all other maps add an alpha channel that is filled with ones
        for i in range(0, len(generated_maps)):
            # last shape index is amount of color channels
            if generated_maps[i].shape[-1] != 4:
                tmp = np.zeros((generated_maps[i].shape[0], generated_maps[i].shape[1], 4))  # place-holder
                tmp[:, :, 0:3] = generated_maps[i]  # copy old 3 channels
                tmp[:, :, 3] = 1  # fill 4. alpha channel
                generated_maps[i] = tmp  # copy back

        # initialize empty texture structures of corresponding size
        img_tex_albedo = bpy.data.images.new("albedo_image", width=self.resolution, height=self.resolution)
        img_tex_roughness = bpy.data.images.new("roughness_image", width=self.resolution, height=self.resolution)
        img_tex_normals = bpy.data.images.new("normals_image", width=self.resolution, height=self.resolution)
        img_tex_heights = bpy.data.images.new("heights_image", width=self.resolution, height=self.resolution)

        # flatten the arrays and assign them to the place-holder textures
        img_tex_albedo.pixels = generated_maps[0].flatten().tolist()
        img_tex_roughness.pixels = generated_maps[1].flatten().tolist()
        img_tex_normals.pixels = generated_maps[2].flatten().tolist()
        img_tex_heights.pixels = generated_maps[3].flatten().tolist()

        return img_tex_albedo, img_tex_roughness, img_tex_normals, img_tex_heights

    def set_shader_mode_gt(self):
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['albedocrack'].outputs['Color'])
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'],
                                 self._nodes['Material Output'].inputs['Surface'])

        # remove displacement links
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)

    def set_shader_mode_normal(self):
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['albedocrack'].outputs['Color'])
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'],
                                 self._nodes['Material Output'].inputs['Surface'])

        # remove displacement links
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)

        # TODO: with lighting currently being calculated from displacement map, this is inaccurate.
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['normalmix'].outputs['Color'])

    def set_shader_mode_color(self):
        # link crack and original map nodes to mixrgb
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'],
                                 self._nodes['roughnessmix'].inputs[1])
        self._nodetree.links.new(self._nodes['roughnesscrack'].outputs['Color'], self._nodes['roughnessmix'].inputs[2])

        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmix'].inputs[1])
        self._nodetree.links.new(self._nodes['normalcrack'].outputs['Color'], self._nodes['normalmix'].inputs[2])

        # link albedo, roughness and normal mixrgb maps to color, roughness displacement
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'], self._nodes['pbr'].inputs[0])
        self._nodetree.links.new(self._nodes['roughnessmix'].outputs['Color'], self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'], self._nodes['normalmapconcrete'].inputs[1])
        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])

    def _load_images_to_textures_nodes(self):
        img_tex_albedo, img_tex_roughness, img_tex_normals, img_tex_heights = self._generate_fractal_crack_maps()

        # feed new texture into appropriate nodes
        self._nodes['albedocrack'].image = img_tex_albedo
        self._nodes['roughnesscrack'].image = img_tex_roughness
        self._nodes['normalcrack'].image = img_tex_normals
        self._nodes['heightcrack'].image = img_tex_heights
        # albedo map
        bpy.data.images.load(filepath=self.albedoTexPath)
        self._nodes['albedoconcrete'].image = bpy.data.images[self.albedoTexPath.split("/")[-1]]

        # roughness map
        bpy.data.images.load(filepath=self.roughnessTexPath)
        self._nodes['roughnessconcrete'].image = bpy.data.images[self.roughnessTexPath.split("/")[-1]]

        # normal map
        bpy.data.images.load(filepath=self.normalTexPath)
        self._nodes['normalconcrete'].image = bpy.data.images[self.normalTexPath.split("/")[-1]]

        # height map
        # TODO: This needs to go into the displacement modifier of the mesh!!!
        bpy.data.images.load(filepath=self.heightTexPath)
        # TODO: Height tex path being assigned to an image in a improper way. Needs to be fixed.
        self._nodes['heightconcrete'].image = bpy.data.images[self.heightTexPath.split("/")[-1]]
        # TODO: returning height texture path so that it can be used for displacement of mesh. This is an imroper fix.
        #img_tex_albedo, img_tex_roughness, img_tex_normals, img_tex_heights = self._generate_fractal_crack_maps()
        return self.heightTexPath.split("/")[-1], img_tex_heights

    # Override(MasterShader)
    def sample_texture(self):
        # TODO: returning height texture path so that it can be used for displacement of mesh. This is an imroper fix.
        heightTexturePath, img_tex_heights = self._load_images_to_textures_nodes()
        return heightTexturePath, img_tex_heights
