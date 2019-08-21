import bpy
import numpy as np
import imageio


class RenderManager():
    def __init__(self, path, frames, samples, resolution, tilesize, cracked):
        self.path = path
        self.frames = frames
        self.samples = samples
        self.resolution = resolution
        self.tilesize = tilesize
        self.cracked = cracked
        # Place-holder lists for rendered image, normal map and ground-truth
        self.result_imgs = []
        self.result_normals = []
        self.result_gt = []

        self.scene = None

    def setScene(self, scene):
        self.scene = scene

    def render(self, camera):
        bpy.data.scenes['Scene'].frame_end = self.frames
        bpy.data.scenes['Scene'].render.filepath = self.path
        bpy.data.scenes['Scene'].cycles.samples = self.samples
        bpy.data.scenes['Scene'].render.resolution_x = self.resolution
        bpy.data.scenes['Scene'].render.resolution_y = self.resolution
        bpy.data.scenes['Scene'].render.resolution_percentage = 100
        # before rendering, set the sceen camera to the camera that you chose
        bpy.data.scenes['Scene'].camera = camera

        # set render tile sizes
        bpy.data.scenes['Scene'].render.tile_x = self.tilesize
        bpy.data.scenes['Scene'].render.tile_y = self.tilesize

        self.render_img(filepath=self.path, frames=self.frames, samples=self.samples)
        # render groundtruth
        self.rendergt(filepath=self.path, frames=self.frames, samples=self.samples, crackflag=self.cracked)
        # render normalmap
        self.rendernp(filepath=self.path, frames=self.frames, samples=self.samples, crackflag=self.cracked)

    def render_img(self, filepath, frames, samples):
        # Commented code can later potentially be used to get the result directly from the CompositorLayer 
        # in principle this works fine, however it needs a GUI to work....
        # and pipe convert and reshape it into a numpy array
        # switch on nodes
        """
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links
        
        # create input render layer node
        rl = tree.nodes.new('CompositorNodeRLayers')
        rl.location = 185, 285
        
        # create output node
        v = tree.nodes.new('CompositorNodeViewer')
        v.name = 'ImageViewerNode'
        v.location = 750, 210
        v.use_alpha = False

        # create another output node for surface normals
        n = tree.nodes.new('CompositorNodeViewer')
        n.location = 750, 390
        n.use_alpha = False
        
        # for the normals
        bpy.data.scenes['Scene'].render.layers["RenderLayer"].use_pass_normal = True

        # Links
        links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input
        links.new(rl.outputs['Normal'], n.inputs[0])  # link Normal output to Viewer input
        """

        self.scene.shaderDict["concrete"].set_shader_mode_color();

        bpy.ops.render.render(write_still=True)
        # as it seems impossible to access rendered image directly due to some blender internal
        # buffer freeing issues, we save the result to a tmp image and load it again.
        res = imageio.imread(filepath)
        self.result_imgs.append(res)

        """
        # get viewer pixels
        img_pixels = bpy.data.images['Viewer Node'].pixels
        normal_pixels = bpy.data.images['Viewer Node'].pixels

        # copy buffer to numpy array for faster manipulation
        # size is always width * height * 4 (rgba)
        arr = np.array(img_pixels)
        arr = arr.reshape((resolution, resolution, 4))
        misc.imsave('outputfile.png', arr)

        arr = np.array(normal_pixels)
        arr = arr.reshape((resolution, resolution, 4))
        misc.imsave('normaloutputfile.png', arr)
        """

    def rendergt(self, filepath, frames, samples, crackflag):
        if crackflag:
            print ('crack map is generated.')
            self.scene.shaderDict["concrete"].set_shader_mode_gt();

            bpy.ops.render.render(write_still=True)
            gt = imageio.imread(filepath)
            # binarize the ground-truth map
            gt = gt > 0
            gt = gt.astype(int)
            imageio.imwrite(filepath, gt)

            self.result_gt.append(gt)
        else:
            print ('crack map not generated.')
            gt = np.zeros((self.resolution, self.resolution, 3))
            self.result_gt.append(gt)

    def rendernp(self, filepath, frames, samples, crackflag):
        self.scene.shaderDict["concrete"].set_shader_mode_normal()

        # render call
        bpy.ops.render.render(write_still=True)

        self.result_normals.append(imageio.imread(filepath))

        res = imageio.imread(filepath)
        self.result_normals.append(res)

    def setPath(self, path):
        self.path = path

    def setSamples(self, samples):
        self.samples = samples

    def setCracked(self, cracked):
        self.cracked = cracked

    def setFrames(self, frames):
        self.frames = frames
