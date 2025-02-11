# Robotic AI Functions

## Overview
This project contains multiple functions that can be accessed through API endpoints. Each function serves a specific purpose and is designed to be consumed via HTTP requests.

## Folder Structure
```
/RAIT
  |-- functions/
      |-- gemini_inference.py
      |-- video_recorder.py
```

## Running the API

## API Endpoints

### 1. Gemini Inference
- **Endpoint:** `/gemini_inference`
- **Method:** `POST`
- **Description:** Performs object detection using Google's Gemini Model on the provided image.
- **Request Body:**
    ```json
    {
        "image": "base64_encoded_image",
        "target_classes": ["class1", "class2"]
    }
    ```
- **Response:** JSON response containing detected objects and their bounding boxes.
    ```json
    {
        "detected_objects": {
            "object_name": [xmin, ymin, xmax, ymax]
        }
    }
    ```

### 2. Video Recorder
- **Endpoint:** `/video_recorder`
- **Method:** `POST`
- **Description:** Records an 8-second video at 30 FPS and saves frames at 2 FPS, while also capturing initial RGB and depth images before each recording.
- **Request Body:**
    ```json
    {
        "num_recordings": 1,
        "action_name": "pouring",
        "objects": ["red soda can", "white cup"]
    }
    ```
- **Response:** JSON response indicating the status of the recording process.
    ```json
    {
        "status": "success",
        "message": "Video and frames saved successfully."
    }
    ```

## Error Handling
The API follows standard HTTP status codes:
- `200 OK` - Successful request
- `400 Bad Request` - Invalid input parameters
- `404 Not Found` - Requested resource not found
- `500 Internal Server Error` - Server-side error
