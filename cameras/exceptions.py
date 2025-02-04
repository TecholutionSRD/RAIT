import traceback

class HIComputerVisionException(Exception):
    """
    Base class for exceptions in the hi_robotics.vision_ai module.
    """
    def __init__(self, message="An error occurred in the hi_robotics.vision_ai module"):
        self.message = f"{message}\n{traceback.format_exc()}"
        super().__init__(self.message)

class ImageOperationsException(HIComputerVisionException):
    """
    Represents an exception that occurred in the ImageOperations class.

    Attributes:
        message (str): The error message.
    """

    def __init__(self, message: str):
        """
        Initializes a ImageOperationsException object.

        Args:
            message (str): The error message.
        """
        super().__init__(message)

    def __str__(self) -> str:
        return self.message
    
class IntelRealSenseCameraException(HIComputerVisionException):
    """
    Represents an exception that occurred in the DepthCamera class.
    """
    def __init__(self, message):
        super().__init__(message)
    
    def __str__(self):
        return self.message
    
class PerceptionException(HIComputerVisionException):
    """
    Custom exception class for perception-related errors.
    """
    def __init__(self, message):
        super().__init__(message)