# Robotic AI Functions

## Overview
This project contains multiple functions that can be accessed through API endpoints. Each function serves a specific purpose and is designed to be consumed via HTTP requests.

## Folder Structure
```
/RAIT
  |-- functions/
      |-- gemini_inference.py
      |-- video_recorder.py
      |-- dataBase.py
      |-- onboardingInformation.py
      |-- utilFunctions.py
```

## Running the API

## API Endpoints

### 1. Gemini Object Detection
- **Endpoint:** `/detect`
- **Method:** `GET`
- **Description:** Detects objects using the Gemini inference model.
- **Response:**
    ```json
    {
        "objects": ["object1", "object2"]
    }
    ```

### 2. Video Recorder
- **Endpoint:** `/record_video`
- **Method:** `GET`
- **Description:** Records videos for demonstration purposes.
- **Parameters:**
    - `num_recordings` (int): Number of recordings to make
    - `action_name` (string): Name of the action being recorded
    - `objects` (array): List of objects involved
- **Response:**
    ```json
    {
        "comment": "Video recording complete."
    }
    ```

### 3. Knowledge Base Check
- **Endpoint:** `/check_knowledge`
- **Method:** `GET`
- **Description:** Retrieves all known grasps and actions from the database.
- **Response:**
    ```json
    {
        "grasps": ["grasp1", "grasp2"],
        "actions": ["action1", "action2"]
    }
    ```

### 4. Specific Knowledge Check
- **Endpoint:** `/check_specific_knowledge`
- **Method:** `GET`
- **Parameters:**
    - `name` (string): Name of the knowledge item to check
- **Description:** Checks if a specific grasp or action exists in the database.
- **Response:**
    ```json
    {
        "name": "item_name",
        "grasp": true|false,
        "action": true|false
    }
    ```

### 5. Onboarding Information
- **Endpoint:** `/onboarding_information`
- **Method:** `POST`
- **Description:** Handles the onboarding process for new actions.
- **Request Body:**
    ```json
    {
        "action_name": "string",
        "description": "string",
        "objects": ["object1", "object2"],
        "confirm": true|false
    }
    ```
- **Response:**
    ```json
    {
        "status": "success|pending",
        "message": "string",
        "task_id": "string",
        "details": {
            "action_name": "string",
            "description": "string",
            "objects": ["string"]
        }
    }
    ```

### 6. Onboarding Confirmation
- **Endpoint:** `/confirm_onboarding`
- **Method:** `GET`
- **Parameters:**
    - `confirm` (boolean): Confirmation status
- **Description:** Confirms or cancels the onboarding process.
- **Response:** String indicating confirmation status

## Error Handling
The API follows standard HTTP status codes:
- `200 OK` - Successful request
- `400 Bad Request` - Invalid input parameters
- `404 Not Found` - Requested resource not found
- `500 Internal Server Error` - Server-side error

## WebSocket Events
The system also supports real-time communication via WebSocket for the following events:
- Session updates
- Audio streaming
- Function call responses
- System status updates
