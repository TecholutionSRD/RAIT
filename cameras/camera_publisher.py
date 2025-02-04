import time
from collections import deque
import threading
from typing import Type, Union, Callable, List
import cv2
import numpy as np
from hi_robotics.vision_ai import Camera
from hi_robotics.network_utils.mqtt_comms import MQTTServer


class ImageQueue:
    def __init__(self, max_size: int = 3):
        self.max_size = max_size
        self.queue = deque()
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def __len__(self):
        with self.lock:
            return len(self.queue)

    def put_image(self, image):
        with self.condition:
            if len(self.queue) == self.max_size:
                self.queue.pop()
            self.queue.appendleft(image)
            self.condition.notify_all()  # Notify any waiting threads that a new image is available

    def get_image(self):
        with self.condition:
            while len(self.queue) == 0:
                self.condition.wait()  # Wait until there is an image available in the queue
            return self.queue[0]

    def get_by_index(self, index):
        with self.lock:
            return self.queue[index]

    def get_length(self):
        with self.lock:
            return len(self.queue)

    def get_all_images(self):
        with self.lock:
            return list(self.queue)


class CameraPublisher:
    def __init__(self, 
                 camera: Type[Camera],
                 queue_size: int = 3,
                 host: str = "",
                 topic_name: str = None,
                 start_publisher: bool = False,
                 debug=False):
        self.camera = camera
        self.image_queue = ImageQueue(queue_size)
        self.subscribers: List[Callable] = []
        self.publisher_thread = None
        self.opened_publisher = False
        self.debug_mode = debug

        # Optional MQTT server setup
        self.mqtt_server = None
        if topic_name:
            self.mqtt_server = MQTTServer(server=host, topic_name=topic_name)

        if start_publisher:
            self.start_publisher()
            self.wait_until_ready()  # Ensure the queue has frames before consumers access it

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        self.subscribers.remove(callback)

    def notify_subscribers(self, images):
        for subscriber in self.subscribers:
            subscriber(images, self.image_queue)

    def start_publisher(self):
        if not self.opened_publisher:
            self.opened_publisher = True
            self.publisher_thread = threading.Thread(target=self.publish_frames, daemon=True)
            self.publisher_thread.start()

    def publish_frames(self):
        while self.opened_publisher:
            try:
                images = self.camera.capture_frame()
                if images is not None:
                    self.image_queue.put_image(images)
                    self.notify_subscribers(images)

                    # Optionally, publish via MQTT
                    if self.mqtt_server:
                        self.publish_via_mqtt(images)

                    # Debugging: Log each frame capture
                    if self.debug_mode:
                        print(f"Captured frame at {time.time()} and added to queue.")
                else:
                    raise ValueError("No image captured from camera.")
            except Exception as e:
                print(f"Error during frame publishing: {e}")
                if self.debug_mode:
                    import traceback
                    traceback.print_exc()
                break

    def publish_via_mqtt(self, images):
        try:
            if self.camera.__class__.__name__ == 'IntelRealSenseCamera':
                self.mqtt_server.publish(images[0].tobytes())
                self.mqtt_server.publish(images[1].tobytes(), topic_name=self.mqtt_server.topic_name + "_depth")
            else:
                self.mqtt_server.publish(images.tobytes())

            if self.debug_mode:
                print("Published frame via MQTT.")
        except Exception as e:
            print(f"Error publishing via MQTT: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()

    def stop_publisher(self):
        if self.opened_publisher:
            self.opened_publisher = False
            if self.publisher_thread is not None:
                self.publisher_thread.join()
            print("Checking Camera Class.")
            if self.camera.__class__.__name__ == 'IntelRealSenseCamera':

                print("Releasing camera.")
                self.camera.release_camera()
                print("Camera Released Waiting for 2 seconds in stop_publisher.")
                time.sleep(0.5)  # Small delay to ensure camera is released
                print("**Publisher stopped and camera released.")
            else:
                print("Camera type not IntelRealSenseCamera. Could not stop camera. Stopping publisher.")

    def toggle_debug_mode(self, debug: bool):
        self.debug_mode = debug
        if debug:
            print("Debug mode enabled for CameraPublisher.")
        else:
            print("Debug mode disabled for CameraPublisher.")

    def wait_until_ready(self, timeout=5):
        """Wait until the image queue has at least one frame, or timeout after a specified period."""
        start_time = time.time()
        while len(self.image_queue) == 0:
            if time.time() - start_time > timeout:
                print("Timeout waiting for the image queue to populate.")
                break
            time.sleep(0.1)  # Small sleep to avoid busy-waiting

    def show_stream(self, window_name='Stream', color=True, depth=False):
        while self.opened_publisher:
            try:
                # This will now block until there is an image in the queue
                image = self.image_queue.get_image()
                if self.camera.__class__.__name__ == 'IntelRealSenseCamera':
                    if color and not depth:
                        cv2.imshow(window_name, image[0])
                    elif depth and not color:
                        cv2.imshow(window_name, image[1])
                    elif color and depth:
                        color_image = image[0]
                        depth_image = image[1]
                        depth_image_3ch = np.stack((depth_image, depth_image, depth_image), axis=-1)
                        combined_image = np.concatenate((color_image, depth_image_3ch), axis=1)
                        cv2.imshow(window_name, combined_image)
                else:
                    cv2.imshow(window_name, image)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyWindow(window_name)
                    break

            except Exception as e:
                print(f"Error displaying stream: {e}")
                if self.debug_mode:
                    import traceback
                    traceback.print_exc()
                break