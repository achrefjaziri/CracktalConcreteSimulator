import bpy


class Scene:
    def __init__(self):
        self.shaderDict = {}

        self._reset_scene()
        self._setup_scene()

    def _setup_scene(self):
        self._setup_camera()
        self._setup_lighting()
        self._setup_objects()
        self._setup_shader()

    def _setup_camera(self):
        raise NotImplementedError

    def _setup_lighting(self):
        raise NotImplementedError

    def _setup_objects(self):
        raise NotImplementedError

    def _setup_shader(self):
        pass

    def _reset_scene(self):
        check = bpy.data.objects is not None
        # remove pre-existing objects from blender
        if check:
            for obj in bpy.data.objects:
                obj.select = True
                bpy.ops.object.delete()
                # clear mesh and material data. removing objects alone is not necessary
                for mesh in bpy.data.meshes:
                    bpy.data.meshes.remove(mesh, do_unlink=True)
                for material in bpy.data.materials:
                    bpy.data.materials.remove(material, do_unlink=True)
                for camera in bpy.data.cameras:
                    bpy.data.cameras.remove(camera, do_unlink=True)
                for lamp in bpy.data.lamps:
                    bpy.data.lamps.remove(lamp, do_unlink=True)

    def update(self):
        pass
