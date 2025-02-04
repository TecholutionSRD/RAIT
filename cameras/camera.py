from abc import ABC, abstractmethod

class Camera(ABC):
    """
    Base class for all cameras.

    All camera classes should inherit from this class.

    This forces all camera classes to implement the following methods:
    - start_camera
    - release_camera
    - capture_frame

    This allows for a consistent interface for all camera classes.
    """
    @abstractmethod
    def start_camera(self):
        pass

    @abstractmethod
    def release_camera(self):
        pass

    @abstractmethod
    def capture_frame(self):
        """
        Capture a frame from the camera.

        Returns:
            For RGB cameras: np.ndarray (the frame)
            For depth cameras: Tuple[np.ndarray, np.ndarray] (color frame, depth frame)
        """
        pass
