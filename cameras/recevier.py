"""
This file contains the code for receving images(frames) from the MQTT server.
"""
import asyncio
import websockets
import cv2
import numpy as np
import base64
import json
import io
import logging
import os
import sys
import pyrealsense2 as rs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config.config import load_config

class CameraReceiver:
    """
    Class to receive and process image frames from an MQTT WebSocket server.
    """
    def __init__(self, config):
        """
        Initializes the CameraReceiver with the provided configuration.
        
        Args:
            config (dict): Configuration dictionary containing WebSocket settings.
        """
        self.config = config.get('Stream', {})
        self.camera_config = config.get('Camera', {})
        self.websocket_server = self.config.get("Websocket_server", "")
        self.websocket_topic = self.config.get("Websocket_topic", "")
        self.websocket = None
    
    async def connect(self):
        """
        Establishes a connection to the WebSocket server.
        """
        try:
            uri = f"{self.websocket_server}{self.websocket_topic}"
            self.websocket = await websockets.connect(uri)
            logging.info(f"Connected to WebSocket server at {uri}")
        except (websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake, ConnectionRefusedError) as e:
            logging.error(f"Error connecting to WebSocket server: {e}")
            self.websocket = None

    def _get_intrinsics(self, location:str="India", camera_name:str="D435I"):
        """
        Get the camera intrinsics from the configuration file.
        """
        intrinsics = rs.intrinsics()
        color_intrinsics = self.camera_config[camera_name][location]['Intrinsics']['Color_Intrinsics']
        intrinsics.width = 640
        intrinsics.height = 480
        intrinsics.ppx = color_intrinsics.get('ppx', 0)
        intrinsics.ppy = color_intrinsics.get('ppy', 0) 
        intrinsics.fx = color_intrinsics.get('fx', 0)
        intrinsics.fy = color_intrinsics.get('fy', 0)
        intrinsics.model = rs.distortion.inverse_brown_conrady
        intrinsics.coeffs = [0, 0, 0, 0, 0]
        return intrinsics


    async def decode_frames(self):
        """
        Receives and decodes both color and depth frames from JSON data.
        
        Returns:
            tuple: (color_frame, depth_frame) if successful, else (None, None)
        """
        if self.websocket is None:
            logging.warning("WebSocket connection is not established.")
            return None, None
        
        try:
            json_data = await self.websocket.recv()
            frame_data = json.loads(json_data)
            
            # Decode color frame
            color_data = base64.b64decode(frame_data.get('color', ""))
            color_arr = np.frombuffer(color_data, np.uint8)
            color_frame = cv2.imdecode(color_arr, cv2.IMREAD_COLOR)
            
            # Decode depth frame
            depth_data = base64.b64decode(frame_data.get('depth', ""))
            depth_bytes = io.BytesIO(depth_data)
            depth_frame = np.load(depth_bytes, allow_pickle=True)
            
            return color_frame, depth_frame
        except (json.JSONDecodeError, KeyError, ValueError, cv2.error, Exception) as e:
            logging.error(f"Error decoding frames: {e}")
            return None, None
    
    async def frames(self):
        """
        Asynchronous generator that continuously receives frames.
        
        Yields:
            tuple: (color_frame, depth_frame) until stopped.
        """
        if self.websocket is None:
            logging.error("WebSocket connection is missing. Exiting frame loop.")
            return

        try:
            while True:
                color_frame, depth_frame = await self.decode_frames()
                yield color_frame, depth_frame
        except asyncio.CancelledError:
            logging.info("Frame receiving loop has been cancelled.")
        except websockets.exceptions.ConnectionClosed as e:
            logging.warning(f"WebSocket connection closed unexpectedly: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """
        Closes the WebSocket connection and releases resources.
        """
        if self.websocket:
            await self.websocket.close()
            logging.info("WebSocket connection closed.")
            self.websocket = None

    async def display(self):
        """
        Connects to the WebSocket server and displays the received frames.
        """
        await receiver.connect()
        
        if receiver.websocket:
            async for color_frame, depth_frame in receiver.frames():
                if color_frame is not None:
                    cv2.imshow("Color Frame", color_frame)
                if depth_frame is not None:
                    cv2.imshow("Depth Frame", depth_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cv2.destroyAllWindows()
        await receiver.cleanup()

    async def capture_frames(self, save_path):
        """
        Connects to the WebSocket server, receives one frame, and saves it to the specified location.
        
        Args:
            save_path (str): Directory path where frames will be saved.
        
        Returns:
            dict: A dictionary containing paths to the 'rgb' and 'depth' directories.
        """
        await self.connect()
        
        rgb_dir = f"{save_path}/rgb"
        depth_dir = f"{save_path}/depth"
        
        if not os.path.exists(save_path) or os.path.exists(rgb_dir) or os.path.exists(depth_dir):
            os.makedirs(rgb_dir)
            os.makedirs(depth_dir)
            logging.info(f"Created directories at {save_path}")

        color_frame_path = None
        depth_frame_path = None

        if self.websocket:
            async for color_frame, depth_frame in self.frames():
                if color_frame is not None:
                    color_frame_path = f"{rgb_dir}/image_0.jpg"
                    cv2.imwrite(color_frame_path, color_frame)
                    logging.info(f"Saved color frame to {color_frame_path}")
                
                if depth_frame is not None:
                    depth_frame_path = f"{depth_dir}/image_0.npy"
                    np.save(depth_frame_path, depth_frame)
                    logging.info(f"Saved depth frame to {depth_frame_path}")
                
                break 

        await self.cleanup()
        
        return {
            "rgb": color_frame_path,
            "depth": depth_frame_path
        }


if __name__ == "__main__":
    config = load_config("config/config.yaml")
    receiver = CameraReceiver(config)
    asyncio.run(receiver.display())
    # # asyncio.run(receiver.capture_frames("data/captured_frames"))
    # output = asyncio.run(receiver.capture_frames("data/captured_frames"))
    # print(output)
