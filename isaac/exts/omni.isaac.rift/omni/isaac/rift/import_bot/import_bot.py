from omni.isaac.core.utils.stage import add_reference_to_stage
import omni.graph.core as og
import omni.usd
from omni.isaac.rift.base_sample import BaseSample
from omni.isaac.urdf import _urdf
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils import prims
from omni.isaac.core.prims import GeometryPrim, RigidPrim

from omni.isaac.core_nodes.scripts.utils import set_target_prims
# from omni.kit.viewport_legacy import get_default_viewport_window
# from omni.isaac.sensor import IMUSensor
from pxr import UsdPhysics, UsdShade, Sdf, Gf
import omni.kit.commands
import os
import numpy as np
import math
import carb
from omni.isaac.core.materials import PhysicsMaterial
from random import randint, choice


NAMESPACE = f"{os.environ.get('ROS_NAMESPACE')}" if 'ROS_NAMESPACE' in os.environ else 'default'

def set_drive_params(drive, stiffness, damping, max_force):
    drive.GetStiffnessAttr().Set(stiffness)
    drive.GetDampingAttr().Set(damping)
    if(max_force != 0.0):
        drive.GetMaxForceAttr().Set(max_force)
    return

def add_physics_material_to_prim(prim, materialPath):
    bindingAPI = UsdShade.MaterialBindingAPI.Apply(prim)
    materialPrim = UsdShade.Material(materialPath)
    bindingAPI.Bind(materialPrim, UsdShade.Tokens.weakerThanDescendants, "physics")

