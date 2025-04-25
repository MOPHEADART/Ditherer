from PIL import Image
import os
import numpy

def apply_bayer_dithering(image: Image.Image, scale_factor: int=2, matrix_size: int=2, color: bool=False) -> Image.Image:

    # grayscale convert
    if not color:
        image = image.convert("L")

    # downscale image
    width, height = image.size
    image = image.resize((width // scale_factor, height // scale_factor), resample=Image.BILINEAR)

    # Normalize values between 0-1
    data = numpy.array(image).astype(numpy.float32) / 255.
    normalized_height, normalized_width = data.shape[:2]

    # Bayer 2x2 Matrix
    bayer_matrix_2x2 = numpy.array([[0.0, 0.5],
                                    [0.75, 0.25]])
    
    # Bayer 4x4 Matrix
    bayer_matrix_4x4 = numpy.array([[0.0, 0.53125, 0.15625, 0.65625],
                                    [0.78125, 0.28125, 0.90625, 0.40625],
                                    [0.21875, 0.71875, 0.09375, 0.59375],
                                    [0.96875, 0.46875, 0.84375, 0.34375]])
    
    # Bayer 8x8 Matrix
    bayer_matrix_8x8 = numpy.array([[0.00000, 0.75000, 0.18750, 0.93750, 0.04688, 0.79688, 0.23438, 0.98438],
                                    [0.50000, 0.25000, 0.68750, 0.43750, 0.54688, 0.29688, 0.73438, 0.48438],
                                    [0.12500, 0.87500, 0.06250, 0.81250, 0.17188, 0.92188, 0.10938, 0.85938],
                                    [0.62500, 0.37500, 0.56250, 0.31250, 0.67188, 0.42188, 0.60938, 0.35938],
                                    [0.03125, 0.78125, 0.21875, 0.96875, 0.01562, 0.76562, 0.20312, 0.95312],
                                    [0.53125, 0.28125, 0.71875, 0.46875, 0.51562, 0.26562, 0.70312, 0.45312],
                                    [0.15625, 0.90625, 0.09375, 0.84375, 0.14062, 0.89062, 0.07812, 0.82812],
                                    [0.65625, 0.40625, 0.59375, 0.34375, 0.64062, 0.39062, 0.57812, 0.32812]])
    
    # Selection of Matrix size
    if matrix_size == 2:
        bayer_matrix = bayer_matrix_2x2

    elif matrix_size == 4:
        bayer_matrix = bayer_matrix_4x4

    elif matrix_size == 8:
        bayer_matrix = bayer_matrix_8x8
    
    else:
        return

    # Array for dithering
    if color:
        dithered = numpy.zeros((normalized_height, normalized_width, 3), dtype=numpy.uint8)
    else:
        dithered = numpy.zeros((normalized_height, normalized_width), dtype=numpy.uint8)

    # Apply Dithering
    for y in range(normalized_height):
        for x in range(normalized_width):
            threshold = bayer_matrix[y % matrix_size, x % matrix_size]
            if color:
                for c in range(3):
                    value = data[y, x, c]
                    dithered[y, x, c] = 255 if value>=threshold else 0
            else:
                value = data[y, x]
                dithered[y, x] = 255 if value >= threshold else 0

    # Convert data back to image
    if color:
        image_dithered = Image.fromarray(dithered, mode="RGB")
    else:
        image_dithered = Image.fromarray(dithered, mode="L")

    return image_dithered