import numpy as np

def apply_chaotic_map(image):
    h, w, _ = image.shape
    indices = np.arange(h * w)
    np.random.seed(42)  # Use a fixed seed for reproducibility
    np.random.shuffle(indices)
    return np.reshape(image, (-1, 3))[indices].reshape(image.shape)

def reverse_chaotic_map(image):
    h, w, _ = image.shape
    indices = np.arange(h * w)
    np.random.seed(42)  # Use the same seed for reversibility
    np.random.shuffle(indices)
    reverse_indices = np.argsort(indices)
    return np.reshape(image, (-1, 3))[reverse_indices].reshape(image.shape)