from typing import List
import cv2
import os
import time
import asyncio
import numpy as np
import sys
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from cameras.recevier import CameraReceiver
from config.config import load_config

# class VideoRecorder:
#     """
#     Class to record an 8-second video at 30 FPS and save frames at 2 FPS,
#     while also capturing initial RGB and depth images before each recording.
#     """
#     def __init__(self, receiver, config, num_recordings, action_name, objects):
#         """
#         Initializes the VideoRecorder with the provided CameraReceiver instance and additional parameters.
        
#         Args:
#             receiver (CameraReceiver): Instance of CameraReceiver to get frames.
#             config (dict): Configuration dictionary for video recording.
#             num_recordings (int): Number of recordings to perform.
#             action_name (str): Name of the action being performed (for logging or naming).
#             objects (List[str]): List of objects detected or relevant to the recording.
#         """
#         self.config = config.get("Video_Recorder", {})
#         self.receiver = receiver
#         self.output_dir = self.config['data_path']
#         self.num_recordings = num_recordings
#         self.action_name = action_name
#         self.objects = objects
#         self.sample_count = 0
#         existing_samples = [d for d in os.listdir(self.output_dir) if d.startswith("sample_")]
#         self.sample_count = len(existing_samples)
#         os.makedirs(self.output_dir, exist_ok=True)
    
#     def create_sample_directory(self):
#         """
#         Creates a new sample directory structure for storing video and frames.
#         """
#         self.sample_count += 1
#         sample_folder = os.path.join(self.output_dir, f"sample_{self.sample_count}")
#         os.makedirs(sample_folder, exist_ok=True)
#         os.makedirs(os.path.join(sample_folder, "rgb"), exist_ok=True)
#         os.makedirs(os.path.join(sample_folder, "depth"), exist_ok=True)
#         os.makedirs(os.path.join(sample_folder, "initial_frames"), exist_ok=True)
#         return sample_folder
    
#     async def capture_initial_frames(self, sample_folder):
#         """
#         Captures a single RGB and depth frame and saves them before video recording.
        
#         Args:
#             sample_folder (str): Path to the current sample folder.
#         """
#         color_frame, depth_frame = await self.receiver.decode_frames()
#         if color_frame is not None:
#             cv2.imwrite(os.path.join(sample_folder, "initial_frames", "image_0.png"), color_frame)
#             cv2.imshow("Initial RGB Frame", color_frame)
#             cv2.waitKey(1)
#         if depth_frame is not None:
#             np.save(os.path.join(sample_folder, "initial_frames", "image_0.npy"), depth_frame)
#         print("Initial frames captured.")
    
#     async def record_video(self):
#         """
#         Records videos based on the number of samples in the configuration.
#         Records at exact FPS and saves all frames, including action name and objects in the file names.
#         """
#         for _ in range(self.num_recordings):
#             sample_folder = self.create_sample_directory()

#             action_folder = os.path.join(sample_folder, self.action_name)
#             os.makedirs(action_folder, exist_ok=True)
#             with open(os.path.join(action_folder, "objects.txt"), 'w') as f:
#                 for obj in self.objects:
#                     f.write(f"{obj}\n")

#             await self.capture_initial_frames(sample_folder)

#             for i in range(5, 0, -1):
#                 print(f"Waiting for {i} seconds before starting recording...")
#                 await asyncio.sleep(1)

#             print("Recording video...")
#             video_path = os.path.join(sample_folder, f"{self.action_name}_video.{self.config['video_format']}")
#             fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#             frame_size = (self.config['width'], self.config['height'])
            
#             out = cv2.VideoWriter(video_path, fourcc, self.config['video_fps'], frame_size)
            
#             if not out.isOpened():
#                 print("Error: VideoWriter failed to open.")
#                 return

#             start_time = time.time()
#             frame_count = 0
#             frame_time = 1.0 / self.config['video_fps']
#             next_frame_time = start_time

#             total_frames = int(self.config['video_duration'] * self.config['video_fps'])

#             while frame_count < total_frames:
#                 current_time = time.time()
                
