"""
This file contains the codes for Google's Gemini Model Inference. 
"""
import asyncio
import time
import os
import threading
from typing import List, Dict, Optional, Tuple
from PIL import Image
import json
import json_repair
import numpy as np
import google.generativeai as genai
from pathlib import Path
import cv2
import sys
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config.config import load_config
from cameras.recevier import CameraReceiver
from functions.utilFunctions import deproject_pixel_to_point, transform_coordinates


class Gemini_Inference:
    """
    Gemini Inference is the class used for various inference tasks using Google's Gemini Model.
    Mainly the task is of object detection.
    
    Args:
        api_key (str): API key for accessing the Gemini model.
        recording_dir (Path): Directory containing the video recording.
        inference_mode (bool): Flag to control whether inference should be performed.
        target_classes (List[str]): List of target classes for detection.
    """
    def __init__(self, config, inference_mode: bool = False):
        self.config = config.get('Gemini', {})
        self.configure_gemini(gemini_api_key)
        self.model = genai.GenerativeModel(model_name=self.config["model_name"])
        self.recording_dir = Path(self.config['recording_dir'])
        self.inference_mode = inference_mode
        self.lock = threading.Lock()
        self.detection_results = None
        self.process_results = None
        self.boxes = None
        self.target_classes = []
        self.default_prompt = (
            "Return bounding boxes for objects in the format:\n"
            "```json\n{'<object_name>': [xmin, ymin, xmax, ymax]}\n```\n"
            "Include multiple instances of objects as '<object_name>_1', '<object_name>_2', etc."
        )
        self.detection_prompt = (
            "You are a world-class computer vision expert. Analyze this image carefully and detect "
            "all objects with detailed, specific descriptions. For example, use 'red soda can' instead of just 'can'. "
            "Include color, brand names, or distinctive features when possible. "
            "Return bounding boxes in the following JSON format:\n"
            "{'<detailed_object_name>': [xmin, ymin, xmax, ymax]}\n"
            "For multiple instances of similar objects, append numbers like '<detailed_object_name>_1', '<detailed_object_name>_2'.\n"
            "Focus on accuracy and detail in object descriptions."
        )
        # self.detection_prompt = ("You are a world-class computer vision expert. Analyze this image carefully and detect all objects with detailed descriptions." "If an object is unique in the image, a general description (e.g., 'soda can') is sufficient. However, if multiple similar objects are present, use specific identifiers such as color, brand names, or distinctive features (e.g., 'red Coca-Cola can', 'blue Pepsi can')")
        self.capture_state = False
    
    @staticmethod
    def configure_gemini(api_key: str) -> None:
        """Configure Gemini API."""
        genai.configure(api_key=api_key)

    def set_target_classes(self, target_classes: List[str]) -> None:
        """
        Set the target classes for detection.
        
        Args:
            target_classes (List[str]): List of target classes.
        """
        self.target_classes = target_classes

    def process_frame(self, image: Image.Image):
        """
        Process a single frame for object detection.
        
        Args:
            image (Image.Image): The input image.
        """
        prompt = self.default_prompt
        if self.target_classes:
            prompt += "\nDetect the following classes: " + ", ".join(self.target_classes if self.target_classes else ["everything"])

        response = self.model.generate_content([image, prompt])
        try:
            detection_results = json.loads(json_repair.repair_json(response.text))
        except ValueError as e:
            detection_results = {}
            print(f"Error parsing detection results: {e}")

        with self.lock:
            self.process_results = detection_results
        
    def get_process_frame_results(self) -> Optional[Dict]:
        """
        Get the results of the processed frame.
        
        Returns:
            dict: The processed frame results.
        """
        with self.lock:
            return self.process_results  
        
    def get_object_detection_results(self) -> Optional[Dict]:
        """
        Get the latest object detection results.
        
        Returns:
            dict: The object detection results.
        """
        with self.lock:
            return self.detection_results
    
    def set_inference_state(self, state: bool):
        """
        Enable or disable inference mode.
        
        Args:
            state (bool): True to enable inference, False to disable.
        """
        self.inference_mode = state

    def set_capture_state(self, state:bool):
        """
        Enable or disable capture mode.
        
        Args:
            state (bool): True to enable capture, False to disable.
        """
        self.capture_state = state
    
    def get_object_center(self, image: Image.Image, target_class: str, save_path:str) -> Optional[Dict]:
        """
        Get the center and bounding box of a detected object.
        
        Args:
            image (Image.Image): The input image.
            target_class (str): The target class name.
        
        Returns:
            dict: A dictionary containing the center coordinates, bounding box, and confidence score.
        """

        self.process_frame(image)
        results = self.get_process_frame_results()
        print("-"*100)
        print(results)
        if not results or target_class not in results:
            return None

        box = results[target_class]
        box = self.normalize_box(box)
        center_x = (box[0] + box[2]) // 2
        center_y = (box[1] + box[3]) // 2
        detection_results = {"center": (center_x, center_y), "box": box, "confidence": 100}
        print(f"Normalized Box: {box}")
        self.detection_results = detection_results
        
        return detection_results
    
    def get_object_centers(self, im_folderpath:str = None , im: Image = None, target_classes: List[str] = None) -> Dict[str, Tuple[Optional[int], Optional[int], Optional[np.ndarray], Optional[float]]]:
        """
        Get the centers of the detected objects for the given target classes.
        
        Args:
            im: PIL Image
            target_classes (List[str]): List of object classes to detect
                
        Returns:
            Dict[str, Tuple[Optional[int], Optional[int], Optional[np.ndarray], Optional[float]]]: 
                Dictionary with target class as key and tuple of center coordinates, bounding box, confidence score as value. 
                All None if detection fails for a class.
        """
        centers = {}
        unscaled_boxes = None

        if not im:
            # Open the latest image path for the given folder
            image_files = sorted(Path(f'{im_folderpath}').glob('*.jpg'), key=os.path.getmtime)
            if image_files:
                im = Image.open(image_files[-1])
            else:
                raise FileNotFoundError("No .jpg files found in the specified directory.")

        if target_classes:
            self.set_target_classes(target_classes=target_classes)
        
        self.process_frame(im)
        unscaled_boxes = self.get_process_frame_results()

        self.boxes = unscaled_boxes
        print("visualizing detections")
        self.visualize_detections(im, unscaled_boxes, self.recording_dir)
        boxes = self.get_real_boxes()
        print(f"Boxes: {boxes}")

        for target_class, box in boxes.items():
            confidence = 100
        
            center_x = int((box[0] + box[2]) / 2)
            center_y = int((box[1] + box[3]) / 2)
            
            centers[target_class] = {"center":[center_x, center_y], "bboxes":box, "confidence":confidence}
            print(f"Center for {target_class}: {centers[target_class]}")
        
        self.detection_results = centers
        return centers

    async def detect(self, camera, target_class: List[str] = ['red soda can']):
        """
        Processes the captured images to detect an object and calculate its real-world coordinates.
        
        :param camera: Camera instance
        :param target_class: List of target objects to detect
        :return: Transformed real-world coordinates of the detected object
        """
        recording_dir = self.config.get("recording_dir")
        save_path = f"{recording_dir}/{int(time.time())}"
        frames = await camera.capture_frames(save_path)
        color_frame_path = frames.get('rgb')
        depth_frame_path = frames.get('depth')

        intrinsics = camera._get_intrinsics(location='India', camera_name='D435I')
        
        self.set_target_classes(target_class)
        color_image = Image.open(color_frame_path)
        print("Gemini Inference: Processing frame...")
        output = self.get_object_center(color_image, target_class[0],save_path)
        print(f"Output: {output}")
        
        pixel_center = output.get('center')
        print(f"Pixel Center Type: {type(pixel_center)}")
        print(f"Pixel Center Value: {pixel_center}")
        
        if not pixel_center:
            print("No object detected.")
            return None
        
        print("Depth image path: ", depth_frame_path)
        depth_image = np.load(depth_frame_path)
        print(f"Shape of Depth: {depth_image.shape}")
        print("Deprojecting pixel to point...")
        try:
            depth_center = deproject_pixel_to_point(depth_image,pixel_center, intrinsics=intrinsics)
        except Exception as e:
            print(f"Error deprojecting pixel: {e}")
            return None
        
        print(f"Depth Center: {depth_center}")
        transformed_center = transform_coordinates(*depth_center)
        print(f"Transformed Center: {transformed_center}")

        return transformed_center

    def detect_objects(self, rgb_frame: Image.Image) -> List[str]:
        """
        Run detection on a single RGB frame and return detected object names.
        
        Args:
            rgb_frame (Image.Image): RGB frame as PIL Image
            
        Returns:
            List[str]: List of detected object names
        """
        # Use detection_prompt instead of default_prompt
        prompt = self.detection_prompt
        if self.target_classes:
            prompt += "\nDetect the following classes: " + ", ".join(self.target_classes)
            
        response = self.model.generate_content([rgb_frame, prompt])
        try:
            results = json.loads(json_repair.repair_json(response.text))
        except ValueError as e:
            print(f"Error parsing detection results: {e}")
            return []
        print("-"*50)
        print(response)
        print("-"*50)
        with self.lock:
            self.process_results = results
            
        if not results:
            return []
        
        object_names = []
        for key in results.keys():
            base_name = key.rsplit('_', 1)[0]  
            if base_name not in object_names:
                object_names.append(base_name)
        print("-"*50)
        print(results)
        print("-"*50)
        
        # image_array = np.array(image)
        # box = detection_results['box']
        # cv2.rectangle(image_array, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        # cv2.circle(image_array, (center_x, center_y), 5, (255, 0, 0), -1)
        # output_path = f"{save_path}/detection_image.jpg"
        # cv2.imwrite(str(output_path), cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
        # print("-"*50)
        # print("Saved Detections")
        
        return object_names

    
    def normalize_box(self, box, width=640, height=480):
        """
        Normalize bounding boxes from pixel coordinates to [0, 1] range.

        Args:
            boxes (list): List of bounding boxes in [ymin, xmin, ymax, xmax] format.
            width (int): Image width.
            height (int): Image height.

        Returns:
            list: Normalized bounding boxes in [ymin, xmin, ymax, xmax] format.
        """

        ymin, xmin, ymax, xmax = box
        normalized_box = [ xmin / 1000*width, ymin / 1000*height, xmax / 1000*width, ymax / 1000*height]
        return normalized_box
    
if __name__ == "__main__":

    async def main():
        config = load_config("config/config.yaml")
        camera = CameraReceiver(config)
        gemini = Gemini_Inference(config)
        # camera = None
        detected_objects = await gemini.detect(camera, target_class=['bottle'])
        print(f"Detected objects: {detected_objects}")
    asyncio.run(main())
    