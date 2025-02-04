import pyrealsense2 as rs
from enum import Enum
from typing import Union, Dict

from hi_robotics.vision_ai.exceptions import IntelRealSenseCameraException

class CameraColorSensorSettings(Enum):
    EXPOSURE = rs.option.exposure
    WHITE_BALANCE = rs.option.white_balance
    BRIGHTNESS = rs.option.brightness
    CONTRAST = rs.option.contrast
    SATURATION = rs.option.saturation
    SHARPNESS = rs.option.sharpness
    GAMMA = rs.option.gamma
    GAIN = rs.option.gain
    HUE = rs.option.hue
    ENABLE_AUTO_EXPOSURE = rs.option.enable_auto_exposure
    ENABLE_AUTO_WHITE_BALANCE = rs.option.enable_auto_white_balance

class CameraDepthSensorSettings(Enum):
    EXPOSURE = rs.option.exposure
    GAIN = rs.option.gain
    LASER_POWER = rs.option.laser_power
    DEPTH_UNITS = rs.option.depth_units
    ENABLE_AUTO_EXPOSURE = rs.option.enable_auto_exposure

class RealSenseSettingsHelper:
    """
    Helper class for changing and retrieving camera settings.

    :param sensor: pyrealsense2.sensor, The sensor object.
    :param settings: Union[Enum, CameraColorSensorSettings, CameraDepthSensorSettings], The settings to use depending on the sensor type (Color or Depth sensors).
    """
    def __init__ (self, sensor: rs.sensor, settings: Union[CameraColorSensorSettings, CameraDepthSensorSettings]):
        self.settings = settings
        self.sensor = sensor

    def _validate_input(self, setting: Union[str, CameraColorSensorSettings, CameraDepthSensorSettings]) -> Union[CameraColorSensorSettings, CameraDepthSensorSettings]:
        """
        Validates the input setting.

        :param setting_name: Union[str, CameraColorSensorSettings, CameraDepthSensorSettings], The setting to validate.
        
        :return: Union[CameraColorSensorSettings, CameraDepthSensorSettings], The validated setting.
        """

        if isinstance(setting, str):
            setting = setting.upper()
            if setting in CameraColorSensorSettings.__members__:
                setting = CameraColorSensorSettings[setting]
            elif setting in CameraDepthSensorSettings.__members__:
                setting = CameraDepthSensorSettings[setting]
            else:
                raise IntelRealSenseCameraException(f"Invalid setting name: {setting}")
        return setting
        
    def toggle_auto_white_balance(self, toggle: bool) -> None:
        """
        Toggles the auto white balance mode of the camera.

        :param toggle: bool, Whether to enable or disable auto white balance.
        """
        self.sensor.set_option(rs.option.enable_auto_white_balance, int(toggle))

    def toggle_auto_exposure(self, toggle: bool) -> None:
        """
        Toggles the auto exposure mode of the camera.

        :param toggle: bool, Whether to enable or disable auto exposure.
        """

        self.sensor.set_option(rs.option.enable_auto_exposure, int(toggle))

    def get_camera_setting_value(self, setting_name: Union[str, CameraColorSensorSettings, CameraDepthSensorSettings]) -> Dict[str, float]:
        """
        Retrieves a camera setting value.

        :param setting_name: Union[str, CameraColorSensorSettings, CameraDepthSensorSettings], The setting to retrieve. Must be one of the supported settings. View the supported settings in the CameraColorSensorSettings and CameraDepthSensorSettings classes.
        
        :return: Dict[str, float], The current value, minimum value, maximum value, step value, and default value of the setting.
        """
        camera_setting_values = {}

        setting = self._validate_input(setting_name).value
        
        current_value = self.sensor.get_option(setting)
        range = self.sensor.get_option_range(setting)

        camera_setting_values.update({
            'current_value': current_value,
            'minimum_value': range.min,
            'maximum_value': range.max,
            'step_value': range.step,
            'default_value': range.default
        })

        return camera_setting_values

    def set_camera_setting_value(self, setting_name: Union[str, CameraColorSensorSettings, CameraDepthSensorSettings], 
                                 value: float, percentage=True) -> None:
        """
        Sets a camera setting value.

        :param setting_name: Union[str, CameraColorSensorSettings, CameraDepthSensorSettings], The setting to set. Must be one of the supported settings. View the supported settings in the CameraColorSensorSettings and CameraDepthSensorSettings classes.
        :param value: float, The value to set for the setting.
        :param percentage: bool, Whether the value is a percentage. Defaults to True.
        """

        
        setting = self._validate_input(setting_name).value
        range = self.sensor.get_option_range(setting)
        if percentage:
            value = range.min + (range.max - range.min) * value / 100
        elif value < range.min or value > range.max:
            raise IntelRealSenseCameraException(f"Invalid value: {value}. Value must be between {range.min} and {range.max}.")
      
        if int(value%range.step) != 0:
            raise IntelRealSenseCameraException(f"Invalid value: {value}. Value must be a multiple of {range.step}.")

        self.sensor.set_option(setting, value)
        return True