#                 if current_time < next_frame_time:
#                     await asyncio.sleep(next_frame_time - current_time)
#                     continue

#                 color_frame, depth_frame = await self.receiver.decode_frames()

#                 if color_frame is not None:
#                     if color_frame.shape[1] != self.config['width'] or color_frame.shape[0] != self.config['height']:
#                         color_frame = cv2.resize(color_frame, frame_size)

#                     if len(color_frame.shape) == 3 and color_frame.shape[2] == 3:
#                         color_frame = cv2.cvtColor(color_frame, cv2.COLOR_RGB2BGR)

#                     out.write(color_frame)
#                     cv2.imshow("Live RGB Feed", color_frame)
#                     cv2.waitKey(1)
#                     frame_filename = f"{self.action_name}_image_{frame_count:03d}.png"
#                     cv2.imwrite(os.path.join(sample_folder, "rgb", frame_filename), color_frame)

#                 if depth_frame is not None:
#                     np.save(os.path.join(sample_folder, "depth", f"{self.action_name}_image_{frame_count:03d}.npy"), depth_frame)

#                 frame_count += 1
#                 next_frame_time = start_time + (frame_count * frame_time)

#             out.release()
#             cv2.destroyAllWindows()
#             print(f"Video and frames saved in {sample_folder}")
#             print(f"Total frames recorded: {frame_count}")

#     async def display_live_feed(self):
#         """
#         Displays the live feed from the receiver after recording completes.
#         """
#         print("Displaying live feed...")
#         while True:
#             color_frame, _ = await self.receiver.decode_frames()
#             if color_frame is not None:
#                 cv2.imshow("Live RGB Feed", color_frame)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#         cv2.destroyAllWindows()
    
# if __name__ == "__main__":
#     config = load_config("config/config.yaml")
#     receiver = CameraReceiver(config)
#     video_config = load_config("config/config.yaml")['Video_Recorder']

#     # Define the parameters to pass to VideoRecorder
#     num_recordings = 1
#     action_name = "pouring"
#     objects = ["red soda can", "white cup"]
#     async def main():
#         await receiver.connect()
#         recorder = VideoRecorder(receiver, config, num_recordings, action_name, objects)
#         await recorder.record_video()
#         await recorder.display_live_feed()

#     asyncio.run(main())



