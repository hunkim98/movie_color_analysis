import os
from PIL import Image
import numpy as np
import shutil


def get_light_direction_3x3(image_path):
    """
    1) Load an image in grayscale;
    2) Resize to 3x3;
    3) Check if center pixel is brighter than all others => 'center';
    4) Else pick whether 'top', 'bottom', 'left', 'right' is brightest;
    5) If tie or cannot decide => None.
    """
    try:
        # 1. Open image in grayscale
        img = Image.open(image_path).convert("L")
    except Exception:
        return None  # Could not open or convert the image

    # 2. Resize to 3x3 (downsample)
    #    For Pillow >= 9, use Image.Resampling.BOX or .BICUBIC, etc.
    #    If your Pillow is older, you might see Image.BOX / Image.ANTIALIAS instead.
    img_3x3 = img.resize((3, 3), Image.Resampling.BOX)

    # Convert to numpy for easy array manipulation
    arr = np.array(img_3x3, dtype=np.float32)  # shape = (3,3)

    # Check total brightness
    total_lum = np.sum(arr)
    if total_lum == 0:
        # Completely black => cannot classify
        return None

    # 3. Check if the center pixel is strictly brighter than all others
    center_val = arr[1, 1]
    # Flatten the entire 3x3 to compare
    all_pixels = arr.flatten()
    # Indices of all pixels except the center
    others = np.concatenate((all_pixels[:4], all_pixels[5:]))

    if np.all(center_val > others):
        # Center is the single brightest pixel
        return "center"

    # 4. Otherwise, sum top/bottom row and left/right column
    top_sum = np.sum(arr[0, :])  # row 0
    bottom_sum = np.sum(arr[2, :])  # row 2
    left_sum = np.sum(arr[:, 0])  # col 0
    right_sum = np.sum(arr[:, 2])  # col 2

    # 5. Find the largest among {top, bottom, left, right}
    values = [
        ("top", top_sum),
        ("bottom", bottom_sum),
        ("left", left_sum),
        ("right", right_sum),
    ]

    # Sort by brightness descending
    values.sort(key=lambda x: x[1], reverse=True)

    # The best direction is the one with the highest sum
    best_direction, best_value = values[0]

    # 6. Check for tie: if the second-best has the same value, we call it None
    if len(values) > 1 and values[1][1] == best_value:
        return None  # tie for first place

    # 7. Return that direction
    return best_direction


# ---------------- Sample Usage ----------------

if __name__ == "__main__":
    movie_name = "vanessa_trick"
    main_dir = f"./output/videos/{movie_name}/frames"

    folders = os.listdir(main_dir)

    for folder in folders:
        folder_path = os.path.join(main_dir, folder)
        # check if it is a directory
        if not os.path.isdir(folder_path):
            continue
        for fname in os.listdir(folder_path):
            direction = None
            chunk_num = folder_path.split("_")[-1]
            if fname.lower().endswith(".jpg") and fname.startswith("lightmap_"):
                frame_num = fname.split("_")[-1].split(".")[0]
                path = os.path.join(folder_path, fname)
                direction = get_light_direction_3x3(path)
                # print(f"{fname} => {direction}")

            if direction is not None:
                palette_file_name = f"palette_{frame_num}.jpg"
                new_dir = os.path.join(main_dir, direction)
                os.makedirs(new_dir, exist_ok=True)
                # print(new_dir)
                # copy the image to the new directory
                # print(new_path)
                original_path = os.path.join(folder_path, palette_file_name)
                new_path = os.path.join(new_dir, f"chunk_{chunk_num}_{frame_num}.jpg")
                shutil.copy2(original_path, new_path)
            else:
                pass
                # print(f"Could not classify {fname}")
