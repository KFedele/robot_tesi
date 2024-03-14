import cv2
import numpy as np
import os

def highlight_imperfections(image_path, output_file):
    # Read the image
    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"Error: Unable to read image from {image_path}")
        return

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Use Canny edge detection to find edges in the image. Le threshold possono essere modificate per rendere il sistema più sensibile ad un certo tipo di imperfezione. 
    edges = cv2.Canny(blurred_image, 1, 50)

    # Find contours in the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty mask to highlight imperfections in red
    imperfections_mask = np.zeros_like(original_image)

    # Set a threshold for the imperfection area. Usando aree più ampie, le imperfezioni più piccole sono eliminate
    imperfection_area_threshold = 10

    # Initialize imperfection count
    imperfection_count = 0

    # Iterate through contours and highlight imperfections
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > imperfection_area_threshold:
            imperfection_count += 1
            cv2.drawContours(imperfections_mask, [contour], -1, (0, 0, 255), 2)

    # Superimpose the imperfections on the original image
    result_image = cv2.addWeighted(original_image, 1, imperfections_mask, 0.7, 0)

    # Display the result
    cv2.imshow("Original Image with Imperfections", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Write imperfection_count to the output file
    with open(output_file, 'a') as f:
        f.write(f"{os.path.basename(image_path)}: {imperfection_count}\n")

    return imperfection_count

if __name__ == "__main__":
    image_folder_path = 'C:/Users/katyl/Desktop/Codici_tesi/ConversioneDati/MachineLearning/uploads'
    
    # Specifica il percorso del file di output
    output_file_path = 'c1.txt'

    # Iterate through all images in the folder
    for filename in os.listdir(image_folder_path):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(image_folder_path, filename)
            imperfection_count = highlight_imperfections(image_path, output_file_path)
            print(f"{os.path.basename(image_path)} - Imperfection Level: {imperfection_count}")

    print("Imperfection counts written to", output_file_path)
