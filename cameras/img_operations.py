import PIL.Image
import cv2
import numpy as np
import math
import PIL
from typing import Union, Tuple, List, Optional

from hi_robotics.vision_ai.exceptions import ImageOperationsException

def handle_image_types(image: Union[str, np.ndarray, PIL.Image.Image]) -> np.ndarray:
    """
    Converts the given image to a numpy array.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image to convert.

    Returns:
        np.ndarray: The converted image.
    """
    if isinstance(image, str):
        return cv2.imread(image)
    elif isinstance(image, PIL.Image.Image):
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    elif isinstance(image, np.ndarray):
        return image
    else:
        raise ImageOperationsException("Unsupported image type.")
    
def draw_polygon(image: Union[str, np.ndarray, PIL.Image.Image], points: List[Tuple[int, int]], 
                 color: Optional[Tuple] = (0, 255, 0), thickness: Optional[int] = 2, 
                 line_type: Optional[int] = cv2.LINE_8, isClosed: Optional[bool] = True) -> np.ndarray:
    """
    Draws a polygon on the given image.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image on which to draw the polygon.
        points (List[Tuple]): A list of points defining the polygon.
        color (Optional[Tuple]): Color of the polygon. Default is green.
        thickness (Optional[int]): Thickness of the polygon outline. Default is 2.
        line_type (Optional[int]): Type of the line to draw. Default is cv2.LINE_8.
        isClosed (Optional[bool]): Whether the polygon is closed. Default is True.

    Returns:
        np.ndarray: The image with the polygon drawn on it.
    """
    points = np.array(points, dtype=np.int32)
    image = handle_image_types(image)

    return cv2.polylines(
        img=image, 
        pts=[points], 
        isClosed=isClosed, 
        color=color, 
        thickness=thickness, 
        lineType=line_type
    )

def draw_filled_polygon(image: Union[str, np.ndarray, PIL.Image.Image], points: List[Tuple[int, int]],
                        color: Optional[Tuple[int, int, int]] = (0, 255, 0), lineType: Optional[int] = cv2.LINE_AA) -> np.ndarray:
    """
    Draws a filled polygon on the given image.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image on which to draw the filled polygon.
        points (List[Tuple]): A list of points defining the polygon.
        color (Optional[Tuple]): Color of the filled polygon. Default is green.
        lineType (Optional[int]): Type of the line to draw. Default is cv2.LINE_AA.

    Returns:
        np.ndarray: The image with the filled polygon drawn on it.
    """
    points = np.array(points, dtype=np.int32)
    image = handle_image_types(image)
    return cv2.fillPoly(
        img=image, 
        pts=[points], 
        color=color, 
        lineType=lineType
    )

def draw_circle(image: Union[str, np.ndarray, PIL.Image.Image], center: Tuple[int, int], radius: int, 
                color: Optional[Tuple[int, int, int]] = (0, 0, 255), thickness: Optional[int] = 2, 
                line_type: Optional[int] = cv2.LINE_AA) -> np.ndarray:
    """
    Draws a circle on the given image.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image on which to draw the circle.
        center (Tuple): Center of the circle.
        radius (int): Radius of the circle.
        color (Optional[Tuple]): Color of the circle. Default is red.
        thickness (Optional[int]): Thickness of the circle outline. Default is 2.
        line_type (Optional[int]): Type of the line to draw. Default is cv2.LINE_AA.
    """
    image = handle_image_types(image)

    return cv2.circle(
        img=image, 
        center=center, 
        radius=radius, 
        color=color, 
        thickness=thickness, 
        lineType=line_type
    )

def put_text(image: Union[str, np.ndarray, PIL.Image.Image], text: str, org: Tuple[int, int], **kwargs) -> np.ndarray:
    """
    Puts text on the given image.

    Args:
        image (np.ndarray): The image on which to put the text.
        text (str): The text to put on the image.
        org (tuple): Bottom-left corner of the text string in the image.

    Keyword Args:
        fontFace (int): Font type. Default is cv2.FONT_HERSHEY_SIMPLEX.
        fontScale (int): Font scale factor that is multiplied by the font-specific base size. Default is 1.
        color (tuple): Color of the text. Default is white.
        thickness (int): Thickness of the lines used to draw a text. Default is 2.
        line_type (int): Type of the line to draw. Default is cv2.LINE_AA.

    Returns:
        np.ndarray: The image with the text drawn on it.
    """
    fontFace = kwargs.get('fontFace', cv2.FONT_HERSHEY_SIMPLEX)
    fontScale = kwargs.get('fontScale', 1)
    color = kwargs.get('color', (255, 255, 255))
    thickness = kwargs.get('thickness', 2)
    line_type = kwargs.get('line_type', cv2.LINE_AA)

    image = handle_image_types(image)

    return cv2.putText(
        img=image, 
        text=text, 
        org=org, 
        fontFace=fontFace, 
        fontScale=fontScale, 
        color=color, 
        thickness=thickness, 
        lineType=line_type
    )

