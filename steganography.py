from PIL import Image
import os

def embed_data(image_path, data):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    data += "#####"  # End marker
    binary_data = ''.join(format(ord(char), '08b') for char in data)
    print(f"Embedding data length: {len(binary_data)} bits")
    print(f"Binary data (first 40): {binary_data[:40]}")
    print(f"Binary data (last 40): {binary_data[-40:]}")

    if len(binary_data) > width * height:
        raise ValueError(f"Data too large ({len(binary_data)} bits) for image ({width * height} pixels)")

    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index < len(binary_data):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_data[data_index])
                pixels[x, y] = (r, g, b)
                data_index += 1
        if data_index >= len(binary_data):
            break  # Exit outer loop once all bits are embedded

    if data_index < len(binary_data):
        raise ValueError(f"Failed to embed all data: only {data_index} of {len(binary_data)} bits embedded")

    stego_image_path = os.path.join("uploads", f"stego_{os.path.basename(image_path)}")
    print(f"Saving stego image to: {stego_image_path}")
    img.save(stego_image_path, 'PNG', compress_level=0)
    if not os.path.exists(stego_image_path):
        raise ValueError(f"Failed to save stego image: {stego_image_path}")

    # Verify embedding
    verify_img = Image.open(stego_image_path).convert('RGB')
    verify_pixels = verify_img.load()
    verify_bits = ""
    total_pixels_to_check = min(width * height, len(binary_data))
    for i in range(total_pixels_to_check):
        x, y = i % width, i // width
        r, _, _ = verify_pixels[x, y]
        verify_bits += str(r & 1)
    print(f"Verified all embedded bits (first 40): {verify_bits[:40]}")
    print(f"Verified all embedded bits (last 40): {verify_bits[-40:]}")
    if verify_bits != binary_data:
        raise ValueError("Verification failed: Embedded data does not match")
    return stego_image_path

def extract_data(stego_image_path):
    print(f"Attempting to load: {stego_image_path}")
    if not os.path.exists(stego_image_path):
        raise FileNotFoundError(f"File not found: {stego_image_path}")

    print(f"File exists: {os.path.exists(stego_image_path)}")
    img = Image.open(stego_image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    binary_data = ""
    end_marker = '01000100' * 5  # "#####" in binary (ASCII 35)
    print(f"Image size: {width}x{height} pixels")
    print(f"End marker: {end_marker}")

    for y in range(height):
        for x in range(width):
            r, _, _ = pixels[x, y]
            binary_data += str(r & 1)
            if len(binary_data) >= len(end_marker) and binary_data[-len(end_marker):] == end_marker:
                message_binary = binary_data[:-len(end_marker)]
                print(f"End marker found at {len(binary_data)} bits")
                print(f"Message binary (first 40): {message_binary[:40]}")
                if len(message_binary) % 8 != 0:
                    raise ValueError("Extracted data length is not a multiple of 8")
                byte_data = [message_binary[k:k+8] for k in range(0, len(message_binary), 8)]
                extracted_message = "".join(chr(int(byte, 2)) for byte in byte_data)
                print(f"Extracted message: {extracted_message}")
                return extracted_message
            if len(binary_data) <= 2000 and len(binary_data) % 40 == 0:
                print(f"Extracted {len(binary_data)} bits: {binary_data[-40:]}")

    print(f"Total bits extracted: {len(binary_data)}")
    print(f"Last 40 bits: {binary_data[-40:]}")
    raise ValueError("No end marker found in extracted data")