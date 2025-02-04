import pyrealsense2 as rs
import numpy as np
from typing import Optional, Union, Tuple, Dict
import signal
import sys
import subprocess
import time
import re

from RAIT.cameras.camera import Camera
from RAIT.cameras.driver_helpers.realsense_settings_helper import RealSenseSettingsHelper, CameraColorSensorSettings, CameraDepthSensorSettings
from RAIT.cameras.exceptions import IntelRealSenseCameraException

class IntelRealSenseCamera(Camera):
    """
    IntelRealSenseCamera class for managing Intel RealSense camera operations.
    This class provides methods to initialize, configure, and capture frames from an Intel RealSense camera. It also includes utilities for retrieving camera settings, depth values, and handling camera resources.
    Attributes:
        camera_id (Optional[int]): The ID of the camera.
        model (Optional[str]): The model of the camera.
        width (int): The width of the camera frame.
        height (int): The height of the camera frame.
        fps (int): The frames per second of the camera feed.
        streaming (bool): Indicates if the camera is currently streaming.
        align_switch (bool): Indicates if color and depth frames should be aligned.
        pipeline_started (bool): Indicates if the camera pipeline has started.
        pipeline (rs.pipeline): The RealSense pipeline object.
        config (rs.config): The RealSense configuration object.
        model_name (Optional[str]): The name of the camera model.
        depth_intrinsics (rs.intrinsics): The intrinsics of the depth stream.
        color_frame (Optional[rs.frame]): The color frame captured from the camera.
        depth_frame (Optional[rs.frame]): The depth frame captured from the camera.
        color_image (Optional[np.ndarray]): The color image captured from the camera.
        depth_image (Optional[np.ndarray]): The depth image captured from the camera.
        depth_scale (float): The scale factor for depth values.
        align (Optional[rs.align]): The align object for aligning color and depth frames.
        profile (Optional[rs.pipeline_profile]): The pipeline profile object.
        device_name (Optional[str]): The name of the camera device.
        depth_sensor (Optional[rs.sensor]): The depth sensor object.
        color_sensor (Optional[rs.sensor]): The color sensor object.
        depth_sensor_helper (Optional[RealSenseSettingsHelper]): Helper for depth sensor settings.
        color_sensor_helper (Optional[RealSenseSettingsHelper]): Helper for color sensor settings.
        color_settings (Optional[Type[CameraColorSensorSettings]]): Color sensor settings class.
        depth_settings (Optional[Type[CameraDepthSensorSettings]]): Depth sensor settings class.
    Methods:
        __init__(self, camera_id: Optional[int] = None, model: Optional[str] = None, width: int = 640, height: int = 480, fps: int = 30, open_pipeline: bool = True, align_switch: bool = True):
            Initializes the IntelRealSenseCamera object with the specified parameters.
        __repr__(self) -> str:
            Returns a string representation of the IntelRealSenseCamera object.
        check_camera_usage(self) -> bool:
        get_model_name(self) -> str:
        get_frames(self):
            Captures and returns the color and depth frames from the camera.
        capture_frame(self) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        get_distance_at_point(self, depth_image: np.ndarray, x: int, y: int) -> float:
        get_filtered_depth(self, depth_frame, pixel: tuple[float, float], depth_scale, kernel_size=5):
            Gets the filtered depth value around a pixel using a kernel.
        get_depth_at_point(self, x: int, y: int, filtered=False) -> Tuple[float, float, float]:
        set_resolution(self, width: int, height: int) -> None:
        set_fps(self, fps: int) -> None:
        get_setting_value(self, setting_name: str, sensor_type: str) -> Dict[str, float]:
        set_setting_value(self, setting_name: str, value: float, sensor_type: str, percentage=True) -> None:
        start_camera(self, default=True) -> None:
        release_camera(self) -> None:
            Releases camera resources with proper cleanup.
        get_intrinsics(self, depth: bool) -> Dict[str, rs.intrinsics]:
            Gets the intrinsics of the camera.
   """
    def __init__(self, camera_id: Optional[int] = None, model: Optional[str] = None, 
                 width: int = 640, height: int = 480, fps: int = 30, 
                 open_pipeline: bool = True, align_switch: bool = True):
        
        self.camera_id = camera_id
        self.model = model
        self.width = width
        self.height = height
        self.fps = fps
        self.streaming = False
        self.align_switch = align_switch
        self.pipeline_started = False

        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.model_name = None

        if open_pipeline:
            self.start_camera(default=True)
        
        self.depth_intrinsics = rs.video_stream_profile(self.pipeline.get_active_profile().get_stream(rs.stream.depth)).get_intrinsics()

    def __repr__(self):
        return f'DepthCamera(camera_id={self.camera_id}, width={self.width}, height={self.height}, fps={self.fps})'

    def check_camera_usage(self) -> bool:
        """
        Checks if the camera is being used by another process and tries to identify it.

        :return: bool, True if the camera is busy, False otherwise.
        """
        try:
            # Run the 'lsof' command to find processes using video devices
            result = subprocess.run(['lsof', '/dev/video0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0 and result.stdout:
                print("Camera resource is currently in use by:")
                print(result.stdout)
                return True
            else:
                print("No processes found using the camera.")
                return False
        except FileNotFoundError:
            print("The 'lsof' command is not available on this system.")
            return False
        
    def find_device_by_model(self) -> Tuple[str, str]:
        """
        Finds the first device that matches the provided model regex.

        :return: Tuple containing the serial number and model name of the matched device.
        """
        devices = rs.context().query_devices()
        if len(devices) == 0:
            raise IntelRealSenseCameraException("No RealSense devices connected.")

        for device in devices:
            model_name = device.get_info(rs.camera_info.name)
            if self.model:
                pattern = f".*{self.model}.*"
                if re.match(pattern, model_name, re.IGNORECASE):
                    serial_number = device.get_info(rs.camera_info.serial_number)
                    print(f"Detected device model: {model_name}")
                    return serial_number, model_name

        raise IntelRealSenseCameraException(f"No RealSense device matching model '{self.model}' found.")
    
    def get_model_name(self) -> str:
        """
        Retrieves the full model name of the Intel RealSense camera matching the provided model regex.

        :return: str, The full model name of the camera.
        """
        _, model_name = self.find_device_by_model()
        return model_name

    def get_frames(self):
        frames = self.pipeline.wait_for_frames()
        
        if self.align_switch:
            aligned_frames = self.align.process(frames)

            self.color_frame = aligned_frames.get_color_frame()
            self.depth_frame = aligned_frames.get_depth_frame()
        
        else:
            self.color_frame = frames.get_color_frame()
            self.depth_frame = frames.get_depth_frame()

        return self.color_frame, self.depth_frame
    
    def capture_frame(self) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Retrieves the color and/or depth images from the camera.

        :return: Union[np.ndarray, Tuple[np.ndarray, np.ndarray]], Color image, depth image, or both as specified.
        """

        self.get_frames()
        
        self.color_image =  np.asanyarray(self.color_frame.get_data())
        self.depth_image = np.asanyarray(self.depth_frame.get_data())

        return self.color_image, self.depth_image

    def get_distance_at_point(self, depth_image:np.ndarray, x:int, y:int) -> float:
        """
        Retrieves the distance value at a specific pixel location given a depth image.

        :param depth_image: np.ndarray, The depth image.
        :param x: int, The x-coordinate of the pixel.
        :param y: int, The y-coordinate of the pixel.

        :return: float, The distance value at the specified pixel location.
        """ 
        return depth_image[y, x] * self.depth_scale
    
    def get_filtered_depth(self, depth_frame, pixel: tuple[float, float], depth_scale, kernel_size=5):
        """Get filtered depth value around a pixel using a kernel."""
        try:
            u, v = int(pixel[0]), int(pixel[1])
            depth = np.asanyarray(depth_frame.get_data())

            # Extract kernel around the pixel
            half_kernel = kernel_size // 2
            kernel = depth[
                max(0, v - half_kernel) : min(depth.shape[0], v + half_kernel + 1),
                max(0, u - half_kernel) : min(depth.shape[1], u + half_kernel + 1),
            ]

            # Convert to meters
            kernel = kernel * depth_scale

            # Filter out invalid values
            valid_depths = kernel[(kernel > 0) & (kernel < 10)]

            if len(valid_depths) == 0:
                return None

            # Use median filtering to remove outliers
            filtered_depth = np.median(valid_depths)

            return filtered_depth

        except Exception as e:
            print(f"Error getting filtered depth: {e}")
            return None

    def get_depth_at_point(self, x: int, y: int, filtered=False) -> Tuple[float, float, float]:
        """
        Retrieves the depth value at a specific pixel location.
        
        Args:
            x: The x-coordinate of the pixel
            y: The y-coordinate of the pixel
            
        Returns:
            Tuple of (x, y, z) coordinates in meters
        """
        try:
            # Get frame dimensions and check boundaries
            width = self.depth_frame.get_width()
            height = self.depth_frame.get_height()
            
            x = max(0, min(int(x), width - 1))
            y = max(0, min(int(y), height - 1))
            
            # Get depth value
            if not filtered:
                depth = self.depth_frame.get_distance(x, y)
            else:
                depth = self.get_filtered_depth(self.depth_frame, (x, y), self.depth_scale)
            
            # Validate depth
            if depth <= 0 or depth > 10:  # max 10 meters
                print(f"Invalid depth at ({x}, {y}): {depth}m")
                return (0.0, 0.0, 0.0)
            
            # Convert to 3D point
            point_3d = rs.rs2_deproject_pixel_to_point(self.depth_intrinsics, [x, y], depth)
            
            return tuple(map(float, point_3d))
            
        except RuntimeError as e:
            print(f"Depth error at ({x}, {y}): {e}")
            return (0.0, 0.0, 0.0)

    def set_resolution(self, width: int, height: int) -> None:
        """
        Sets the resolution of the camera frame.
        """
        self.release_camera()
        self.width = width
        self.height = height
        self.start_camera()

    def set_fps(self, fps: int) -> None:
        """
        Sets the frames per second of the camera feed.
        """
        self.fps = fps
        self.set_resolution(self.width, self.height)

    def get_setting_value(self, setting_name: str, sensor_type: str) -> Dict[str, float]:
        """
        Retrieves a camera setting value.

        :param setting_name: str, The setting to retrieve. Must be one of the supported settings. View the supported settings in the CameraColorSensorSettings and CameraDepthSensorSettings classes.
        :param sensor_type: str, The sensor type. Must be either 'color' or 'depth'.

        :return: Dict[str, float], The current value, minimum value, maximum value, step value, and default value of the setting.
        """
        if sensor_type == 'color':
            return self.color_sensor_helper.get_camera_setting_value(setting_name)
        elif sensor_type == 'depth':
            return self.depth_sensor_helper.get_camera_setting_value(setting_name)
        else:
            raise IntelRealSenseCameraException(f"Invalid sensor type: {sensor_type}. Must be either 'color' or 'depth'.")
        
    def set_setting_value(self, setting_name: str, value: float, sensor_type: str, percentage=True) -> None:
        """
        Sets a camera setting value.

        :param setting_name: str, The setting to set. Must be one of the supported settings. View the supported settings in the CameraColorSensorSettings and CameraDepthSensorSettings classes.
        :param value: float, The value to set for the setting.
        :param sensor_type: str, The sensor type. Must be either 'color' or 'depth'.
        :param percentage: bool, Whether the value is a percentage. Defaults to True.
        """
        if sensor_type == 'color':
            self.color_sensor_helper.set_camera_setting_value(setting_name, value, percentage)
        elif sensor_type == 'depth':
            self.depth_sensor_helper.set_camera_setting_value(setting_name, value, percentage)
        else:
            raise IntelRealSenseCameraException(f"Invalid sensor type: {sensor_type}. Must be either 'color' or 'depth'.")

    def start_camera(self, default=True) -> None:
        """
        Starts the camera, initializing it based on the model name provided.

        :param default: bool, Whether to set the camera settings to default values. Defaults to True.
        """
        if self.check_camera_usage():
            raise IntelRealSenseCameraException("The camera is currently in use by another process. Please stop the other process and try again.")

        devices = rs.context().query_devices()
        if len(devices) == 0:
            raise IntelRealSenseCameraException("No RealSense devices found.")

        if self.model:
            self.camera_id, self.device_name = self.find_device_by_model()
            self.config.enable_device(self.camera_id)
        elif self.camera_id is None:
            print("No camera ID specified, selecting the first available camera.")
            first_device = devices[0]
            self.camera_id = first_device.get_info(rs.camera_info.serial_number)
            self.device_name = first_device.get_info(rs.camera_info.name)
            self.config.enable_device(self.camera_id)
        else:
            self.config.enable_device(str(self.camera_id))

        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)

        try:
            self.profile = self.pipeline.start(self.config)
            self.depth_sensor = self.profile.get_device().first_depth_sensor()
            if self.device_name == 'Intel RealSense D405':
                self.color_sensor = self.profile.get_device().first_depth_sensor()
                self.color_settings = CameraColorSensorSettings
                self.depth_settings = CameraColorSensorSettings
            else:
                self.color_sensor = self.profile.get_device().first_color_sensor()
                self.color_settings = CameraColorSensorSettings
                self.depth_settings = CameraDepthSensorSettings

            print("Starting Camera")
            print(f"Device Name: {self.device_name}")
            print(f"Camera ID: {self.camera_id}")

            self.depth_sensor_helper = RealSenseSettingsHelper(self.depth_sensor, self.depth_settings)
            self.color_sensor_helper = RealSenseSettingsHelper(self.color_sensor, self.color_settings)
            self.depth_scale = self.depth_sensor.get_depth_scale()

            if self.align_switch:
                self.align = rs.align(rs.stream.color)
                print('Aligning color and depth frames')

            self.pipeline.wait_for_frames()
            self.pipeline_started = True

            if default:
                for setting in self.color_settings:
                    setting_values = self.color_sensor_helper.get_camera_setting_value(setting)
                    self.color_sensor_helper.set_camera_setting_value(setting, setting_values['default_value'], percentage=False)
                    print(f'Color Option {setting} set to {setting_values["default_value"]}')

                for setting in self.depth_settings:
                    setting_values = self.depth_sensor_helper.get_camera_setting_value(setting)
                    self.depth_sensor_helper.set_camera_setting_value(setting, setting_values['default_value'], percentage=False)
                    print(f'Depth Setting {setting} set to {setting_values["default_value"]}')

        except Exception as e:
            print(f"Failed to start camera: {e}")
            self.release_camera()
            raise IntelRealSenseCameraException(f"Failed to start camera: {e}")
        
    def release_camera(self) -> None:
        """Release camera resources with proper cleanup."""
        print("***********Releasing camera resources...")
        try:
            if hasattr(self, 'pipeline') and self.pipeline:
                if self.pipeline_started:
                    print("Stopping pipeline...")
                    self.pipeline.stop()
                    
                    # Wait for resources to be released
                    print("Waiting for resources to be released...")
                    time.sleep(2)
                    
                    # Reset state
                    self.pipeline_started = False
                    self.streaming = False
                    print("Pipeline stopped successfully")
                    
            # Clear device references
            if hasattr(self, 'depth_sensor'):
                self.depth_sensor = None
            if hasattr(self, 'color_sensor'):
                self.color_sensor = None
                
            print("All camera resources released")
            
        except Exception as e:
            print(f"Error during camera release: {e}")
            # Force cleanup on error
            self.pipeline_started = False
            self.streaming = False
            self.pipeline = None
            print(f"Error during camera release: {e}")

    def get_intrinsics(self,depth):
        """
        Get the intrinsics of camera
        """
        color_intrinsics = rs.video_stream_profile(self.pipeline.get_active_profile().get_stream(rs.stream.color)).get_intrinsics()
        depth_intrinsics = rs.video_stream_profile(self.pipeline.get_active_profile().get_stream(rs.stream.depth)).get_intrinsics()
        if depth:
            return {"color_intrinsics":color_intrinsics,"depth_intrinsics":depth_intrinsics}
        else:
            return {"color_intrinsics":color_intrinsics,"depth_intrinsics":None}