def mask_overlay(image: Union[str, np.ndarray, PIL.Image.Image], points: List[Tuple[int, int]], border:bool = True, **kwargs) -> np.ndarray:
    """
    Combines an image and its segmentation mask into a single image.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The original image.
        points (List[Tuple]): A list of points defining the mask.
        border (bool): Whether to draw a border around the mask. Default is True.

    Keyword Args:
        color (Tuple): Color of the mask. Default is red.
        alpha (float): Transparency of the mask. Default is 0.5.
        resize (Tuple[Int, Int]): New size of the image. Default is None.
        make_mask (bool): Whether to create an empty mask. Default is True.

    """
    color = kwargs.get('color', (255, 0, 0))
    alpha = kwargs.get('alpha', 0.5)
    resize = kwargs.get('resize', None)

    image = handle_image_types(image)

    if kwargs.get('make_mask', True):
        # Create an empty mask
        mask = np.zeros_like(image)
    else:
        mask = kwargs.get('mask', None)
    
    if kwargs.get('border', True):
        # Draw a border around the mask
        mask = cv2.drawContours(mask, [points], -1, color, -1)
    
    if resize is not None:
        # Resize both the image and mask
        image = cv2.resize(image, resize)
        mask = cv2.resize(mask, resize)
    
    image_combined = cv2.addWeighted(image, 1, mask, alpha, 0)
    return image_combined

