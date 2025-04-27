from PIL import Image
import numpy as np

def apply_bayer_dithering(image: Image.Image, scale_factor: int=2, matrix_size: int=2, color: bool = False, steps: int = None) -> Image.Image:

    # downscale image
    width, height = image.size
    new_width = width // scale_factor
    new_height = height // scale_factor
    image = image.resize((new_width, new_height), resample=Image.BILINEAR)

    # Normalize values between 0-1
    data = np.array(image, dtype=np.float32) / 255.0

    # Bayer matrices normalized
    bayer_matrices = {
        2: np.array([[0, 2],
                    [3, 1]]) / 4,
        4: np.array([[0, 8, 2, 10],
                    [12, 4, 14, 6],
                    [3, 11, 1, 9],
                    [15, 7, 13, 5]]) / 16,
        8: np.array([[0, 48, 12, 60, 3, 51, 15, 63],
                    [32, 16, 44, 28, 35, 19, 47, 31],
                    [8, 56, 4, 52, 11, 59, 7, 55],
                    [40, 24, 36, 20, 43, 27, 39, 23],
                    [2, 50, 14, 62, 1, 49, 13, 61],
                    [34, 18, 46, 30, 33, 17, 45, 29],
                    [10, 58, 6, 54, 9, 57, 5, 53],
                    [42, 26, 38, 22, 41, 25, 37, 21]]) / 64
    }

    # selected Bayer matrix
    bayer_matrix = bayer_matrices.get(matrix_size, bayer_matrices[2])
    matrix_height, matrix_width = bayer_matrix.shape

    if color:
        bayer_matrix = np.stack([bayer_matrix] * 3, axis=-1)

    # Array for dithering
    if color:
        if len(data.shape) == 2:
            data = np.stack([data]*3, axis=-1)

        threshold = np.tile(bayer_matrix,
                                (new_height // matrix_height + 1,
                                 new_width // matrix_width + 1, 1))
        threshold = threshold[:new_height, :new_width, :]
    else:
        if len(data.shape) == 3:
            data = np.mean(data, axis=-1)

        threshold = np.tile(bayer_matrix,
                                (new_height // matrix_height + 1,
                                 new_width // matrix_width + 1))
            
        threshold = threshold[ :new_height, :new_width]

    # Apply bayer threshold
    data = data * (steps - 1)
    data = data + threshold
    data = np.floor(data)
    data = data / (steps - 1)
    data = np.clip(data, 0.0, 1.0)

    # Scale normalized values back to 0-255
    dithered = (data * 255).astype(np.uint8)

    # Convert data back to PIL image
    mode = "RGB" if color else "L"
    return Image.fromarray(dithered, mode=mode)