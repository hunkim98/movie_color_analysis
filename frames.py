import os
from PIL import Image
from collections import Counter


def detect_black_bars(img, brightness_threshold=10, coverage_threshold=0.98):
    """
    Detect how many rows from the top and bottom are effectively "black bars".
    We do this by checking each row's average brightness; if it's below
    brightness_threshold for almost all pixels, we consider it a black row.

    :param img: PIL Image in RGB (or converted to RGB).
    :param brightness_threshold: Max average brightness for a pixel to be considered black.
    :param coverage_threshold: Fraction of pixels in a row that must be below threshold to
                               treat that entire row as black.
    :return: (top_crop, bottom_crop) in pixels
    """
    width, height = img.size
    pixels = img.load()

    def row_is_black(row_index):
        """Check if a row is 'black' under the given threshold rules."""
        black_count = 0
        for x in range(width):
            r, g, b = pixels[x, row_index]
            # Simple luminosity estimate
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < brightness_threshold:
                black_count += 1
        # If enough pixels are under the threshold, mark the entire row black
        return (black_count / width) >= coverage_threshold

    # Detect top black rows
    top_crop = 0
    for row in range(height):
        if row_is_black(row):
            top_crop += 1
        else:
            break

    # Detect bottom black rows
    bottom_crop = 0
    for row in range(height - 1, -1, -1):
        if row_is_black(row):
            bottom_crop += 1
        else:
            break

    return (top_crop, bottom_crop)


def get_average_color(img):
    """
    Return the (R, G, B) average color of an image.
    """
    # Convert to RGB just in case
    img = img.convert("RGB")
    pixels = img.getdata()
    r_total, g_total, b_total = 0, 0, 0
    count = 0

    for r, g, b in pixels:
        r_total += r
        g_total += g
        b_total += b
        count += 1

    return (r_total // count, g_total // count, b_total // count)


def get_dominant_color(img, resize=150):
    """
    Return the dominant color (R, G, B) of the image by counting most frequent pixel.
    For performance, we resize the image to at most 'resize' in width or height.
    """
    img = img.convert("RGB")
    # Optionally resize to speed up the process for large images
    w, h = img.size
    if max(w, h) > resize:
        ratio = resize / max(w, h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h))

    # Count each pixel’s frequency
    pixels = list(img.getdata())
    most_common = Counter(pixels).most_common(1)
    return most_common[0][0]  # (R, G, B) of the most frequent pixel


def create_color_block(color, size=(100, 100)):
    """
    Create a PIL Image filled with the given RGB color.
    """
    block = Image.new("RGB", size, color)
    return block


def create_color_palette(img, grid_size=(4, 4), block_size=(50, 50)):
    """
    Create a 4x4 color palette image, where each cell is the average color
    of that region in the original image.

    :param img: Cropped PIL Image.
    :param grid_size: (rows, cols) - default is 4x4.
    :param block_size: (width, height) of each cell in the output palette image.
    :return: A new PIL Image object with the palette.
    """
    rows, cols = grid_size
    block_w, block_h = block_size
    width, height = img.size

    # Dimensions in the original for each subregion
    sub_w = width // cols
    sub_h = height // rows

    palette_img = Image.new("RGB", (block_w * cols, block_h * rows))

    # Convert once, so we can read pixel data
    img_rgb = img.convert("RGB")

    for row in range(rows):
        for col in range(cols):
            # Calculate the sub-box in the original image
            left = col * sub_w
            top = row * sub_h
            right = left + sub_w
            bottom = top + sub_h

            # Crop that region
            region = img_rgb.crop((left, top, right, bottom))
            # Average color
            avg_color = get_average_color(region)

            # Create a small block
            block = create_color_block(avg_color, size=block_size)

            # Paste it in the palette
            palette_img.paste(block, (col * block_w, row * block_h))

    return palette_img


