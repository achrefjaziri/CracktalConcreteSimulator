import bpy

class MeshDisplacement:

    def __init__(self, blender_object):
        self.mesh = blender_object

        self.mesh.select = True
        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.data.textures.new('displacement', type='IMAGE')

    def displace(self, height_tex_path, disp_strength=0.05):
        # load the height map and assign it to the displacement modifier's texture
        bpy.data.textures['displacement'].image = bpy.data.images[height_tex_path.split("/")[-1]]
        self.mesh.modifiers['Displace'].texture = bpy.data.textures['displacement']

        # Blender's default value is strange and displaces way too much.
        # Advise is to keep the value below 0.1
        self.mesh.modifiers['Displace'].strength = disp_strength