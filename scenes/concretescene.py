import bpy
import math
import os

from lib.scene import Scene
from lib.crackshader import CrackShader
from lib.mastershader import MasterShader
from lib.meshmodifiers import MeshDisplacement

class ConcreteScene(Scene):
    def __init__(self, resolution, is_cracked, path):
        # attributes of the scene used in setup need to be called before parent init!
        # otherwise they are not known to the overrinding function!
        self.resolution = resolution

        self.isCracked = is_cracked

        self.DisplacedMesh = None

        self.pathname = path
        super(ConcreteScene, self).__init__()

    # Override(Scene)
    def _setup_camera(self):
        # add camera
        bpy.ops.object.camera_add()
        # location of camera
        bpy.data.objects['Camera'].location = (0.0, -15.0, 2.0)
        # rotation of camera. x axis rotation is 105.125 degrees in this example
        bpy.data.objects['Camera'].rotation_euler = [105.125*math.pi/180, 0.0, 0.0]
        # scale of camera usually unaltered
        bpy.data.objects['Camera'].scale = [1.0, 1.0, 1.0]
        # focal length of camera
        bpy.data.cameras['Camera'].lens = 35.00
        # focal length unit
        bpy.data.cameras['Camera'].lens_unit = 'MILLIMETERS'

    # Override(Scene)
    def _setup_lighting(self):
        # add light source
        bpy.ops.object.lamp_add(type='SUN')
        # change sun location
        bpy.data.objects['Sun'].location = [0.0, -5.0, 5.0]
        # change rotation of sun's direction vector.
        bpy.data.objects['Sun'].rotation_euler = [59*math.pi/180, 0.0, 0.0]

        # use nodes for blackbody
        bpy.data.lamps['Sun'].use_nodes = True

        # set color from temperature and light intensity
        bpy.data.lamps['Sun'].node_tree.nodes.new("ShaderNodeBlackbody")
        # use a blackbody emission node for the sun and set the temperature
        bpy.data.lamps['Sun'].node_tree.nodes['Blackbody'].inputs['Temperature'].default_value = 6500
        bpy.data.lamps['Sun'].node_tree.links.new(bpy.data.lamps['Sun'].node_tree.nodes['Blackbody'].outputs['Color'],
                                                  bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Color'])
        bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 3.3

    """
    def _add_modifiers(self, blender_obj):
        # select given object
        blender_obj.select = True

        # displacement modifier
        # TODO: displacement modifier not getting updated.
        # Need a remove & add modifier handle
        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.data.textures.new('displacement', type='IMAGE')
    """

    # Override(Scene)
    def _setup_objects(self):
        # add a base primitive mesh. in this case a plane mesh is added at the origin
        bpy.ops.mesh.primitive_plane_add(location=(0.0, -2.0, 5.5))
        # default object name is 'Plane'. or index 2 in this case
        # set scale and rotation
        bpy.data.objects['Plane'].scale = [6.275, 6.275, 6.275]
        bpy.data.objects['Plane'].rotation_euler = [105*math.pi/180, 0.0, 0.0]

        # subdivide, so that the vertices can get displaced (instead if just bump-mapping)
        # TODO: Think of adding a cmd line option for lower-end systems to go with bump-map mode only
        self.subdivide_object(bpy.data.objects['Plane'], cuts=400)

        self.DisplacedMesh = MeshDisplacement(bpy.data.objects['Plane'])
        # TODO: do something with displaced plane

    # Override(Scene)
    def _setup_shader(self):
        # TODO: FIND OUT IF DUPLICATE IS NECESSARY?!
        albedo_path = os.path.join(self.pathname[0] + '_Base_Color' + self.pathname[1])
        roughness_path = os.path.join(self.pathname[0] + '_Roughness' + self.pathname[1])
        normal_path = os.path.join(self.pathname[0] + '_Normal' + self.pathname[1])
        height_path = os.path.join(self.pathname[0] + '_Height' + self.pathname[1])
        ao_Path = os.path.join(self.pathname[0] + '_Ambient_Occlusion' + self.pathname[1])
        metallic_Path = os.path.join(self.pathname[0] + '_Metallic' + self.pathname[1])

        shadername = "concrete"
        if self.isCracked:
            # TODO: INCLUDE HEIGHT MAP
            shader = CrackShader(shadername, albedo_path, roughness_path, normal_path, height_path, self.resolution)
        else:
            shader = MasterShader(shadername, albedo_path, roughness_path, normal_path, height_path)

        self.shaderDict[shadername] = shader

        # Link shader to plane object
        bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete']
        # TODO: sample shader image sources!

        # Sample shader values
        shader.sample_texture()

        # Apply shader to obj mesh
        # TODO: UV unwrapping only happening once!
        shader.apply_to_blender_object("Plane")

    # Override(Scene)
    def update(self, heighttexpath):
        for key in self.shaderDict:
            try:
                self.shaderDict[key].sample_texture()
            except Exception:
                pass

        self.DisplacedMesh.displace(heighttexpath, disp_strength=1.0)