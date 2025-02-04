"""
This module contains utility functions for vision_utils package.

Examples of what belong in this module:
    - Functions that are used by multiple classes in the package
    - Functions that don't fit into any of the other modules in the package
    - Functions that are used by the package but are not part of the package's core functionality
    - Small extra functionality that is not part of the package's core functionality
"""

import cv2
import math
import numpy as np
import pyrealsense2 as rs
from typing import List, Tuple, Union

# TODO: Review these functions and remove hardcoding
def get_center_of_mask(mask: np.ndarray) -> Tuple[int, int]:
    """
    Get the center of the mask.

    Args:
        mask (np.ndarray): The mask.

    Returns:
        Tuple[int, int]: The center of the mask.
    """
    try:
        M = cv2.moments(mask)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return cX, cY
    except ZeroDivisionError:
        print("Division by zero while calculating moments.")
    except Exception as e:
        print("Error while getting center of mask:", e)

def get_center_of_bbox(bbox: Union[List[int], Tuple[int, int, int, int]]) -> Tuple[int, int]:
    """
    Get the center of the bounding box.

    Args:
        bbox (Union[List[int], Tuple[int, int, int, int]]): The bounding box.

    Returns:
        Tuple[int, int]: The center of the bounding box.
    """
    try:
        x, y, w, h = bbox
        cX = x + w // 2
        cY = y + h // 2
        return cX, cY
    except ValueError:
        print("Bounding box must contain exactly four elements.")
    except Exception as e:
        print("Error while getting center of bbox:", e)

