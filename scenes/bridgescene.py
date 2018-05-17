import bpy
import math
import os
import sys

import pandas as pd
import copy

from lib.scene import Scene
from lib.crackshader import CrackShader
from lib.mastershader import MasterShader
from lib.meshmodifiers import MeshDisplacement

class BridgeScene(Scene):
	def __init__(self, resolution, is_cracked, texturepath, bridgepath, cam_traj_path, cam_traj_column_names):
		# attributes of the scene used in setup need to be called before parent init!
		# otherwise they are not known to the overriding function!
		self.resolution = resolution

		self.isCracked = is_cracked

		self.DisplacedMesh = []

		self.DisplacedCrack = []

		self.texturepath = texturepath
		self.bridgepath = bridgepath
		
		self.cam_traj_path = cam_traj_path
		self.cam_traj_column_names = cam_traj_column_names
		self._load_cam_trajectory()
		
		super(BridgeScene, self).__init__()

	def _load_cam_trajectory(self):

		self.camera_positions = pd.read_csv(self.cam_traj_path, header=None)
		self.camera_positions.columns = self.cam_traj_column_names

		# "correct coordinate system"
		self.camera_positions.camera_z *= -1

		tmp = copy.deepcopy(self.camera_positions.camera_x)
		self.camera_positions.camera_x = self.camera_positions.camera_y
		self.camera_positions.camera_y = tmp
		
		#position change for camera to focus on beam
		#self.camera_positions.camera_z = -0.2
		#self.camera_positions.camera_y -=10.
		#self.camera_positions.camera_x +=10.
		#self.camera_positions.gimbal_yaw +=math.pi/2
		
		#orient camera to point up
		self.camera_positions.gimbal_pitch +=math.pi/2
		
		self.camera_positions.camera_roll = self.camera_positions.gimbal_roll
		self.camera_positions.camera_pitch = self.camera_positions.gimbal_pitch
		self.camera_positions.camera_yaw = self.camera_positions.gimbal_yaw

		#print "Got %d camera positions" % (len(camera_positions))
		self.cam_traj_key = self.camera_positions.image_file_name[1:4]
		self.camera_positions.set_index("image_file_name", inplace=True)

	# Override(Scene)
	def _setup_camera(self):
		for idx, img_fname in enumerate(self.cam_traj_key):
			# get meta-data
			current_meta = self.camera_positions.loc[img_fname.split("/")[-1]]
			
			#add flash to each camera
			bpy.ops.object.lamp_add(type='POINT', radius=5, view_align=False, location=(current_meta.camera_x, current_meta.camera_y, current_meta.camera_z), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
			
			# add camera
			bpy.ops.object.camera_add()
		
			#rename it
			camera = bpy.context.object
			camera.name = 'Camera'+str(idx)
		
			# location of camera
			bpy.data.objects[camera.name].location = (current_meta.camera_x, current_meta.camera_y, current_meta.camera_z)
			# rotation of camera. x axis rotation is 105.125 degrees in this example
			bpy.data.objects[camera.name].rotation_euler = [current_meta.camera_roll, current_meta.camera_pitch, current_meta.camera_yaw]
			# scale of camera usually unaltered
			bpy.data.objects[camera.name].scale = [1.0, 1.0, 1.0]
			if(len(bpy.data.cameras) == 1):
				# focal length of camera
				bpy.data.cameras['Camera'].lens = 35.00
				# focal length unit
				bpy.data.cameras['Camera'].lens_unit = 'MILLIMETERS'
        
	def _get_cam_calibration_matrix(self, camd):
		f_in_mm = camd.data.lens
		scene = bpy.context.scene
		resolution_x_in_px = scene.render.resolution_x
		resolution_y_in_px = scene.render.resolution_y
		scale = scene.render.resolution_percentage / 100
		sensor_width_in_mm = camd.data.sensor_width
		sensor_height_in_mm = camd.data.sensor_height
		pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
		if (camd.data.sensor_fit == 'VERTICAL'):
			# the sensor height is fixed (sensor fit is horizontal), 
			# the sensor width is effectively changed with the pixel aspect ratio
			s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio 
			s_v = resolution_y_in_px * scale / sensor_height_in_mm
		else: # 'HORIZONTAL' and 'AUTO'
			# the sensor width is fixed (sensor fit is horizontal), 
			# the sensor height is effectively changed with the pixel aspect ratio
			s_u = resolution_x_in_px * scale / sensor_width_in_mm
			s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

		# Parameters of intrinsic calibration matrix K
		fx_px = f_in_mm * s_u
		fy_px = f_in_mm * s_v
		cx_px = resolution_x_in_px * scale / 2
		cy_px = resolution_y_in_px * scale / 2
		skew = 0 # only use rectangular pixels

		return np.array([[fx_px, skew, cx_px],[0,fy_px,cy_px],[0,0,1]])


	# Override(Scene)
	def _setup_lighting(self):
		# add light source
		bpy.ops.object.lamp_add(type='SUN')
		# change sun location
		bpy.data.objects['Sun'].location = [0.0, -5.0, 16.0]
		# change rotation of sun's direction vector.
		bpy.data.objects['Sun'].rotation_euler = [59*math.pi/180, 0, -math.pi/4.]

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
	
	def _split_obj_into_faces(obj):
	
		bpy.ops.object.mode_set(mode = 'EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.edge_split()
		bpy.ops.mesh.separate(type='LOOSE')
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		
		#deselect everything
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.scene.objects.active = None
	
	# Override(Scene)
	def _setup_objects(self):
		bpy.ops.import_mesh.ply(filepath = self.bridgepath)
		bridge_name = self.bridgepath.split("/")[-1].split(".")[0]
		
		self._split_obj_into_faces()
		self.bridgeObjs = [ob for ob in bpy.context.scene.objects if ob.name.startswith(bridge_name)]
		
		for obj in self.bridgeObjs:

			# subdivide, so that the vertices can get displaced (instead if just bump-mapping)
			# TODO: Think of adding a cmd line option for lower-end systems to go with bump-map mode only
			bpy.context.scene.objects.active = obj
			self.subdivide_object(obj, cuts=100)
			#
			objNameSplit = obj.name.split('.')
			#after split into faces, all objects are numbered (001, 002 etc.), apart from the first one
			if len(objNameSplit) < 2:
				objNum = '0'
			else:
				objNum = obj.name.split('.')[1]

			self.DisplacedMesh.append( MeshDisplacement(obj, 'concrete_displacement'+objNum) )
			if self.isCracked:
				self.DisplacedCrack.append( MeshDisplacement(obj, 'crack_displacement'+objNum) )

	# Override(Scene)
	def _setup_shader(self):
		albedo_path = os.path.join(self.texturepath[0] + '_Base_Color' + self.texturepath[1])
		roughness_path = os.path.join(self.texturepath[0] + '_Roughness' + self.texturepath[1])
		normal_path = os.path.join(self.texturepath[0] + '_Normal' + self.texturepath[1])
		height_path = os.path.join(self.texturepath[0] + '_Height' + self.texturepath[1])
		ao_Path = os.path.join(self.texturepath[0] + '_Ambient_Occlusion' + self.texturepath[1])
		metallic_Path = os.path.join(self.texturepath[0] + '_Metallic' + self.texturepath[1])
		
		shadername = "concrete"

		if self.isCracked:
			shader = CrackShader(shadername, albedo_path, roughness_path, normal_path, height_path, self.resolution)
		else:
			shader = MasterShader(shadername, albedo_path, roughness_path, normal_path, height_path)

		self.shaderDict[shadername] = shader

		print('Assign texture to all bridge faces')
		for obj in self.bridgeObjs:
			bpy.context.scene.objects.active = obj
			# Link shader to grid object
			obj.active_material = bpy.data.materials[shadername]
			#("sample_texture")
			# TODO: sample shader image sources!
			# Sample shader values
			shader.sample_texture()
			#print("apply_blender_obj")
			# Apply shader to obj mesh
			# TODO: UV unwrapping only happening once!
			shader.apply_to_blender_object( obj )
			sys.stdout.write('.')
			sys.stdout.flush()
		print('END Assign texture to all bridge faces')

	# Override(Scene)
	def update(self):
		for dmesh, dcrack in zip(self.DisplacedMesh, self.DisplacedCrack ):
			for key in self.shaderDict:
				try:
				    # TODO: returning height texture path so that it can be used for displacement of mesh. This is an imroper fix.
				    if self.isCracked:
				        heightTexPath, img_tex_heights = self.shaderDict[key].sample_texture()
				        dmesh.displace(heightTexPath, disp_strength=0.05)
				        # Negative value is given for displacement strength of crack because displacement has to be in
				        # the opposite direction of the normals in object coordinates.
				        dcrack.displace(img_tex_heights, disp_strength=-0.01)
				    else:
				        heightTexPath = self.shaderDict[key].sample_texture()
				        dmesh.displace(heightTexPath, disp_strength=0.05)
				except Exception:
				    pass

