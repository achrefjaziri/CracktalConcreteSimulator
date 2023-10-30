import bpy

class Scene:
    def __init__(self):
        self.shaderDict = {}

        self.compositionNodeTree = None
        self.compositionNodeTreeLinks = None

        self._reset_scene()
        self._setup_scene()

    def _setup_scene(self):
        # Activate scene compositing nodes
        bpy.context.scene.use_nodes = True
        # Set scene units to metric
        bpy.context.scene.unit_settings.system = "METRIC"
        
        self._setup_camera()
        self._setup_lighting()
        self._setup_objects()
        self._setup_shader()
        self._setup_scene_composition()

    def _setup_camera(self):
        raise NotImplementedError

    def _setup_lighting(self):
        raise NotImplementedError

    def _setup_objects(self):
        raise NotImplementedError

    def _setup_shader(self):
        pass

    def _setup_scene_composition(self):
        self.compositionNodeTree = bpy.context.scene.node_tree
        self.compositionNodeTreeLinks = self.compositionNodeTree.links
        return

    def subdivide_object(self, blender_obj, cuts=100):
        # TODO: potentially move this to concretescene
        # select given object
        blender_obj.select = True

        # go into edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
		
        # subdivision of mesh
        if cuts > 100:
            bpy.ops.mesh.subdivide(number_cuts=100, quadtri=False)
            bpy.ops.mesh.subdivide(number_cuts=int(cuts/100), quadtri=False)
        else:
            bpy.ops.mesh.subdivide(number_cuts=cuts, quadtri=False)

        # go back into object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        blender_obj.select = False

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

    def update(self, heighttexpath):
        pass