class ImportBot(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self.cone_list = []
        self.cube_list = []
        return


    def set_friction(self, robot_prim_path):
        stage = omni.usd.get_context().get_stage()
        omni.kit.commands.execute('AddRigidBodyMaterialCommand',stage=stage, path='/World/Physics_Materials/Rubber',staticFriction=1.1,dynamicFriction=1.5,restitution=None)
        omni.kit.commands.execute('AddRigidBodyMaterialCommand',stage=stage, path='/World/Physics_Materials/RubberProMax',staticFriction=1.5,dynamicFriction=2.0,restitution=None)

        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/Rubber',prim_path=[f"{robot_prim_path}/front_left_wheel_link"],strength=['weakerThanDescendants'])
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/Rubber',prim_path=[f"{robot_prim_path}/front_right_wheel_link"],strength=['weakerThanDescendants'])
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/Rubber',prim_path=[f"{robot_prim_path}/rear_left_wheel_link"],strength=['weakerThanDescendants'])
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/Rubber',prim_path=[f"{robot_prim_path}/rear_right_wheel_link"],strength=['weakerThanDescendants'])
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/Rubber',prim_path=[f"/World/defaultGroundPlane"],strength=['weakerThanDescendants'])
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_2/Charge_Station/station_pivot_base"],strength=['weakerThanDescendants'],material_purpose='physics')
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_2/Charge_Station/station_incline_panel_01"],strength=['weakerThanDescendants'],material_purpose='physics')
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_2/Charge_Station/station_incline_panel"],strength=['weakerThanDescendants'],material_purpose='physics')
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_2/Charge_Station/station_pivot_connector/station_top_panel"],strength=['weakerThanDescendants'],material_purpose='physics')
        
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_1/Charge_Station/station_pivot_base"],strength=['weakerThanDescendants'],material_purpose='physics')
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_1/Charge_Station/station_incline_panel_01"],strength=['weakerThanDescendants'],material_purpose='physics')
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_1/Charge_Station/station_incline_panel"],strength=['weakerThanDescendants'],material_purpose='physics')
        omni.kit.commands.execute('BindMaterialExt',material_path='/World/Physics_Materials/RubberProMax',prim_path=[f"/World/ChargeStation_1/Charge_Station/station_pivot_connector/station_top_panel"],strength=['weakerThanDescendants'],material_purpose='physics')


        # omni.kit.commands.execute('BindMaterial',material_path='/World/Physics_Materials/Rubber',prim_path=[f"/World/FE_2023/FE_2023/FE_2023_01"],strength=['weakerThanDescendants'])
        # omni.kit.commands.execute('BindMaterial',material_path='/World/Physics_Materials/Rubber',prim_path=[f"/World/FE_2023/FE_2023/FE_2023_01_01"],strength=['weakerThanDescendants'])

    def setup_scene(self):
        world = self.get_world()
        
        # world.get_physics_context().enable_gpu_dynamics(True)
        
        world.set_simulation_dt(1/300.0,1/60.0)
        world.scene.add_default_ground_plane()
        self.setup_field()
        # self.setup_perspective_cam()
        self.setup_world_action_graph()
        return
    def add_game_piece(self):
        print("asdklj;f;asdjdfdl;asdjfkl;asdjfkl;asdjfkl;asfjkla;sdjkflka;k")
        self.extension_path = os.path.abspath(__file__)
        self.project_root_path = os.path.abspath(os.path.join(self.extension_path, "../../../../../../.."))
        cone = os.path.join(self.project_root_path, "assets/2023_field_cpu/parts/GE-23700_JFH.usd")
        cube = os.path.join(self.project_root_path, "assets/2023_field_cpu/parts/GE-23701_JFL.usd")
        add_reference_to_stage(cone, "/World/Cone_1")
        substation_empty = [True, True, True, True]
        game_piece_list = self.cone_list+self.cube_list
        for game_piece in game_piece_list:
            pose, orienation = game_piece.get_world_pose()
            print(pose)
            if(pose[0]<8.17+0.25 and pose[0]>8.17-0.25):
                if(pose[1]<-2.65+0.25 and pose[1]>-2.65-0.25):
                    substation_empty[0]=False
                    print("substation_empty[0]=False")
                elif pose[1]<-3.65+0.25 and pose[1]>-3.65-0.25:
                    substation_empty[1]=False
                    print("substation_empty[1]=False")

            elif (pose[0]<-8.17+0.25 and pose[0]>-8.17-0.25):
                if(pose[1]<-2.65+0.25 and pose[1]>-2.65-0.25):
                    substation_empty[2]=False
                    print("substation_empty[2]=False")

                elif pose[1]<-3.65+0.25 and pose[1]>-3.65-0.25:
                    substation_empty[3]=False
                    print("substation_empty[3]=False")
        for i in range(4):
            if substation_empty[i]:
                next_cube = (len(self.cube_list)+1)
                next_cone = (len(self.cone_list)+1)
                if(i==0):
                    position = [8.17, -2.65, 1.15]
                elif(i==1):
                    position = [-8.17, -2.65, 1.15]
                elif(i==2):
                    position = [8.17, -3.65, 1.15]
                else:
                    position = [-8.17, -3.65, 1.15]
                if choice([True, False]):
                    print("yes")
                    name = "/World/Cube_"+str(next_cube)
                    view = "cube_"+str(next_cube)+"_view"
                    add_reference_to_stage(cube, "/World/Cube_"+str(next_cube))
                    self.cube_list.append(GeometryPrim(name, view, position=position))
                else:
                    print("yesss")
                    name = "/World/Cone_"+str(next_cone)
                    view = "cone_"+str(next_cone)+"_view" 
                    add_reference_to_stage(cone, name)
                    self.cone_list.append(GeometryPrim(name, view, position=position))





        return
   
    def setup_field(self):
        world = self.get_world()
        self.extension_path = os.path.abspath(__file__)
        self.project_root_path = os.path.abspath(os.path.join(self.extension_path, "../../../../../../.."))
        field = os.path.join(self.project_root_path, "assets/flattened_field/field2.usd")
        cone = os.path.join(self.project_root_path, "assets/game_pieces/GE-23700_JFH.usd")
        cube = os.path.join(self.project_root_path, "assets/game_pieces/GE-23701_JFL.usd")
        chargestation = os.path.join(self.project_root_path, "assets/chargestation/chargestation.usd")
        add_reference_to_stage(chargestation, "/World/ChargeStation_1")
        add_reference_to_stage(chargestation, "/World/ChargeStation_2")
        add_reference_to_stage(field, "/World/FE_2023")
        add_reference_to_stage(cone, "/World/Cone_1")
        add_reference_to_stage(cone, "/World/Cone_2")
        add_reference_to_stage(cone, "/World/Cone_3")
        add_reference_to_stage(cone, "/World/Cone_4")
        add_reference_to_stage(cone, "/World/Cone_5")
        add_reference_to_stage(cone, "/World/Cone_6")
        # add_reference_to_stage(cone, "/World/Cone_7")
        # add_reference_to_stage(cone,  "/World/Cone_8")
        field_1 = RigidPrim("/World/FE_2023","field_1_view",position=np.array([0.0,0.0,0.0]),scale=np.array([1, 1, 1]))
        # cone_1 = RigidPrim("/World/Cone_1","cone_1_view",position=np.array([1.20298,-0.56861,-0.4]))
        # cone_2 = GeometryPrim("/World/Cone_2","cone_2_view",position=np.array([1.20298,3.08899,0.0]))
        # cone_3 = GeometryPrim("/World/Cone_3","cone_3_view",position=np.array([-1.20298,-0.56861,0.0]))
        # cone_4 = GeometryPrim("/World/Cone_4","cone_4_view",position=np.array([-1.20298,3.08899,0.0]))
        chargestation_1 = GeometryPrim("/World/ChargeStation_1","cone_3_view",position=np.array([-4.53419,1.26454,0.025]),scale=np.array([0.0486220472,0.0486220472,0.0486220472]), orientation=np.array([ 1,1,0,0 ]))
        chargestation_2 = GeometryPrim("/World/ChargeStation_2","cone_4_view",position=np.array([4.53419,1.26454,0.025]),scale=np.array([0.0486220472,0.0486220472,0.0486220472]), orientation=np.array([ 1,1,0,0 ]))
        self.cone_list.append( RigidPrim("/World/Cone_1","cone_1_view",position=np.array([1.20298,-0.56861,0.0])))
        self.cone_list.append( RigidPrim("/World/Cone_2","cone_2_view",position=np.array([1.20298,3.08899,0.0])))
        self.cone_list.append( RigidPrim("/World/Cone_3","cone_3_view",position=np.array([-1.20298,-0.56861,0.0])))
        self.cone_list.append( RigidPrim("/World/Cone_4","cone_4_view",position=np.array([-1.20298,3.08899,0.0])))
        self.cone_list.append( RigidPrim("/World/Cone_5","cone_5_view",position=np.array([-7.23149,-1.97376,0.86292])))
        self.cone_list.append( RigidPrim("/World/Cone_6","cone_6_view",position=np.array([7.23149,-1.97376,0.86292])))
        

        add_reference_to_stage(cube, "/World/Cube_1")
        add_reference_to_stage(cube, "/World/Cube_2")
        add_reference_to_stage(cube, "/World/Cube_3")
        add_reference_to_stage(cube, "/World/Cube_4")
        add_reference_to_stage(cube, "/World/Cube_5")
        add_reference_to_stage(cube, "/World/Cube_6")
        # add_reference_to_stage(cube, "/World/Cube_7")
        # # add_reference_to_stage(cube, "/World/Cube_8")
        # cube_1 = GeometryPrim("/World/Cube_1","cube_1_view",position=np.array([1.20298,0.65059,0.121]))
        # cube_2 = GeometryPrim("/World/Cube_2","cube_2_view",position=np.array([1.20298,1.86979,0.121]))
        # cube_3 = GeometryPrim("/World/Cube_3","cube_3_view",position=np.array([-1.20298,0.65059,0.121]))
        # cube_4 = GeometryPrim("/World/Cube_4","cube_4_view",position=np.array([-1.20298,1.86979,0.121]))
        self.cube_list.append( RigidPrim("/World/Cube_1","cube_1_view",position=np.array([1.20298,0.65059,0.121])))
        self.cube_list.append( RigidPrim("/World/Cube_2","cube_2_view",position=np.array([1.20298,1.86979,0.121])))
        self.cube_list.append( RigidPrim("/World/Cube_3","cube_3_view",position=np.array([-1.20298,0.65059,0.121])))
        self.cube_list.append( RigidPrim("/World/Cube_4","cube_4_view",position=np.array([-1.20298,1.86979,0.121])))
        self.cube_list.append( RigidPrim("/World/Cube_5","cube_5_view",position=np.array([-7.25682,-2.99115,1.00109])))
        self.cube_list.append( RigidPrim("/World/Cube_6","cube_6_view",position=np.array([7.25682,-2.99115,1.00109])))

    async def setup_post_load(self):
        self._world = self.get_world()
        # self._world.get_physics_context().enable_gpu_dynamics(True)
        self.robot_name = "rift"
        self.extension_path = os.path.abspath(__file__)
        self.project_root_path = os.path.abspath(os.path.join(self.extension_path, "../../../../../../.."))
        self.path_to_urdf = os.path.join(self.extension_path, "../../../../../../../..", "src/rift_description/urdf/rift.urdf")
        carb.log_info(self.path_to_urdf)

        self._robot_prim_path = self.import_robot(self.path_to_urdf)


        if self._robot_prim_path is None:
            print("Error: failed to import robot")
            return
        
        self._robot_prim = self._world.scene.add(
            Robot(prim_path=self._robot_prim_path, name=self.robot_name, position=np.array([0.0, 0.0, 0.5]))
        )
        
        self.configure_robot(self._robot_prim_path)
        return
    
    def import_robot(self, urdf_path):
        import_config = _urdf.ImportConfig()
        import_config.merge_fixed_joints = False
        import_config.fix_base = False
        import_config.make_default_prim = True
        import_config.self_collision = False
        import_config.create_physics_scene = False
        import_config.import_inertia_tensor = True
        import_config.default_drive_strength = 1047.19751
        import_config.default_position_drive_damping = 52.35988
        import_config.default_drive_type = _urdf.UrdfJointTargetType.JOINT_DRIVE_VELOCITY
        import_config.distance_scale = 1.0
        import_config.density = 0.0
        result, prim_path = omni.kit.commands.execute( "URDFParseAndImportFile", 
            urdf_path=urdf_path,
            import_config=import_config)

        if result:
            return prim_path
        return None

    
    def configure_robot(self, robot_prim_path):
        w_sides = ['left', 'right']
        l_sides = ['front', 'back']
        stage = self._world.stage
        chassis_name = f"swerve_chassis_link"

       
        front_left_axle = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/{chassis_name}/front_left_axle_joint"), "angular")
        front_right_axle = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/{chassis_name}/front_right_axle_joint"), "angular")
        rear_left_axle = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/{chassis_name}/rear_left_axle_joint"), "angular")
        rear_right_axle = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/{chassis_name}/rear_right_axle_joint"), "angular")
        front_left_wheel = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/front_left_axle_link/front_left_wheel_joint"), "angular")
        front_right_wheel = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/front_right_axle_link/front_right_wheel_joint"), "angular")
        rear_left_wheel = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/rear_left_axle_link/rear_left_wheel_joint"), "angular")
        rear_right_wheel = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/rear_right_axle_link/rear_right_wheel_joint"), "angular")
        arm_roller_bar_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/arm_elevator_leg_link/arm_roller_bar_joint"), "linear")
        elevator_center_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/elevator_outer_1_link/elevator_center_joint"), "linear")
        elevator_outer_2_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/elevator_center_link/elevator_outer_2_joint"), "linear")
        elevator_outer_1_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/arm_back_leg_link/elevator_outer_1_joint"), "angular")
        top_gripper_left_arm_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/top_gripper_bar_link/top_gripper_left_arm_joint"), "angular")
        top_gripper_right_arm_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/top_gripper_bar_link/top_gripper_right_arm_joint"), "angular")
        top_slider_joint = UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath(f"{robot_prim_path}/elevator_outer_2_link/top_slider_joint"), "linear")
        
        set_drive_params(front_left_axle, 1, 1000, 0)
        set_drive_params(front_right_axle, 1, 1000, 0)
        set_drive_params(rear_left_axle, 1, 1000, 0)
        set_drive_params(rear_right_axle, 1, 1000, 0)
               
        set_drive_params(front_left_wheel, 1, 100000000, 0)
        set_drive_params(front_right_wheel, 1, 100000000, 0)
        set_drive_params(rear_left_wheel, 1, 100000000, 0)
        set_drive_params(rear_right_wheel, 1, 100000000, 0)
        
        set_drive_params(arm_roller_bar_joint, 10000000, 100000, 98.0)
        set_drive_params(elevator_center_joint, 10000000, 100000, 98.0)
        set_drive_params(elevator_outer_1_joint, 10000000, 100000, 2000.0)
        set_drive_params(elevator_outer_2_joint, 10000000, 100000, 98.0)
        set_drive_params(top_gripper_left_arm_joint, 10000000, 100000, 98.0)
        set_drive_params(top_gripper_right_arm_joint, 10000000, 100000, 98.0)
        set_drive_params(top_slider_joint, 10000000, 100000, 98.0)
        
        # self.create_lidar(robot_prim_path)
        self.create_imu(robot_prim_path)
        self.create_depth_camera(robot_prim_path)
        self.setup_camera_action_graph(robot_prim_path)
        self.setup_imu_action_graph(robot_prim_path)
        self.setup_robot_action_graph(robot_prim_path)  
        self.set_friction(robot_prim_path)
        return

    def create_lidar(self, robot_prim_path):
        lidar_parent = f"{robot_prim_path}/lidar_link"
        lidar_path = "/lidar"
        self.lidar_prim_path = lidar_parent + lidar_path
        result, prim = omni.kit.commands.execute(
            "RangeSensorCreateLidar",
            path=lidar_path,
            parent=lidar_parent,
            min_range=0.4,
            max_range=25.0,
            draw_points=False,
            draw_lines=True,
            horizontal_fov=360.0,
            vertical_fov=30.0,
            horizontal_resolution=0.4,
            vertical_resolution=4.0,
            rotation_rate=0.0,
            high_lod=False,
            yaw_offset=0.0,
            enable_semantics=False
        )
        return

    def create_imu(self, robot_prim_path):
        imu_parent = f"{robot_prim_path}/zed2i_camera_center"
        imu_path = "/imu"
        self.imu_prim_path = imu_parent + imu_path
        result, prim = omni.kit.commands.execute(
            "IsaacSensorCreateImuSensor",
            path=imu_path,
            parent=imu_parent,
            translation=Gf.Vec3d(0, 0, 0),
            orientation=Gf.Quatd(1, 0, 0, 0),
            visualize=False,
        )
        return        
    
    def create_depth_camera(self, robot_prim_path):
        self.depth_left_camera_path = f"{robot_prim_path}/zed2i_right_camera_optical_frame/left_cam"
        self.depth_right_camera_path = f"{robot_prim_path}/zed2i_right_camera_optical_frame/right_cam"
        self.left_camera = prims.create_prim(
            prim_path=self.depth_left_camera_path,
            prim_type="Camera",
            attributes={
                "focusDistance": 1,
                "focalLength": 24,
                "horizontalAperture": 20.955,
                "verticalAperture": 15.2908,
                "clippingRange": (0.1, 1000000),
                "clippingPlanes": np.array([1.0, 0.0, 1.0, 1.0]),
            },
        )

        self.right_camera = prims.create_prim(
            prim_path=self.depth_right_camera_path,
            prim_type="Camera",
            attributes={
                "focusDistance": 1,
                "focalLength": 24,
                "horizontalAperture": 20.955,
                "verticalAperture": 15.2908,
                "clippingRange": (0.1, 1000000),
                "clippingPlanes": np.array([1.0, 0.0, 1.0, 1.0]),
            },
        )
        # # omni.kit.commands.execute('ChangeProperty',
        # #         prop_path=Sdf.Path('/rift/zed2i_right_camera_isaac_frame/left_cam.xformOp:orient'),
        # #         value=Gf.Quatd(0.0, Gf.Vec3d(1.0, 0.0, 0.0)),
        # #         prev=Gf.Quatd(1.0, Gf.Vec3d(0, 0, 0))
        # #         )

        # # omni.kit.commands.execute('ChangeProperty',
        # #         prop_path=Sdf.Path('/rift/zed2i_right_camera_isaac_frame/right_cam.xformOp:orient'),
        # #         value=Gf.Quatd(0.0, Gf.Vec3d(1.0, 0.0, 0.0)),
        # #         prev=Gf.Quatd(1.0, Gf.Vec3d(0, 0, 0))
        #         )
        return

    def setup_world_action_graph(self):
        og.Controller.edit(
            {"graph_path": "/globalclock", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("ReadSimTime", "omni.isaac.core_nodes.IsaacReadSimulationTime"),
                    ("Context", "omni.isaac.ros2_bridge.ROS2Context"),
                    ("PublishClock", "omni.isaac.ros2_bridge.ROS2PublishClock"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
                    ("Context.outputs:context", "PublishClock.inputs:context"),
                    ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
                ],
            }
        )
        return  
    
    def setup_camera_action_graph(self, robot_prim_path):
        camera_graph = "{}/camera_sensor_graph".format(robot_prim_path)
        enable_left_cam = True
        enable_right_cam = False
        rgbType = "RgbType"
        infoType = "InfoType"
        depthType = "DepthType"
        depthPclType = "DepthPclType"

        def createCamType(side, name, typeNode, topic):
            return {
                "create": [
                    (f"{side}CamHelper{name}", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
                ],
                "connect": [
                    (f"{side}CamViewProduct.outputs:renderProductPath", f"{side}CamHelper{name}.inputs:renderProductPath"),
                    (f"{side}CamSet.outputs:execOut", f"{side}CamHelper{name}.inputs:execIn"),
                    (f"{typeNode}.inputs:value", f"{side}CamHelper{name}.inputs:type"),
                ],
                "setvalues": [
                    (f"{side}CamHelper{name}.inputs:topicName", f"{side.lower()}/{topic}"),
                    (f"{side}CamHelper{name}.inputs:frameId", f"{NAMESPACE}/zed2i_{side.lower()}_camera_frame"),
                    (f"{side}CamHelper{name}.inputs:nodeNamespace", f"/{NAMESPACE}"),
                ]
            }

        def getCamNodes(side, enable):
            camNodes = {
                "create": [
                    (f"{side}CamBranch", "omni.graph.action.Branch"),
                    (f"{side}CamCreateViewport", "omni.isaac.core_nodes.IsaacCreateViewport"),
                    (f"{side}CamViewportResolution", "omni.isaac.core_nodes.IsaacSetViewportResolution"),
                    (f"{side}CamViewProduct", "omni.isaac.core_nodes.IsaacGetViewportRenderProduct"),
                    (f"{side}CamSet", "omni.isaac.core_nodes.IsaacSetCameraOnRenderProduct"),
                ],
                "connect": [
                    ("OnPlaybackTick.outputs:tick", f"{side}CamBranch.inputs:execIn"),
                    (f"{side}CamBranch.outputs:execTrue", f"{side}CamCreateViewport.inputs:execIn"),
                    (f"{side}CamCreateViewport.outputs:execOut", f"{side}CamViewportResolution.inputs:execIn"),
                    (f"{side}CamCreateViewport.outputs:viewport", f"{side}CamViewportResolution.inputs:viewport"),
                    (f"{side}CamCreateViewport.outputs:viewport", f"{side}CamViewProduct.inputs:viewport"),
                    (f"{side}CamViewportResolution.outputs:execOut", f"{side}CamViewProduct.inputs:execIn"),
                    (f"{side}CamViewProduct.outputs:execOut", f"{side}CamSet.inputs:execIn"),
                    (f"{side}CamViewProduct.outputs:renderProductPath", f"{side}CamSet.inputs:renderProductPath"),
                ],
                "setvalues": [
                    (f"{side}CamBranch.inputs:condition", enable),
                    (f"{side}CamCreateViewport.inputs:name", f"{side}Cam"),
                    (f"{side}CamViewportResolution.inputs:width", 640),
                    (f"{side}CamViewportResolution.inputs:height", 360),
                ]
            }
            rgbNodes = createCamType(side, "RGB", rgbType, "rgb")
            infoNodes = createCamType(side, "Info", infoType, "camera_info")
            depthNodes = createCamType(side, "Depth", depthType, "depth")
            depthPClNodes = createCamType(side, "DepthPcl", depthPclType, "depth_pcl")
            camNodes["create"] += rgbNodes["create"] + infoNodes["create"] + depthNodes["create"] + depthPClNodes["create"]
            camNodes["connect"] += rgbNodes["connect"] + infoNodes["connect"] + depthNodes["connect"] + depthPClNodes["connect"]
            camNodes["setvalues"] += rgbNodes["setvalues"] + infoNodes["setvalues"] + depthNodes["setvalues"] + depthPClNodes["setvalues"]
            return camNodes

        leftCamNodes = getCamNodes("Left", enable_left_cam)
        rightCamNodes = getCamNodes("Right", enable_right_cam)
        og.Controller.edit(
            {"graph_path": camera_graph, "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    (rgbType, "omni.graph.nodes.ConstantToken"),
                    (infoType, "omni.graph.nodes.ConstantToken"),
                    (depthType, "omni.graph.nodes.ConstantToken"),
                    (depthPclType, "omni.graph.nodes.ConstantToken"),
                ] + leftCamNodes["create"] + rightCamNodes["create"],

                og.Controller.Keys.CONNECT: leftCamNodes["connect"] + rightCamNodes["connect"],

                og.Controller.Keys.SET_VALUES: [
                    (f"{rgbType}.inputs:value", "rgb"),
                    (f"{infoType}.inputs:value", "camera_info"),
                    (f"{depthType}.inputs:value", "depth"),
                    (f"{depthPclType}.inputs:value", "depth_pcl"),
                ] + leftCamNodes["setvalues"] + rightCamNodes["setvalues"],
            }
        )
        set_target_prims(primPath=f"{camera_graph}/RightCamSet", targetPrimPaths=[self.depth_right_camera_path], inputName="inputs:cameraPrim")
        set_target_prims(primPath=f"{camera_graph}/LeftCamSet", targetPrimPaths=[self.depth_left_camera_path], inputName="inputs:cameraPrim")
        return


    def setup_imu_action_graph(self, robot_prim_path):
        sensor_graph = "{}/imu_sensor_graph".format(robot_prim_path)
        swerve_link = "{}/swerve_chassis_link".format(robot_prim_path)
        lidar_link = "{}/lidar_link/lidar".format(robot_prim_path)

        og.Controller.edit(
            {"graph_path": sensor_graph, "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    # General Nodes
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("SimTime", "omni.isaac.core_nodes.IsaacReadSimulationTime"),
                    ("Context", "omni.isaac.ros2_bridge.ROS2Context"),
                    # Odometry Nodes
                    ("ComputeOdometry", "omni.isaac.core_nodes.IsaacComputeOdometry"),
                    ("PublishOdometry", "omni.isaac.ros2_bridge.ROS2PublishOdometry"),
                    ("RawOdomTransform", "omni.isaac.ros2_bridge.ROS2PublishRawTransformTree"),
                    # LiDAR Nodes
                    # ("ReadLidar", "omni.isaac.range_sensor.IsaacReadLidarBeams"),
                    # ("PublishLidar", "omni.isaac.ros2_bridge.ROS2PublishLaserScan"),
                    # IMU Nodes
                    ("IsaacReadImu", "omni.isaac.sensor.IsaacReadIMU"),
                    ("PublishImu", "omni.isaac.ros2_bridge.ROS2PublishImu"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("PublishOdometry.inputs:nodeNamespace", f"/{NAMESPACE}"),
                    # ("PublishLidar.inputs:nodeNamespace", f"/{NAMESPACE}"),
                    ("PublishImu.inputs:nodeNamespace", f"/{NAMESPACE}"), 
                    # ("PublishLidar.inputs:frameId", f"{NAMESPACE}/lidar_link"),
                    ("RawOdomTransform.inputs:childFrameId", f"{NAMESPACE}/base_link"),
                    ("RawOdomTransform.inputs:parentFrameId", f"{NAMESPACE}/zed/odom"),
                    ("PublishOdometry.inputs:chassisFrameId", f"{NAMESPACE}/base_link"),
                    ("PublishOdometry.inputs:odomFrameId", f"{NAMESPACE}/zed/odom"),
                    # ("PublishImu.inputs:frameId", f"{NAMESPACE}/zed2i_imu_link"),
                    ("PublishImu.inputs:frameId", f"{NAMESPACE}/zed2i_camera_center"),
                    ("PublishOdometry.inputs:topicName", "zed/odom")
                ],
                og.Controller.Keys.CONNECT: [
                    # Odometry Connections
                    ("OnPlaybackTick.outputs:tick", "ComputeOdometry.inputs:execIn"),
                    ("OnPlaybackTick.outputs:tick", "RawOdomTransform.inputs:execIn"),
                    ("ComputeOdometry.outputs:execOut", "PublishOdometry.inputs:execIn"),
                    ("ComputeOdometry.outputs:angularVelocity", "PublishOdometry.inputs:angularVelocity"),
                    ("ComputeOdometry.outputs:linearVelocity", "PublishOdometry.inputs:linearVelocity"),
                    ("ComputeOdometry.outputs:orientation", "PublishOdometry.inputs:orientation"),
                    ("ComputeOdometry.outputs:orientation", "RawOdomTransform.inputs:rotation"),
                    ("ComputeOdometry.outputs:position", "PublishOdometry.inputs:position"),
                    ("ComputeOdometry.outputs:position", "RawOdomTransform.inputs:translation"),
                    ("Context.outputs:context", "PublishOdometry.inputs:context"),
                    ("Context.outputs:context", "RawOdomTransform.inputs:context"),
                    ("SimTime.outputs:simulationTime", "PublishOdometry.inputs:timeStamp"),
                    ("SimTime.outputs:simulationTime", "RawOdomTransform.inputs:timeStamp"),

                    # LiDAR Connections
                    # ("OnPlaybackTick.outputs:tick", "ReadLidar.inputs:execIn"),
                    # ("ReadLidar.outputs:execOut", "PublishLidar.inputs:execIn"),
                    # ("Context.outputs:context", "PublishLidar.inputs:context"),
                    # ("SimTime.outputs:simulationTime", "PublishLidar.inputs:timeStamp"),
                    
                    # ("ReadLidar.outputs:azimuthRange", "PublishLidar.inputs:azimuthRange"),
                    # ("ReadLidar.outputs:depthRange", "PublishLidar.inputs:depthRange"),
                    # ("ReadLidar.outputs:horizontalFov", "PublishLidar.inputs:horizontalFov"),
                    # ("ReadLidar.outputs:horizontalResolution", "PublishLidar.inputs:horizontalResolution"),
                    # ("ReadLidar.outputs:intensitiesData", "PublishLidar.inputs:intensitiesData"),
                    # ("ReadLidar.outputs:linearDepthData", "PublishLidar.inputs:linearDepthData"),
                    # ("ReadLidar.outputs:numCols", "PublishLidar.inputs:numCols"),
                    # ("ReadLidar.outputs:numRows", "PublishLidar.inputs:numRows"),
                    # ("ReadLidar.outputs:rotationRate", "PublishLidar.inputs:rotationRate"),
                    
                    # IMU Connections
                    ("OnPlaybackTick.outputs:tick", "IsaacReadImu.inputs:execIn"),
                    ("IsaacReadImu.outputs:execOut", "PublishImu.inputs:execIn"),
                    ("Context.outputs:context", "PublishImu.inputs:context"),
                    ("SimTime.outputs:simulationTime", "PublishImu.inputs:timeStamp"),

                    ("IsaacReadImu.outputs:angVel", "PublishImu.inputs:angularVelocity"),
                    ("IsaacReadImu.outputs:linAcc", "PublishImu.inputs:linearAcceleration"),
                    ("IsaacReadImu.outputs:orientation", "PublishImu.inputs:orientation"),
                ],
            }
        )
        # Setup target prims for the Odometry and the Lidar
        set_target_prims(primPath=f"{sensor_graph}/ComputeOdometry", targetPrimPaths=[swerve_link], inputName="inputs:chassisPrim")
        set_target_prims(primPath=f"{sensor_graph}/ComputeOdometry", targetPrimPaths=[swerve_link], inputName="inputs:chassisPrim") 
        set_target_prims(primPath=f"{sensor_graph}/IsaacReadImu", targetPrimPaths=[self.imu_prim_path], inputName="inputs:imuPrim")
        return

    def setup_robot_action_graph(self, robot_prim_path):
        robot_controller_path = f"{robot_prim_path}/ros_interface_controller"
        og.Controller.edit(
            {"graph_path": robot_controller_path, "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("ReadSimTime", "omni.isaac.core_nodes.IsaacReadSimulationTime"),
                    ("Context", "omni.isaac.ros2_bridge.ROS2Context"),
                    ("PublishJointState", "omni.isaac.ros2_bridge.ROS2PublishJointState"),
                    ("SubscribeDriveState", "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
                    ("SubscribeArmState", "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
                    ("articulation_controller", "omni.isaac.core_nodes.IsaacArticulationController"),
                    ("arm_articulation_controller", "omni.isaac.core_nodes.IsaacArticulationController"),
                    
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("PublishJointState.inputs:topicName", "isaac_joint_states"),
                    ("SubscribeDriveState.inputs:topicName", "isaac_joint_commands"),
                    ("SubscribeDriveState.inputs:topicName", "isaac_drive_commands"),
                    ("SubscribeArmState.inputs:topicName", "isaac_arm_commands"),
                    ("articulation_controller.inputs:usePath", False),
                    ("arm_articulation_controller.inputs:usePath", False),
                    ("SubscribeDriveState.inputs:nodeNamespace", f"/{NAMESPACE}"),
                    ("SubscribeArmState.inputs:nodeNamespace", f"/{NAMESPACE}"),
                    ("PublishJointState.inputs:nodeNamespace", f"/{NAMESPACE}"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
                    ("OnPlaybackTick.outputs:tick", "SubscribeDriveState.inputs:execIn"),
                    ("OnPlaybackTick.outputs:tick", "SubscribeArmState.inputs:execIn"),
                   
                    ("SubscribeDriveState.outputs:execOut", "articulation_controller.inputs:execIn"),
                    ("SubscribeArmState.outputs:execOut", "arm_articulation_controller.inputs:execIn"),
                    ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),
                    
                    ("Context.outputs:context", "PublishJointState.inputs:context"),
                    ("Context.outputs:context", "SubscribeDriveState.inputs:context"),
                    ("Context.outputs:context", "SubscribeArmState.inputs:context"),
                    
                    ("SubscribeDriveState.outputs:jointNames", "articulation_controller.inputs:jointNames"),
                    ("SubscribeDriveState.outputs:velocityCommand", "articulation_controller.inputs:velocityCommand"),
                    ("SubscribeArmState.outputs:jointNames", "arm_articulation_controller.inputs:jointNames"),
                    ("SubscribeArmState.outputs:positionCommand", "arm_articulation_controller.inputs:positionCommand"),
                ],
            }
        )

        set_target_prims(primPath=f"{robot_controller_path}/articulation_controller", targetPrimPaths=[robot_prim_path])
        set_target_prims(primPath=f"{robot_controller_path}/arm_articulation_controller", targetPrimPaths=[robot_prim_path])
        set_target_prims(primPath=f"{robot_controller_path}/PublishJointState", targetPrimPaths=[robot_prim_path])
        return

    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return
    
    async def setup_post_clear(self):
        return
    
    def world_cleanup(self):
        carb.log_info(f"Removing {self.robot_name}")
        if self._world is not None:
            self._world.scene.remove_object(self.robot_name)
        return