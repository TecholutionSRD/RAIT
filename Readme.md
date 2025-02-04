# RAIT: Robotics AI Toolkit
A toolkit for robotics computer vision applications, providing camera interfaces and image processing utilities.

## Project Structure
```
RAIT/
├── cameras/
│   ├── __init__.py
│   ├── camera.py                 # Base camera interface
│   ├── camera_publisher.py       # Camera frame publishing
│   ├── intel_realsense_camera.py # Intel RealSense implementation
│   ├── img_operations.py         # Image processing utilities
│   ├── utils.py                  # Helper functions
│   ├── receiver.py               # Frame receiving via WebSocket
│   ├── exceptions.py             # Custom exceptions
│   └── driver_helpers/           # Camera-specific helpers
│       ├── __init__.py
│       ├── realsense_settings_helper.py
│       └── rgb_settings_helper.py
└── config/
    ├── config.py                 # Configuration loader
    └── config.yaml               # Configuration file
```

## Features
- **Camera Interfaces**: Support for various camera models including Intel RealSense.
- **Image Processing**: Utilities for image manipulation and processing.
- **Configuration Management**: Easy configuration through YAML and Python files.
- **WebSocket Support**: Frame receiving and publishing over WebSocket.

<!-- ## Installation
To install the toolkit, run:
```sh
pip install RAIT-toolkit
``` -->

## Usage
Import the necessary modules and start using the toolkit in your project:
```python
from RAIT.cameras.recrvier import CameraReceiver
from RAIT.config.config import load_config
```

## Contributing
Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more details.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.