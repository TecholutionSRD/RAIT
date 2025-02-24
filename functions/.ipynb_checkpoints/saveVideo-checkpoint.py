# """
# This file contains the code to save task videos into Google Cloud Storage.
# """
# import vertexai
# from google.cloud import storage
# from google.cloud.exceptions import GoogleCloudError
# from vertexai.generative_models import GenerativeModel, Part
# from google.oauth2 import service_account
# import os
# import sys
# from pathlib import Path
# from typing import Optional

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
# from config.config import load_config

# config = load_config("../config/config.yaml")['GCP_BUCKET_JSON']

# def video_to_bucket(source_path: str, bucket_name: str = "video-analysing") -> Optional[str]:
#     """
#     Upload a video file to Google Cloud Storage bucket.
    
#     Args:
#         source_path (str): Local path to the video file to upload (e.g., /path/to/recordings/Action/sample_n/Action_video.mp4)
#         bucket_name (str): Name of the GCS bucket (default: "video-analysing")
    
#     Returns:
#         Optional[str]: GCS URI of the uploaded file if successful, None if failed
#     """
#     try:
#         if not source_path:
#             raise ValueError("Source path must not be empty")
        
#         source_path = Path(source_path)
#         if not source_path.exists():
#             raise FileNotFoundError(f"Source file not found: {source_path}")

#         # Extract components from path
#         parts = source_path.parts
#         try:
#             recordings_idx = parts.index('recordings')
#             action = parts[recordings_idx + 1]
#             sample = parts[recordings_idx + 2]
#             video_name = parts[-1]
            
#             # Construct destination path
#             destination_blob_name = f"recordings/{action}/{sample}/{video_name}"
            
#         except (ValueError, IndexError):
#             raise ValueError("Source path does not follow expected pattern: recordings/action/sample_n/video.mp4")

#         valid_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
#         if source_path.suffix.lower() not in valid_extensions:
#             raise ValueError(f"Invalid video format. Supported formats: {valid_extensions}")

#         json_path = config.get("path")
#         if not json_path or not Path(json_path).exists():
#             raise ValueError("Invalid or missing GCP credentials path")
            
#         os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
        
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
        
#         blob = bucket.blob(destination_blob_name)
#         blob.upload_from_filename(str(source_path))
        
#         gs_url = f"gs://{bucket.name}/{destination_blob_name}"
#         return gs_url

#     except (GoogleCloudError, ValueError, FileNotFoundError) as e:
#         print(f"Error uploading video: {str(e)}")
#         return None
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return None

# # Example usage
# if __name__ == "__main__":
#     source_video_path = "/home/shreyas/Desktop/Stream/data/recordings/Pouring/sample_1/Pouring_video.mp4"
#     gcp_url = video_to_bucket(source_path=source_video_path)
#     if gcp_url:
#         print(f"Upload successful. GCS URI: {gcp_url}")
#     else:
#         print("Upload failed")
#----------------------------------------------------------------------------------------------------------------------#
# Siddhartha's Code

# """
# This file contains the code to save task videos into Google Cloud Storage.
# """
# import vertexai
# from google.cloud import storage
# from google.cloud.exceptions import GoogleCloudError
# from vertexai.generative_models import GenerativeModel, Part
# from google.oauth2 import service_account
# import os
# import sys
# from pathlib import Path
# from typing import Optional

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
# from config.config import load_config

# config = load_config("../config/config.yaml")['GCP_BUCKET_JSON']

# def video_to_bucket(source_path: str, bucket_name: str = "video-analysing") -> Optional[str]:
#     """
#     Upload a video file to Google Cloud Storage bucket and return a public URL.
    
#     Args:
#         source_path (str): Local path to the video file to upload (e.g., /path/to/recordings/Action/sample_n/Action_video.mp4)
#         bucket_name (str): Name of the GCS bucket (default: "video-analysing")
    
#     Returns:
#         Optional[str]: Public URL of the uploaded file if successful, None if failed
#     """
#     try:
#         if not source_path:
#             raise ValueError("Source path must not be empty")
        
#         source_path = Path(source_path)
#         if not source_path.exists():
#             raise FileNotFoundError(f"Source file not found: {source_path}")

#         # Extract components from path
#         parts = source_path.parts
#         try:
#             recordings_idx = parts.index('recordings')
#             action = parts[recordings_idx + 1]
#             sample = parts[recordings_idx + 2]
#             video_name = parts[-1]
            
