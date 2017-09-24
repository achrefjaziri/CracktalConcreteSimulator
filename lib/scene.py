import bpy
import math
import os
import sys
import numpy as np
import colorsys


class Scene():
    def __init__(self):
        self.resetSceneToEmpty();
        self.setUp();

    def setUp(self):
        self._setUpCamera();
        self._setUpLighting();
        self._setUpObjects();
        self._setUpShader();

    def _setUpCamera(self):
        raise NotImplementedError

    def _setUpLighting(self):
        raise NotImplementedError

    def _setUpObjects(self):
        raise NotImplementedError

    def _setUpShader(self):
        pass;

    def resetSceneToEmpty(self):
        check = bpy.data.objects is not None
        # remove pre-existing objects from blender
        if check == True:
            for object in bpy.data.objects:
                object.select = True
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
