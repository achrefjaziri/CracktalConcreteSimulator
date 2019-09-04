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

        self.result_imgs_right = []
        self.result_normals_right = []
        self.result_gt_right = []


        self.scene = None

    def setScene(self, scene):
        self.scene = scene

    def render(self, cameraLeft, cameraRight):
        bpy.data.scenes['Scene'].frame_end = self.frames
        bpy.data.scenes['Scene'].render.filepath = self.path
        bpy.data.scenes['Scene'].cycles.samples = self.samples
        bpy.data.scenes['Scene'].render.resolution_x = self.resolution
        bpy.data.scenes['Scene'].render.resolution_y = self.resolution
        bpy.data.scenes['Scene'].render.resolution_percentage = 100
        
        # before rendering, set the sceen camera to the camera that you chose
        #bpy.data.scenes['Scene'].camera = cameraLeft

        # set render tile sizes
        bpy.data.scenes['Scene'].render.tile_x = self.tilesize
        bpy.data.scenes['Scene'].render.tile_y = self.tilesize

        # render color image left
        self.render_img(filepath=self.path, camera=cameraLeft, save_list=self.result_imgs)
        # render color image right
        self.render_img(filepath=self.path, camera=cameraRight, save_list=self.result_imgs_right)

        # render groundtruth
        self.render_gt(filepath=self.path, camera=cameraLeft, crackflag=self.cracked, save_list=self.result_gt)
        # render groundtrugh right
        #self.render_gt(filepath=self.path, camera=cameraRight, crackflag=self.cracked, save_list=self.result_gt_right)
        
        # render normalmap
        self.render_np(filepath=self.path, camera=cameraLeft, save_list=self.result_normals)

        # render normalmap right
        self.render_np(filepath=self.path, camera=cameraRight, save_list=self.result_normals_right)


    def render_img(self, filepath, camera, save_list):
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
        # Set the camera used in this rendering pass
        self.setCamera(camera)
        # Setup shader
        self.scene.shaderDict["concrete"].set_shader_mode_color();
        # Render call
        bpy.ops.render.render(write_still=True)
        # as it seems impossible to access rendered image directly due to some blender internal
        # buffer freeing issues, we save the result to a tmp image and load it again.
        # Read rendered image from temp file to np array
        res = imageio.imread(filepath)
        save_list.append(res)

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

    def render_gt(self, filepath, camera, crackflag, save_list):
        # Set the camera used in this rendering pass
        self.setCamera(camera)

        if crackflag:
            print ('crack map is generated.')
            self.scene.shaderDict["concrete"].set_shader_mode_gt();

            bpy.ops.render.render(write_still=True)
            gt = imageio.imread(filepath)
            # binarize the ground-truth map
            gt = gt > 0
            gt = gt.astype(int)
            imageio.imwrite(filepath, gt)

            save_list.append(gt)
        else:
            print ('crack map not generated.')
            gt = np.zeros((self.resolution, self.resolution, 3))
            self.save_list.append(gt)

    def render_np(self, filepath, camera, save_list):
        # Set the camera used in this rendering pass
        self.setCamera(camera)

        # Setup shader
        self.scene.shaderDict["concrete"].set_shader_mode_normal()

        # Render call
        bpy.ops.render.render(write_still=True)

        # Read rendered image from temp file to np array
        res = imageio.imread(filepath)
        save_list.append(res)

    def setPath(self, path):
        self.path = path

    def setSamples(self, samples):
        self.samples = samples

    def setCracked(self, cracked):
        self.cracked = cracked

    def setFrames(self, frames):
        self.frames = frames

    def setCamera(self, camera):
        bpy.data.scenes['Scene'].camera = camera