#             # Construct destination path
#             destination_blob_name = f"recordings/{action}/{sample}/{video_name}"
            
#         except (ValueError, IndexError):
#             raise ValueError("Source path does not follow expected pattern: recordings/action/sample_n/video.mp4")

#         valid_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
#         if source_path.suffix.lower() not in valid_extensions:
#             raise ValueError(f"Invalid video format. Supported formats: {valid_extensions}")

#         json_path = config.get("path")
#         if not json_path or not Path(json_path).exists():
#             raise ValueError("Invalid or missing GCP credentials path")
            
#         os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
        
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
        
#         blob = bucket.blob(destination_blob_name)
#         blob.content_type = 'video/mp4'
#         blob.upload_from_filename(str(source_path))
        
#         # Generate public URL (Uniform Bucket-Level Access required)
#         public_url = f"https://storage.googleapis.com/{bucket.name}/{destination_blob_name}"
#         return public_url

#     except (GoogleCloudError, ValueError, FileNotFoundError) as e:
#         print(f"Error uploading video: {str(e)}")
#         return None
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return None

# # Example usage
# if __name__ == "__main__":
#     source_video_path = "/home/shreyas/Desktop/Stream/data/recordings/Pouring/sample_1/Pouring_video.mp4"
#     gcp_url = video_to_bucket(source_path=source_video_path)
#     if gcp_url:
#         print(f"Upload successful. Public URL: {gcp_url}")
#     else:
#         print("Upload failed")
#----------------------------------------------------------------------------------------------------------------------#
# Shreyas's Code
"""
This file contains the code to save task videos into Google Cloud Storage.
"""
import sys
import os
from pathlib import Path
from typing import Optional
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config.config import load_config

config = load_config("../config/config.yaml")['GCP_BUCKET_JSON']

def video_to_bucket(source_path: str, bucket_name: str = "video-analysing") -> Optional[str]:
    """
    Upload a video file to Google Cloud Storage and return normal URL.
    
    Args:
        source_path (str): Local path to video file
        bucket_name (str): GCS bucket name
    Returns:
        Optional[str]: Normal URL if successful, None if failed
    """
    try:
        # Validate source path
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Validate video format
        valid_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
        if source_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Invalid video format. Supported: {valid_extensions}")
            
        # Convert the video first
        converted_path = convert_video(str(source_path))
        if not converted_path:
            raise RuntimeError("Video conversion failed")

        # Extract path components for the converted video
        converted_source_path = Path(converted_path)
        parts = converted_source_path.parts
        recordings_idx = parts.index('recordings')
        action = parts[recordings_idx + 1]
        sample = parts[recordings_idx + 2]
        video_name = parts[-1]
        
        # Set destination path
        destination_blob_name = f"recordings/{action}/{sample}/{video_name}"

        # Initialize GCS client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/ai-hand.json"
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Upload with content type
        blob = bucket.blob(destination_blob_name)
        blob.content_type = 'video/mp4'  # Set proper MIME type
        blob.upload_from_filename(converted_path)
        
        # Return the normal URL (not public)
        # Generate public URL (Uniform Bucket-Level Access required)
        public_url = f"https://storage.googleapis.com/{bucket.name}/{destination_blob_name}"
        return public_url

        
        print(f"Upload successful: {bucket_url}")
        return bucket_url

    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return None

def convert_video(input_path: str) -> Optional[str]:
    """
    Converts the video into the required format.
    
    Args:
        input_path (str): Path to the input video file
    
    Returns:
        Optional[str]: Path to the converted video if successful, None otherwise
    """
    try:
        # Create output path with "_converted.mp4" suffix
        input_path_obj = Path(input_path)
        stem = input_path_obj.stem
        output_path = str(input_path_obj.with_name(f"{stem}_converted.mp4"))
        
        # Run ffmpeg command
        command = f"ffmpeg -i '{input_path}' -vcodec libx264 -acodec aac '{output_path}'"
        result = os.system(command)
        
        if result == 0:
            print(f"Video conversion successful: {output_path}")
            return output_path
        else:
            print(f"Video conversion failed with exit code: {result}")
            return None
            
    except Exception as e:
        print(f"Video conversion error: {str(e)}")
        return None
    
if __name__ == "__main__":
    video_path = "../../Realtime-WebRTC/data/recordings/Grasping/sample_7/Grasping_video.mp4"
    url = video_to_bucket(video_path)
    if url:
        print(f"Video available at: {url}")