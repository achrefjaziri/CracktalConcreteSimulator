import bpy
import time

class MasterShader:

    def __init__(self, material_name, albedo_texture_path, roughness_texture_path,
                 normal_texture_path, height_texture_path,albedo_noise_texture_path):
        print('im in baby !!')
        self.name = material_name
        self.albedoTexPath = albedo_texture_path
        self.roughnessTexPath = roughness_texture_path
        self.normalTexPath = normal_texture_path
        self.heightTexPath = height_texture_path
        self.albedoNoisePath = albedo_noise_texture_path

        self._nodetree = None
        self._nodes = None

        self.__setup()

    def __setup(self):
        print("mastershader setup")
        bpy.ops.material.new()
        
        bpy.data.materials['Material'].name = self.name
        # TODO: do this with extra functionality!!!!!

        # Setup shader structure with nodes
        bpy.data.materials[self.name].use_nodes = True

        self._nodetree = bpy.data.materials[self.name].node_tree  # required for linking
        self._nodes = bpy.data.materials[self.name].node_tree.nodes

        self._nodes['Material Output'].location = [650, 300]

        self._nodes.new('ShaderNodeBsdfPrincipled')
        self._nodes['Principled BSDF'].name = 'pbr'
        self._nodes['pbr'].location = [450, 600]
        # inputs[5] is specular value
        self._nodes['pbr'].inputs[5].default_value = 0.0

        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'albedoconcrete'  # albedo concrete
        self._nodes['albedoconcrete'].location = [-600, 600]

        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'roughnessconcrete'  # roughness concrete
        self._nodes['roughnessconcrete'].location = [-600, 0]
        self._nodes['roughnessconcrete'].color_space = 'NONE'

        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'normalconcrete'  # normal concrete
        self._nodes['normalconcrete'].location = [-600, -600]
        self._nodes['normalconcrete'].color_space = 'NONE'

        self._nodes.new('ShaderNodeNormalMap')
        self._nodes['Normal Map'].name = 'normalmapconcrete'
        self._nodes['normalmapconcrete'].location = [-200, -300]

        # TODO: height texture image node created. Check if this is necessary
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'heightconcrete'  # normal concrete
        self._nodes['heightconcrete'].location = [-600, -900]
        self._nodes['heightconcrete'].color_space = 'NONE'

        # Emmission Shader Node for displaying ground truth and normal maps
        self._nodes.new('ShaderNodeEmission')
        self._nodes['Emission'].name = 'emit1'
        self._nodes['emit1'].location = [450, -100]
        print('setting shader node')

        #Shader node for displaying Graffiti, moss etc..
        self._nodes.new('ShaderNodeTexImage')
        self._nodes['Image Texture'].name = 'albedonoise'  # albedo noise
        self._nodes['albedonoise'].location = [-600, 900]
        print('setting mix node')

        # create mix rgb nodes to mix noise map and original image pbr maps
        mix =self._nodes.new('ShaderNodeMixRGB')
        mix.name = 'albedomix'
        mix.location = [-200, 750]
        mix.blend_type = 'MIX'


        # add appropriate factors for scaling mixrgb nodes
        #self._nodes['albedomix'].inputs[0].default_value = 0.5

    def set_shader_mode_gt(self):
        pass

    def set_shader_mode_normal(self):
        self._nodetree.links.new(self._nodes['emit1'].outputs['Emission'],
                                 self._nodes['Material Output'].inputs['Surface'])
        self._nodetree.links.new(self._nodes['emit1'].inputs['Color'], self._nodes['normalconcrete'].outputs['Color'])
        for l in self._nodes['Material Output'].inputs['Displacement'].links:
            self._nodetree.links.remove(l)

    def set_shader_mode_color(self):

        print('color mode!!')
        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])

        self._nodetree.links.new(self._nodes['pbr'].outputs[0], self._nodes['Material Output'].inputs['Surface'])
        print('first link')
        self._nodetree.links.new(self._nodes['albedoconcrete'].outputs['Color'],
                                 self._nodes['albedomix'].inputs[1])
        print('second link')
        self._nodetree.links.new(self._nodes['albedonoise'].outputs['Color'],
                                 self._nodes['albedomix'].inputs[2])
        self._nodetree.links.new(self._nodes['albedonoise'].outputs['Alpha'],
                                 self._nodes['albedomix'].inputs[0])
        print('third link')
        self._nodetree.links.new(self._nodes['albedomix'].outputs['Color'], self._nodes['pbr'].inputs[0])
        print('back to roughness and stuff')
        self._nodetree.links.new(self._nodes['roughnessconcrete'].outputs['Color'],
                                 self._nodes['pbr'].inputs['Roughness'])
        self._nodetree.links.new(self._nodes['normalconcrete'].outputs['Color'],
                                 self._nodes['normalmapconcrete'].inputs[1])
        self._nodetree.links.new(self._nodes['normalmapconcrete'].outputs[0], self._nodes['pbr'].inputs['Normal'])
        print("This prints once a minute.")
        time.sleep(600)
    def _load_images_to_textures_nodes(self):
        print("load texture to nodes")
        # albedo map
        bpy.data.images.load(filepath=self.albedoTexPath)
        self._nodes['albedoconcrete'].image = bpy.data.images[self.albedoTexPath.split("/")[-1]]
        print('loading noise texture')
        #albedo noise
        bpy.data.images.load(filepath=self.albedoNoisePath)
        self._nodes['albedonoise'].image = bpy.data.images[self.albedoNoisePath.split("/")[-1]]
        print("load albdo texture",self.albedoNoisePath.split("/")[-1])
        print("albedo images1",self._nodes['albedonoise'].image )
        print("albedo images1",self._nodes['albedoconcrete'].image )
        time.sleep(600)

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
        # TODO: returning height texture path so that it can be used for displacement of mesh. This is an improper fix.
        return self.heightTexPath.split("/")[-1]

    def apply_to_blender_object(self, blender_obj):
        blender_obj.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # introduce mesh displacement based on loaded height map
        #self._displace(curr_obj)

    """
    def _displace(self, blender_obj, disp_strength=1): #disp_strength=0.05):
        # load the height map and assign it to the displacement modifier's texture
        bpy.data.textures['displacement'].image = bpy.data.images[self.heightTexPath.split("/")[-1]]
        blender_obj.modifiers['Displace'].texture = bpy.data.textures['displacement']

        # Blender's default value is strange and displaces way too much.
        # Advise is to keep the value below 0.1
        blender_obj.modifiers['Displace'].strength = disp_strength
    """

    def load_texture(self, albedo_path, roughness_path, normal_path, height_path, albedo_noise_path):
        self.albedoTexPath = albedo_path
        self.roughnessTexPath = roughness_path
        self.normalTexPath = normal_path
        self.heightTexPath = height_path
        self.albedoNoisePath = albedo_noise_path

    def sample_texture(self):
        # TODO: returning height texture path so that it can be used for displacement of mesh. This is an imroper fix.
        heightTexturePath = self._load_images_to_textures_nodes()
        return heightTexturePath
