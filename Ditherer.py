from PIL import Image
import os
import numpy

def apply_bayer_dithering(image: Image.Image, scale_factor: int=2) -> Image.Image:

    # grayscale convert
    image_grayscale = image.convert("L")

    # downscale image
    width, height = image_grayscale.size
    image_downscaled = image_grayscale.resize((width // scale_factor, height // scale_factor), resample=Image.BILINEAR)

    # Normalize values between 0-1
    data = numpy.array(image_downscaled).astype(numpy.float32) / 255.
    normalized_height, normalized_width = data.shape

    # Bayer 2x2 Matrix
    bayer_matrix = numpy.array([[0.0, 0.5],
                            [0.75, 0.25]])

    # Array for dithering
    dithered = numpy.zeros((normalized_height, normalized_width), dtype=numpy.uint8)

    # Apply Dithering
    for y in range(normalized_height):
        for x in range(normalized_width):
            threshold = bayer_matrix[y % 2, x % 2]
            value = data[y, x]
            dithered[y, x] = 255 if value >= threshold else 0

    # Convert data back to image
    image_dithered = Image.fromarray(dithered, mode="L")

    # Upscale to original size
    image_upscaled = image_dithered.resize((width, height), resample=Image.NEAREST)

    return image_upscaled