def get_center(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    """
    Get the center of the line.

    Args:
        x1 (int): The x-coordinate of the first point.
        y1 (int): The y-coordinate of the first point.
        x2 (int): The x-coordinate of the second point.
        y2 (int): The y-coordinate of the second point.

    Returns:
        Tuple[int, int]: The center of the line.
    """
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    return center_x, center_y

def find_edge_points(image: np.ndarray, start_point: Tuple[int, int], end_point: Tuple[int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Find the leftmost and rightmost points along the line.

    Args:
        image (np.ndarray): The image.
        start_point (Tuple[int, int]): The start point of the line.
        end_point (Tuple[int, int]): The end point of the line.

    Returns:
        Tuple[Tuple[int, int], Tuple[int, int]]: The leftmost and rightmost points along the line.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # Create a mask with zeros
    mask = np.zeros_like(edged)

    # Draw the line on the mask
    cv2.line(mask, start_point, end_point, 255, 1)

    # Bitwise AND the mask with the Canny edges
    line_edges = cv2.bitwise_and(edged, edged, mask=mask)

    # Find indices of non-zero values in the line_edges
    nonzero_indices = np.nonzero(line_edges)

    if len(nonzero_indices[0]) > 0:
        # Find the leftmost and rightmost points along the line
        leftmost_index = np.argmin(nonzero_indices[1])
        rightmost_index = np.argmax(nonzero_indices[1])

        leftmost_point = (nonzero_indices[1][leftmost_index], nonzero_indices[0][leftmost_index])
        rightmost_point = (nonzero_indices[1][rightmost_index], nonzero_indices[0][rightmost_index])

        return leftmost_point, rightmost_point

    return (0, 0), (0, 0)


def get_theta(x1: int, y1: int, x2: int, y2: int) -> float:
    """
    Get the angle of the line.

    Args:
        x1 (int): The x-coordinate of the first point.
        y1 (int): The y-coordinate of the first point.
        x2 (int): The x-coordinate of the second point.
        y2 (int): The y-coordinate of the second point.
    
    Returns:
        float: The angle of the line.
    """
    delta_y = y2 - y1
    delta_x = x2 - x1
    theta = math.atan2(delta_y, delta_x)
    return theta

def get_top_bottom_left_right(image: np.ndarray) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """
    Get the topmost, bottommost, leftmost, and rightmost points of the object.

    Args:
        image (np.ndarray): The image.

    Returns:
        Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]: The topmost, bottommost, leftmost, and rightmost points of the object.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        object_contour = max(contours, key=cv2.contourArea)

        # Get top, bottom, left, and right points
        top_most = tuple(object_contour[object_contour[:, :, 1].argmin()][0])
        bottom_most = tuple(object_contour[object_contour[:, :, 1].argmax()][0])
        left_most = tuple(object_contour[object_contour[:, :, 0].argmin()][0])
        right_most = tuple(object_contour[object_contour[:, :, 0].argmax()][0])

        return top_most, bottom_most, left_most, right_most

    return (0, 0), (0, 0), (0, 0), (0, 0)


def get_contours(image):
    """
    Get the contours in the image.

    Args:
        image (np.ndarray): The image.

    Returns:
        List[np.ndarray]: The contours in the image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 0

    filtered_contours = [contour for contour in contours if cv2.contourArea(contour) >= min_area]

    return filtered_contours

def get_height(color_image: np.ndarray, depth_frame: rs.depth_frame) -> float:
    """
    Get the height of the object in the image.

    Args:
        color_image (np.ndarray): The color image.
        depth_frame (rs.depth_frame): The depth frame.

    Returns:
        float: The height of the object in the image.
    """
    # Get the topmost, bottommost, leftmost, and rightmost points of the object
    topg, bottomg, leftg, rightg = get_top_bottom_left_right(color_image)

    # Get the centers of the top-bottom and left-right lines
    centerg1 = get_center(topg[0], topg[1], leftg[0], leftg[1])
    centerg2 = get_center(bottomg[0], bottomg[1], rightg[0], rightg[1])

    # Get the centers of the top-right and bottom-left lines
    centerf1 = get_center(topg[0], topg[1], rightg[0], rightg[1])
    centerf2 = get_center(bottomg[0], bottomg[1], leftg[0], leftg[1])

    # Calculate the lengths of the top-bottom and left-right lines
    length1 = math.sqrt((centerg2[0] - centerg1[0])**2 + (centerg2[1] - centerg1[1])**2)
    length2 = math.sqrt((centerf2[0] - centerf1[0])**2 + (centerf2[1] - centerf1[1])**2)

    # Get the center of the object
    if length1 > length2:
        center = get_center(centerg1[0], centerg1[1], centerg2[0], centerg2[1])
    else:
        center = get_center(centerf1[0], centerf1[1], centerf2[0], centerf2[1])

    # Get the start and end points of the line
    start_point = (center[0] + 200, center[1])
    end_point = (center[0] - 200, center[1])

    # Find the leftmost and rightmost points along the line
    leftmost, rightmost = find_edge_points(color_image, start_point, end_point)
    center_depth = depth_frame.get_distance(center[0], center[1])

    # Calculate the height of the object
    if leftmost != (0, 0) and rightmost != (0, 0):
        new_left = (leftmost[0] - 20, leftmost[1])
        new_right = (rightmost[0] + 10, rightmost[1])

        left_depth = depth_frame.get_distance(new_left[0], new_left[1])
        right_depth = depth_frame.get_distance(new_right[0], new_right[1])

        left_height = left_depth - center_depth
        right_height = right_depth - center_depth

        if left_depth == 0:  # If black spot detected on left side
            return right_height
        elif right_depth == 0:  # If black spot detected on right side
            return left_height
        elif left_depth != 0 and right_depth != 0:  # If no black spots detected
            return (right_height + left_height) / 2

    return 0.0  # Return 0.0 if height cannot be calculated

def get_width(color_image: np.ndarray, depth_frame: rs.depth_frame) -> float:
    """
    Get the width of the object in the image.

    Args:
        color_image (np.ndarray): The color image.
        depth_frame (rs.depth_frame): The depth frame.

    Returns:
        float: The width of the object in the image.
    """
    # Get the topmost, bottommost, leftmost, and rightmost points of the object
    topg, bottomg, leftg, rightg = get_top_bottom_left_right(color_image)

    # Get the centers of the top-bottom and left-right lines
    centerg1 = get_center(topg[0], topg[1], leftg[0], leftg[1])
    centerg2 = get_center(bottomg[0], bottomg[1], rightg[0], rightg[1])

    # Get the centers of the top-right and bottom-left lines
    centerf1 = get_center(topg[0], topg[1], rightg[0], rightg[1])
    centerf2 = get_center(bottomg[0], bottomg[1], leftg[0], leftg[1])

    # Calculate the lengths of the top-bottom and left-right lines
    length1 = math.sqrt((centerg2[0] - centerg1[0])**2 + (centerg2[1] - centerg1[1])**2)
    length2 = math.sqrt((centerf2[0] - centerf1[0])**2 + (centerf2[1] - centerf1[1])**2)

    # Get the center of the object
    if length1 > length2:
        center = get_center(centerg1[0], centerg1[1], centerg2[0], centerg2[1])
    else:
        center = get_center(centerf1[0], centerf1[1], centerf2[0], centerf2[1])

    # Get the start and end points of the line
    start_point = (center[0] + 200, center[1])
    end_point = (center[0] - 200, center[1])

    # Find the leftmost and rightmost points along the line
    leftmost, rightmost = find_edge_points(color_image, start_point, end_point)
    center_depth = depth_frame.get_distance(center[0], center[1])

    # Calculate the width of the object
    p = rightmost[0] - leftmost[0]
    d = center_depth

    # This is a linear regression model for width calculation
    width_calc = 0.457874804833073 * p + 34.787430566919376 * d - 6.180874999478928
    return width_calc
