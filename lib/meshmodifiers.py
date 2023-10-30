import bpy


class MeshDisplacement:
    def __init__(self, blender_object, texture_name):
        self.mesh = blender_object

        self.mesh.select = True
        self.texture_name = texture_name
        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.data.textures.new(self.texture_name, type='IMAGE')

        bpy.data.objects[blender_object.name].modifiers['Displace'].name = self.texture_name
        bpy.data.objects[blender_object.name].modifiers[self.texture_name].texture_coords = 'UV'
        bpy.data.objects[blender_object.name].modifiers[self.texture_name].mid_level = 0.00

    def displace(self, height_texture, disp_strength=0.05):
        # load the height map and assign it to the displacement modifier's texture
        if type(height_texture) is str:
            bpy.data.textures[self.texture_name].image = bpy.data.images[height_texture.split("/")[-1]]
        else:
            bpy.data.textures[self.texture_name].image = height_texture
        self.mesh.modifiers[self.texture_name].texture = bpy.data.textures[self.texture_name]

        # Blender's default value is strange and displaces way too much.
        # Advise is to keep the value below 0.1
        self.mesh.modifiers[self.texture_name].strength = disp_strength
