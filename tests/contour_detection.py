import cv2
import numpy as np


def detect_black_squares(image_path, output_path=None):
    """
    Detect black squares in an image using OpenCV

    Args:
        image_path: Path to input image
        output_path: Optional path to save result image

    Returns:
        List of detected square contours
    """

    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")

    original = img.copy()

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply threshold to get binary image (black regions become white)
    # Using THRESH_BINARY_INV so black becomes white (foreground)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Optional: Apply morphological operations to clean up noise
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    squares = []

    for contour in contours:
        # Filter by area (adjust min_area based on your needs)
        area = cv2.contourArea(contour)
        if area < 100:  # Skip very small contours
            continue

        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if it's a quadrilateral (4 vertices)
        if len(approx) == 4:
            # Check if it's roughly square-shaped
            # Calculate bounding rectangle
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h

            # Check if aspect ratio is close to 1 (square)
            if 0.8 <= aspect_ratio <= 1.2:  # Allow some tolerance
                # Additional check: compare contour area to bounding box area
                rect_area = w * h
                extent = float(area) / rect_area

                # If extent is high, it's likely a filled square
                if extent > 0.7:
                    squares.append(approx)

                    # Draw the detected square
                    cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)

                    # Optional: Draw bounding rectangle
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)

                    # Add text label
                    cv2.putText(img, f'Square {len(squares)}', (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    print(f"Found {len(squares)} black squares")

    # Save or display result
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"Result saved to {output_path}")

    # Display images (comment out if running headless)
    cv2.imshow('Original', original)
    cv2.imshow('Threshold', thresh)
    cv2.imshow('Detected Squares', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return squares

def detect_black_squares_advanced(image_path, output_path=None):
    """
    Advanced version with more robust detection parameters
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")

    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding for better results with varying lighting
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    squares = []

    for contour in contours:
        area = cv2.contourArea(contour)

        # Filter by area
        if area < 500:  # Minimum area threshold
            continue

        # Get convex hull to handle slightly irregular shapes
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        # Check if contour is convex enough
        if area / hull_area < 0.8:
            continue

        # Approximate to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check for quadrilateral
        if len(approx) == 4:
            # Calculate side lengths to verify it's square-like
            sides = []
            for i in range(4):
                p1 = approx[i][0]
                p2 = approx[(i + 1) % 4][0]
                side_length = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                sides.append(side_length)

            # Check if all sides are roughly equal
            side_ratio = max(sides) / min(sides) if min(sides) > 0 else float('inf')

            if side_ratio <= 1.3:  # Allow some tolerance for side length variation
                squares.append(approx)
                cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)

    print(f"Advanced detection found {len(squares)} black squares")

    if output_path:
        cv2.imwrite(output_path, img)

    return squares


if __name__ == "__main__":
    # Replace with your image path
    image_path = r"C:\Users\atcos\Documents\Pycharm Projects\eagle-eye\tests\misc_files\40013-40014 [misalign].png"

    try:
        # Basic detection
        squares = detect_black_squares(image_path, "result_basic.jpg")

        # Advanced detection
        # squares_advanced = detect_black_squares_advanced(image_path, "result_advanced.jpg")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to replace 'your_image.jpg' with the actual path to your image")
