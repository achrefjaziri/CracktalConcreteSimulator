import bpy
import numpy as np
import math
import os

from lib.scene import Scene
from lib.crackshader import CrackShader
from lib.mastershader import MasterShader
from lib.meshmodifiers import MeshDisplacement


class ConcreteSceneStereo(Scene):
    def __init__(self, resolution, is_cracked, path):
        # attributes of the scene used in setup need to be called before parent init!
        # otherwise they are not known to the overriding function!
        self.resolution = resolution

        self.isCracked = is_cracked

        self.DisplacedMesh = None

        self.DisplacedCrack = None

        self.pathname = path
        super(ConcreteScene, self).__init__()

    # Override(Scene)
    def _setup_camera(self):
        # Left Camera
        # add camera
        bpy.ops.object.camera_add()
        # rename camera
        bpy.data.cameras['Camera'].name = 'CameraLeft'
        bpy.data.objects['Camera'].name = 'CameraLeft'
        # location of camera
        bpy.data.objects['CameraLeft'].location = (-2.0, -14.0, 2.0)
        # rotation of camera. x axis rotation is 105.125 degrees in this example
        bpy.data.objects['CameraLeft'].rotation_euler = [105.125*math.pi/180, 0.0, -8*math.pi/180]
        # scale of camera usually unaltered
        bpy.data.objects['CameraLeft'].scale = [1.0, 1.0, 1.0]
        # focal length of camera
        bpy.data.cameras['CameraLeft'].lens = 35.00
        # focal length unit
        bpy.data.cameras['CameraLeft'].lens_unit = 'MILLIMETERS'

        # Right Camera
        # add camera
        bpy.ops.object.camera_add()
        # rename camera
        bpy.data.cameras['Camera'].name = 'CameraRight'
        bpy.data.objects['Camera'].name = 'CameraRight'
        # location of camera
        bpy.data.objects['CameraRight'].location = (2.0, -14, 2.0)
        # rotation of camera. x axis rotation is 105.125 degrees in this example
        bpy.data.objects['CameraRight'].rotation_euler = [105.125*math.pi/180, 0.0, 8*math.pi/180]
        # scale of camera usually unaltered
        bpy.data.objects['CameraRight'].scale = [1.0, 1.0, 1.0]
        # focal length of camera
        bpy.data.cameras['CameraRight'].lens = 35.00
        # focal length unit
        bpy.data.cameras['CameraRight'].lens_unit = 'MILLIMETERS'

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
        bpy.data.lamps['Sun'].node_tree.nodes['Blackbody'].inputs['Temperature'].default_value = 5800 #6500
        bpy.data.lamps['Sun'].node_tree.links.new(bpy.data.lamps['Sun'].node_tree.nodes['Blackbody'].outputs['Color'],
                                                  bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Color'])
        bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 3.3


    # Override(Scene)
    def _setup_objects(self):

        # add a base primitive mesh. in this case a grid mesh is added at the origin
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=int(self.resolution/2), y_subdivisions=int(self.resolution/2),
                                        location=(0.0, -2.0, 5.5))
                                        
        # default object name is 'Grid'
        # set scale and rotation
        bpy.data.objects['Grid'].scale = [6.275, 6.275, 6.275]
        bpy.data.objects['Grid'].rotation_euler = [105*math.pi/180, 0.0, 0.0]

        """
        # add a base primitive mesh. in this case a plane mesh is added at the origin
        bpy.ops.mesh.primitive_plane_add(location=(0.0, -2.0, 5.5))
        # default object name is 'Plane'. or index 2 in this case
        # set scale and rotation
        bpy.data.objects['Plane'].scale = [6.275, 6.275, 6.275]
        bpy.data.objects['Plane'].rotation_euler = [105 * math.pi / 180, 0.0, 0.0]

        # subdivide, so that the vertices can get displaced (instead if just bump-mapping)
        # TODO: Think of adding a cmd line option for lower-end systems to go with bump-map mode only
        self.subdivide_object(bpy.data.objects['Plane'], cuts=500)
        """

        # UV unwrap object
        bpy.data.objects['Grid'].select = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.unwrap()
        bpy.ops.object.editmode_toggle()

        self.DisplacedMesh = MeshDisplacement(bpy.data.objects['Grid'], 'concrete_displacement')
        if self.isCracked:
            self.DisplacedCrack = MeshDisplacement(bpy.data.objects['Grid'], 'crack_displacement')

    # Override(Scene)
    def _setup_shader(self):
        albedo_path = os.path.join(self.pathname[0] + '_Base_Color' + self.pathname[1])
        roughness_path = os.path.join(self.pathname[0] + '_Roughness' + self.pathname[1])
        normal_path = os.path.join(self.pathname[0] + '_Normal' + self.pathname[1])
        height_path = os.path.join(self.pathname[0] + '_Height' + self.pathname[1])
        ao_Path = os.path.join(self.pathname[0] + '_Ambient_Occlusion' + self.pathname[1])
        metallic_Path = os.path.join(self.pathname[0] + '_Metallic' + self.pathname[1])

        shadername = "concrete"

        if self.isCracked:
            shader = CrackShader(shadername, albedo_path, roughness_path, normal_path, height_path, self.resolution)
        else:
            shader = MasterShader(shadername, albedo_path, roughness_path, normal_path, height_path)

        self.shaderDict[shadername] = shader

        # Link shader to grid object
        bpy.data.objects['Grid'].active_material = bpy.data.materials['concrete']

        # Sample shader values
        shader.sample_texture()

        # Apply shader to obj mesh
        # TODO: UV unwrapping only happening once!
        shader.apply_to_blender_object(bpy.data.objects['Grid'])

    # Override(Scene)
    def update(self):

        # Update Sun rotation
        rand_sun_rotation_y = np.random.uniform(-30, 30)
        bpy.data.objects['Sun'].rotation_euler = [59 * math.pi / 180, rand_sun_rotation_y, 0.0]

        for key in self.shaderDict:
            try:
                # TODO: returning height texture path so that it can be used for displacement of mesh. This is an imroper fix.
                if self.isCracked:
                    heightTexPath, img_tex_heights = self.shaderDict[key].sample_texture()
                    self.DisplacedMesh.displace(heightTexPath, disp_strength=0.05)
                    # Negative value is given for displacement strength of crack because displacement has to be in
                    # the opposite direction of the normals in object coordinates.
                    rand_disp_strenght = np.random.uniform(0.03, 0.05)
                    self.DisplacedCrack.displace(img_tex_heights, disp_strength=-rand_disp_strenght)
                else:
                    heightTexPath = self.shaderDict[key].sample_texture()
                    self.DisplacedMesh.displace(heightTexPath, disp_strength=0.05)
            except Exception:
                pass

