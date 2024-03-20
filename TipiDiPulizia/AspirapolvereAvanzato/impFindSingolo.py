import cv2
import os
import numpy as np

def count_imperfections(image_path: str) -> int:
    # Read the image
    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"Error: Unable to read image from {image_path}")
        return -1

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Use Canny edge detection to find edges in the image
    edges = cv2.Canny(blurred_image, 1, 50)

    # Find contours in the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Set a threshold for the imperfection area
    imperfection_area_threshold = 2

    # Initialize imperfection count
    imperfection_count = 0

    # Create an empty mask to highlight imperfections in red
    imperfections_mask = np.zeros_like(original_image)

    # Iterate through contours and count imperfections
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > imperfection_area_threshold:
            imperfection_count += 1
            cv2.drawContours(imperfections_mask, [contour], -1, (0, 0, 255), 2)

    # Superimpose the imperfections on the original image
    result_image = cv2.addWeighted(original_image, 1, imperfections_mask, 0.7, 0)

    # Split the image path into directory and filename
    image_dir, image_name = os.path.split(image_path)

    # Create a new directory path for the analyzed images
    analyzed_dir = os.path.join(image_dir, "analyzed")

    # Check if the analyzed directory exists, if not, create it
    if not os.path.exists(analyzed_dir):
        os.makedirs(analyzed_dir)

    # Construct the output image path with "_analyzed" added to the filename
    analyzed_image_name = os.path.splitext(image_name)[0] + "_analyzed.jpg"
    analyzed_image_path = os.path.join(analyzed_dir, analyzed_image_name)

    # Save the result image
    cv2.imwrite(analyzed_image_path, result_image)

    return imperfection_count, analyzed_image_path