def calculate_distance(pt1: tuple, pt2: tuple) -> float:
    """
    Calculates the Euclidean distance between two points.

    Args:
        pt1 (tuple): The first point.
        pt2 (tuple): The second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

def xywh2xyxy(x: int, y: int, w: int, h: int) -> tuple:
    """
    Converts bounding box coordinates from (x, y, width, height) to (x1, y1, x2, y2) format.

    Args:
        x (int): x-coordinate of the center.
        y (int): y-coordinate of the center.
        w (int): Width of the bounding box.
        h (int): Height of the bounding box.

    Returns:
        tuple: The converted coordinates (x1, y1, x2, y2).
    """
    x1, y1 = x - w // 2, y - h // 2
    x2, y2 = x + w // 2, y + h // 2
    return x1, y1, x2, y2

def xyxy2xywh(x1: int, y1: int, x2: int, y2: int) -> tuple:
    """
    Converts bounding box coordinates from (x1, y1, x2, y2) to (x, y, width, height) format.

    Args:
        x1 (int): x-coordinate of the top-left corner.
        y1 (int): y-coordinate of the top-left corner.
        x2 (int): x-coordinate of the bottom-right corner.
        y2 (int): y-coordinate of the bottom-right corner.

    Returns:
        tuple: The converted coordinates (x, y, width, height).
    """
    x = (x1 + x2) // 2
    y = (y1 + y2) // 2
    w = x2 - x1
    h = y2 - y1
    return x, y, w, h

def xywh2points(x: int, y: int, w: int, h: int) -> list:
    """
    Converts bounding box coordinates from (x, y, width, height) to a list of points.

    Args:
        x (int): x-coordinate of the center.
        y (int): y-coordinate of the center.
        w (int): Width of the bounding box.
        h (int): Height of the bounding box.

    Returns:
        list: A list of points defining the bounding box.
    """
    x1, y1, x2, y2 = xywh2xyxy(x, y, w, h)
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def read_image(image_path: str) -> np.ndarray:
    """
    Reads an image from the given path.

    Args:
        image_path (str): The path to the image file.

    Returns:
        np.ndarray: The image.
    """
    return cv2.imread(image_path)

def write_image(image: Union[str, np.ndarray, PIL.Image.Image], output_path: str) -> bool:
    """
    Writes the given image to the output path.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image to write.
        output_path (str): The path to write the image file.

    Returns:
        bool: True if the image was written successfully, False otherwise.
    """
    return cv2.imwrite(output_path, handle_image_types(image))

def show_image(image: Union[str, np.ndarray, PIL.Image.Image], window_name: str = "Image Window") -> None:
    """
    Displays the given image.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image to display.
        window_name (str): The name of the window. Default is None.
    """
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)

def resize_image(image: Union[str, np.ndarray, PIL.Image.Image], size: tuple) -> np.ndarray:
    """
    Resizes the given image to the specified size.

    Args:
        image (Union[str, np.ndarray, PIL.Image.Image]): The image to resize.
        size (tuple): The new size of the image.

    Returns:
        np.ndarray: The resized image.
    """
    return cv2.resize(handle_image_types(image), size)

# TODO: MAKE THIS FUNCTION BETTER THIS IS WAYYYYY TOO LONG
def modify_image(image: np.ndarray, modification_type: str, **kwargs) -> tuple:
    """
    Applies various modifications to the given image.

    Args:
        image (np.ndarray): The image to modify.
        modification_type (str): The type of modification to apply.

                    1) resize: Resizes the image.
                    Keyword Args: width (int), height (int), interpolation (int)

                    2) flip: Flips the image.
                    Keyword Args: flipcode (int)

                    3) bitwise_and: Performs bitwise AND operation with a secondary image.
                    Keyword Args: secondary_image (np.ndarray)

                    4) bitwise_or: Performs bitwise OR operation with a secondary image.
                    Keyword Args: secondary_image (np.ndarray)

                    5) bitwise_not: Performs bitwise NOT operation.

                    6) threshold: Applies a threshold to the image.
                    Keyword Args: threshold_value (int), max_value (int), type (int), gray (bool) to grayscale image before applying

                    7) gaussian_blur: Applies Gaussian blur to the image.
                    Keyword Args: kernel_size (tuple), sigmaX (float)

                    8) grayscale: Converts the image to grayscale.

                    9) bgr2rgb: Converts the image from BGR to RGB.

                    10) color_map: Applies a color map to the image.
                    Keyword Args: colormap (int), alpha (float) for colour scaling

                    11) canny: Applies Canny edge detection to the image.
                    Keyword Args: threshold1 (int), threshold2 (int), gray (bool) to grayscale image before applying

                    12) dilate: Applies dilation to the image.
                    Keyword Args: kernel_size (tuple), iterations (int), gray (bool) to grayscale image before applying

                    13) erode: Applies erosion to the image.
                    Keyword Args: kernel_size (tuple), iterations (int), gray (bool) to grayscale image before applying

                    14) plane_correction: Corrects the perspective of the image.
                    Keyword Args: points (list) in order of [top_left, top_right, bottom_right, bottom_left], width (int), height (int) 

                    15) channel_first: Transposes the image to channel-first format.

                    16) channel_last: Transposes the image to channel-last format.

                    17) normalize: Normalizes the image.
                    Keyword Args: alpha (float), beta (float), norm_type (int), dtype (type)

                    18) stack: Stacks two images along a specified axis.
                    Keyword Args: secondary_image (np.ndarray), axis (int)

                    19) make_3_channel: Converts the image to a 3-channel image.



    Returns:
        tuple: A tuple containing a boolean indicating success and the modified image.
    """
    ret = False

    if modification_type == 'resize':
        width, height = kwargs.get('width'), kwargs.get('height')
        if any(v is None for v in [width, height]):
            raise ImageOperationsException('Width and height not found')
        interpolation = kwargs.get('interpolation', cv2.INTER_AREA)
        image = cv2.resize(image, (width, height), interpolation=interpolation)
        ret = True

    elif modification_type == 'flip':
        flipcode = kwargs.get('flipcode', 1)
        image = cv2.flip(image, flipcode)
        ret = True

    elif modification_type == 'bitwise_and':
        image2 = kwargs.get('secondary_image')
        if image2 is None:
            raise ImageOperationsException('Secondary image not found')
        image = cv2.bitwise_and(image, image2)
        ret = True

    elif modification_type == 'bitwise_or':
        image2 = kwargs.get('secondary_image')
        if image2 is None:
            raise ImageOperationsException('Secondary image not found')
        image = cv2.bitwise_or(image, image2)
        ret = True

    elif modification_type == 'bitwise_not':
        image = cv2.bitwise_not(image)
        ret = True

    elif modification_type == 'threshold':
        maxval = kwargs.get('max_value', np.max(image))
        thresh = kwargs.get('threshold_value', int(maxval / 2))
        type = kwargs.get('type', cv2.THRESH_BINARY)
        if kwargs.get('gray', True):
            ret, image = self.image_modifications(image, 'grayscale')
        ret, image = cv2.threshold(image, thresh=thresh, maxval=maxval, type=type)
        ret = True

    elif modification_type == 'gaussian_blur':
        kernel_size = kwargs.get('kernel_size', (3, 3))
        sigmaX = kwargs.get('sigmaX', 0)
        image = cv2.GaussianBlur(image, ksize=kernel_size, sigmaX=sigmaX)
        ret = True

    elif modification_type == 'grayscale':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret = True

    elif modification_type == 'bgr2rgb':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ret = True

    elif modification_type == 'color_map':
        colormap = kwargs.get('colormap', cv2.COLORMAP_JET)
        alpha = kwargs.get('alpha', 1)
        image = cv2.applyColorMap((image * alpha).astype(np.uint8), colormap)
        ret = True

    elif modification_type == 'canny':
        thresh1 = kwargs.get('threshold1', 100)
        thresh2 = kwargs.get('threshold2', 200)
        if kwargs.get('gray', True):
            ret, image = self.image_modifications(image, 'grayscale')
        image = cv2.Canny(image, threshold1=thresh1, threshold2=thresh2)
        ret = True

    elif modification_type == 'dilate':
        kernel_size = kwargs.get('kernel_size', (3, 3))
        kernel = np.ones(kernel_size, np.uint8)
        iterations = kwargs.get('iterations', 1)
        if kwargs.get('gray', True):
            ret, image = self.image_modifications(image, 'grayscale')
        image = cv2.dilate(image, kernel=kernel, iterations=iterations)
        ret = True

    elif modification_type == 'erode':
        kernel_size = kwargs.get('kernel_size', (5, 5))
        kernel = np.ones(kernel_size, np.uint8)
        iterations = kwargs.get('iterations', 1)
        if kwargs.get('gray', True):
            ret, image = self.image_modifications(image, 'grayscale')
        image = cv2.erode(image, kernel=kernel, iterations=iterations)
        ret = True

    elif modification_type == 'plane_correction':
        points = kwargs.get('points')
        if points is None or len(points) != 4:
            raise ImageOperationsException('Plane corner points [top_left, top_right, bottom_right, bottom_left] not found')
        top_left, top_right, bottom_right, bottom_left = points
        top_width = self.calculate_distance(top_left, top_right)
        bottom_width = self.calculate_distance(bottom_left, bottom_right)
        left_height = self.calculate_distance(top_left, bottom_left)
        right_height = self.calculate_distance(top_right, bottom_right)
        width = kwargs.get('width', int((top_width + bottom_width) / 2))
        height = kwargs.get('height', int((left_height + right_height) / 2))
        targets = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
        corners = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)
        transformation_matrix = cv2.getPerspectiveTransform(src=corners, dst=targets)
        image = cv2.warpPerspective(image, M=transformation_matrix, dsize=(width, height))
        ret = True

    elif modification_type == 'channel_first':
        image = np.transpose(image, (2, 0, 1))
        ret = True

    elif modification_type == 'channel_last':
        image = np.transpose(image, (1, 2, 0))
        ret = True

    elif modification_type == 'normalize':
        alpha = kwargs.get('alpha', 0)
        beta = kwargs.get('beta', 1)
        norm_type = kwargs.get('norm_type', cv2.NORM_MINMAX)
        dtype = kwargs.get('dtype', image.dtype)
        image = cv2.normalize(image, None, alpha=alpha, beta=beta, norm_type=norm_type, dtype=dtype)
        ret = True

    elif modification_type == 'stack':
        image2 = kwargs.get('secondary_image')
        axis = kwargs.get('axis', 0)
        if image2 is None:
            raise ImageOperationsException('Images not found')
        image = np.concatenate([image, image2], axis=axis, dtype=image.dtype)
        ret = True
    
    elif modification_type == 'make_3_channel':
        image = np.asarray([image, image, image], dtype=image.dtype)
        ret, image = self.modify_image(image, 'channel_last')
        ret = True

    else:
        ret = False
        image = None
        
    return ret, image
