import bpy
import math
import os
import sys
import numpy as np
import colorsys

from lib.scene import Scene
from lib.crackshader import CrackShader

class ConcreteScene(Scene):
    def __init__(self, resolution):
        # attributes of the scene used in setup need to be called befor parent init!
        # otherwise they are not known to the overrinding function!
        self.resolution = resolution;
        
        super(ConcreteScene, self).__init__();


    #Override(Scene)
    def _setUpCamera(self):
        # add camera
        bpy.ops.object.camera_add()
        # location of camera
        bpy.data.objects['Camera'].location = (0.0, -15.0, 2.0)
        # rotation of camera. x axis rotation is 105.125 degrees in this example
        bpy.data.objects['Camera'].rotation_euler = [105.125*math.pi/180, 0.0, 0.0]
        # scale of camera usually unaltered.
        bpy.data.objects['Camera'].scale = [1.0, 1.0, 1.0]
        # by default camera type is perspective. uncomment below line for changing camera to orthographic.
        #bpy.data.cameras['Camera'].type='ORTHO'     #PERSP for perspective. default orthographic scale is 7.314
        # focal length of camera
        bpy.data.cameras['Camera'].lens = 35.00
        # focal length unit
        bpy.data.cameras['Camera'].lens_unit = 'MILLIMETERS' #FOV for field of view
        # note: you can add camera presets like samsung galaxy s4.
        # look at documentation and uncomment below line and modify accordinly. below line not tested
        #bpy.ops.script.execute_preset(filepath="yourpathlocation")

    #Override(Scene)
    def _setUpLighting(self):
        # add lamp
        bpy.ops.object.lamp_add(type='SUN')
        # change sun location.
        bpy.data.objects['Sun'].location = [0.0,-5.0,5.0]
        bpy.data.objects['Sun'].rotation_euler = [59*math.pi/180, 0.0, 0.0]

        # you can modify object names. example given below. uncomment if needed.
        # if uncommented upcoming commands should also be modified accordingly
        #bpy.data.lamps[0].name = 'Sun'
        #bpy.data.objects['Sun'].name = 'Sun'
        # you can add more light sources. uncomment below line for example light source
        #bpy.ops.object.lamp_add(type='POINT')

        # change rotation of sun's direction vector.
        bpy.data.objects['Sun'].rotation_euler = [59*math.pi/180, 0.0, 0.0]
        # in order to change color, strength of sun, we have to use nodes.
        # also node editing is quite useful for designing layers to your rendering
        bpy.data.lamps['Sun'].use_nodes = True
        # in the above statement we used 'Lamp' instead of index 0.
        # The default name of lamps is 'Lamp' as described in the above comments.

        # set color and strength value of sun using nodes.
        bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Color'].default_value = [1.0, 1.0, 1.0, 1.0]
        bpy.data.lamps['Sun'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 3.0


    #Override(Scene)
    def _setUpObjects(self):
        pass;

    #Override(Scene)
    def _setUpShader(self, albedoval=[0.5, 0.5, 0.5], locationval=[0, 0, 0], rotationval=[0, 0, 0], scaleval=[1, 1, 1], concrete=1, cracked=1):
        # add a base primitive mesh. in this case a plane mesh is added at origin
        print("Set primitive mesh")
        bpy.ops.mesh.primitive_plane_add(location=(0.0, -2.0, 5.5))
        # default object name is 'Plane'. or index 2 in this case
        # set scale and rotation
        print("Modify mesh")
        bpy.data.objects['Plane'].scale = [6.275, 6.275, 6.275]
        bpy.data.objects['Plane'].rotation_euler = [105*math.pi/180, 0.0, 0.0]

        shadername = "concrete";
        albedoPath = os.path.join('concretedictionary/concrete' + str(concrete) + '/albedo' + str(concrete) + '.png')
        roughnessPath = os.path.join('concretedictionary/concrete' + str(concrete) + '/roughness' + str(concrete) + '.png');
        normalPath = os.path.join('concretedictionary/concrete' + str(concrete) + '/normal' + str(concrete) + '.png')
        
        if(not cracked):
            print("Init mastershader");
            shader = MasterShader(shadername, albedoPath, roughnessPath, normalPath);
            print("Done...");

            print("Link shader to plane object");
            bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete'];
            print("Done...");

            # TODO: sample shader image sources!

            print("Sample shader values");
            shader.sampleTexture();
            print("Done...");
            
            print("Apply shader to obj mesh");
            shader.applyTo("Plane");
            print("Done...");
        elif(cracked):
            print("Init crackshader");
            shader = CrackShader(shadername, albedoPath, roughnessPath, normalPath, self.resolution);
            print("Done...");

            print("Link shader to plane object");
            bpy.data.objects['Plane'].active_material = bpy.data.materials['concrete'];
            print("Done...");

            # TODO: sample shader image sources!

            print("Sample shader values");
            shader.sampleTexture();
            print("Done...");
            
            print("Apply shader to obj mesh");
            shader.applyTo("Plane");
            print("Done...");