def create_light_map(img, grid_size=(4, 4), block_size=(50, 50)):
    """
    Create a 4x4 lightness map image, where each cell’s brightness
    is the average brightness of that region in the original image.
    We fill each cell with a grayscale value corresponding to that brightness.

    :param img: Cropped PIL Image.
    :param grid_size: (rows, cols) - default is 4x4.
    :param block_size: (width, height) of each cell in the output.
    :return: A new PIL Image object with the lightness map.
    """
    rows, cols = grid_size
    block_w, block_h = block_size
    width, height = img.size

    sub_w = width // cols
    sub_h = height // rows

    lightmap = Image.new("RGB", (block_w * cols, block_h * rows))

    img_rgb = img.convert("RGB")

    for row in range(rows):
        for col in range(cols):
            left = col * sub_w
            top = row * sub_h
            right = left + sub_w
            bottom = top + sub_h

            region = img_rgb.crop((left, top, right, bottom))

            # Compute average brightness (grayscale)
            # E.g., lum = 0.299*r + 0.587*g + 0.114*b
            # We'll do a quick average on the entire region
            pixels = region.getdata()
            lum_total = 0
            count = 0
            for r, g, b in pixels:
                lum_total += 0.299 * r + 0.587 * g + 0.114 * b
                count += 1
            avg_lum = int(lum_total / count)

            # Create a grayscale color block
            gray_block = create_color_block(
                (avg_lum, avg_lum, avg_lum), size=block_size
            )
            lightmap.paste(gray_block, (col * block_w, row * block_h))

    return lightmap


def process_frames(directory):
    """
    1. Find all images in 'directory'.
    2. Pick the middle image to detect black bars and compute top/bottom crop.
    3. For each image:
       - Crop out black bars
       - Compute and save "dominant_" block
       - Compute and save "average_" block
       - Compute and save "palette_" image (4x4 color map)
       - Compute and save "lightmap_" image (4x4 grayscale map)
    """
    # Gather images
    all_files = [
        f
        for f in os.listdir(directory)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if not all_files:
        print("No images found in directory:", directory)
        return

    all_files.sort()  # sort by name
    # Pick the middle file
    mid_index = len(all_files) // 2
    sample_path = os.path.join(directory, all_files[mid_index])

    # Detect black bars using the sample image
    sample_img = Image.open(sample_path).convert("RGB")
    top_crop, bottom_crop = detect_black_bars(sample_img)

    print(
        f"Detected top_crop={top_crop}, bottom_crop={bottom_crop} using sample image: {all_files[mid_index]}"
    )

    for filename in all_files:
        img_path = os.path.join(directory, filename)
        img = Image.open(img_path).convert("RGB")
        w, h = img.size

        # Crop the image to remove black bars
        # left, upper, right, lower
        # print(w, h - bottom_crop)
        cropped_img = img.crop((0, top_crop, w, h - bottom_crop))
        base_name, ext = os.path.splitext(filename)

        # --- 1) Dominant color ---
        dominant_color = get_dominant_color(cropped_img)
        dominant_block = create_color_block(dominant_color, size=(100, 100))
        dominant_block.save(os.path.join(directory, f"dominant_{base_name}.jpg"))

        # --- 2) Average color ---
        avg_color = get_average_color(cropped_img)
        avg_block = create_color_block(avg_color, size=(100, 100))
        avg_block.save(os.path.join(directory, f"average_{base_name}.jpg"))

        # --- 3) 4x4 color palette ---
        palette = create_color_palette(
            cropped_img, grid_size=(4, 4), block_size=(50, 50)
        )
        palette.save(os.path.join(directory, f"palette_{base_name}.jpg"))

        # --- 4) 4x4 light map ---
        light_map = create_light_map(cropped_img, grid_size=(4, 4), block_size=(50, 50))
        light_map.save(os.path.join(directory, f"lightmap_{base_name}.jpg"))

        print(f"Processed {filename}")


if __name__ == "__main__":
    video_name = "vanessa_trick"
    all_dirs = os.listdir(f"output/videos/{video_name}/frames")
    for dir in all_dirs:
        print(dir)
        frames_dir = f"output/videos/{video_name}/frames/{dir}"
        process_frames(frames_dir)