class VideoRecorder:
    """
    Class to record an 8-second video at 30 FPS and save frames at 2 FPS,
    while also capturing initial RGB and depth images before each recording.
    """
    def __init__(self, receiver, config, num_recordings, action_name, objects):
        """
        Initializes the VideoRecorder with the provided CameraReceiver instance and additional parameters.
        
        Args:
            receiver (CameraReceiver): Instance of CameraReceiver to get frames.
            config (dict): Configuration dictionary for video recording.
            num_recordings (int): Number of recordings to perform.
            action_name (str): Name of the action being performed (for logging or naming).
            objects (List[str]): List of objects detected or relevant to the recording.
        """
        self.config = config.get("Video_Recorder", {})
        self.receiver = receiver
        self.output_dir = self.config['data_path']  # Base output directory
        self.num_recordings = num_recordings
        self.action_name = action_name
        self.objects = objects
        self.sample_count = 0
        existing_samples = [d for d in os.listdir(self.output_dir) if d.startswith("sample_")]
        self.sample_count = len(existing_samples)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_sample_directory(self):
        """
        Creates a new sample directory structure under the action name, e.g., "data/recordings/pouring/sample_1".
        """
        self.sample_count += 1
        # Create the action-specific directory structure
        action_folder = os.path.join(self.output_dir, self.action_name)
        os.makedirs(action_folder, exist_ok=True)
        
        sample_folder = os.path.join(action_folder, f"sample_{self.sample_count}")
        os.makedirs(sample_folder, exist_ok=True)
        
        os.makedirs(os.path.join(sample_folder, "rgb"), exist_ok=True)
        os.makedirs(os.path.join(sample_folder, "depth"), exist_ok=True)
        os.makedirs(os.path.join(sample_folder, "initial_frames"), exist_ok=True)
        
        return sample_folder
    
    async def capture_initial_frames(self, sample_folder):
        """
        Captures a single RGB and depth frame and saves them before video recording.
        
        Args:
            sample_folder (str): Path to the current sample folder.
        """
        color_frame, depth_frame = await self.receiver.decode_frames()
        if color_frame is not None:
            cv2.imwrite(os.path.join(sample_folder, "initial_frames", "image_0.png"), color_frame)
            cv2.imshow("Initial RGB Frame", color_frame)
            cv2.waitKey(1)
        if depth_frame is not None:
            np.save(os.path.join(sample_folder, "initial_frames", "image_0.npy"), depth_frame)
        print("Initial frames captured.")
    
    async def record_video(self):
        """
        Records videos based on the number of samples in the configuration.
        Records at exact FPS and saves all frames, including action name and objects in the file names.
        """
        for _ in range(self.num_recordings):
            sample_folder = self.create_sample_directory()

            action_folder = os.path.join(sample_folder, self.action_name)
            os.makedirs(action_folder, exist_ok=True)
            with open(os.path.join(action_folder, "objects.txt"), 'w') as f:
                for obj in self.objects:
                    f.write(f"{obj}\n")

            await self.capture_initial_frames(sample_folder)

            for i in range(5, 0, -1):
                print(f"Waiting for {i} seconds before starting recording...")
                await asyncio.sleep(1)

            print("Recording video...")
            video_path = os.path.join(sample_folder, f"{self.action_name}_video.{self.config['video_format']}")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            frame_size = (self.config['width'], self.config['height'])
            
            out = cv2.VideoWriter(video_path, fourcc, self.config['video_fps'], frame_size)
            
            if not out.isOpened():
                print("Error: VideoWriter failed to open.")
                return

            start_time = time.time()
            frame_count = 0
            frame_time = 1.0 / self.config['video_fps']
            next_frame_time = start_time

            total_frames = int(self.config['video_duration'] * self.config['video_fps'])

            while frame_count < total_frames:
                current_time = time.time()
                
                if current_time < next_frame_time:
                    await asyncio.sleep(next_frame_time - current_time)
                    continue

                color_frame, depth_frame = await self.receiver.decode_frames()

                if color_frame is not None:
                    if color_frame.shape[1] != self.config['width'] or color_frame.shape[0] != self.config['height']:
                        color_frame = cv2.resize(color_frame, frame_size)

                    if len(color_frame.shape) == 3 and color_frame.shape[2] == 3:
                        color_frame = cv2.cvtColor(color_frame, cv2.COLOR_RGB2BGR)

                    out.write(color_frame)
                    cv2.imshow("Live RGB Feed", color_frame)
                    cv2.waitKey(1)
                    frame_filename = f"{self.action_name}_image_{frame_count:03d}.png"
                    cv2.imwrite(os.path.join(sample_folder, "rgb", frame_filename), color_frame)

                if depth_frame is not None:
                    np.save(os.path.join(sample_folder, "depth", f"{self.action_name}_image_{frame_count:03d}.npy"), depth_frame)

                frame_count += 1
                next_frame_time = start_time + (frame_count * frame_time)

            out.release()
            cv2.destroyAllWindows()
            print(f"Video and frames saved in {sample_folder}")
            print(f"Total frames recorded: {frame_count}")

    async def display_live_feed(self):
        """
        Displays the live feed from the receiver after recording completes.
        """
        print("Displaying live feed...")
        while True:
            color_frame, _ = await self.receiver.decode_frames()
            if color_frame is not None:
                cv2.imshow("Live RGB Feed", color_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()

if __name__ == "__main__":
    config = load_config("config/config.yaml")
    receiver = CameraReceiver(config)
    video_config = load_config("config/config.yaml")['Video_Recorder']

    # Define the parameters to pass to VideoRecorder
    num_recordings = 1
    action_name = "pouring"
    objects = ["red soda can", "white cup"]
    
    async def main():
        await receiver.connect()
        recorder = VideoRecorder(receiver, config, num_recordings, action_name, objects)
        await recorder.record_video()
        await recorder.display_live_feed()

    asyncio.run(main())
