import os
from PIL import Image
import numpy as np
import json


folder_dir = "data"

output_dir = "output"

image_files = [f for f in os.listdir(folder_dir) if f.endswith(".png")]


def get_image_colors(image_path):
    # Open the image
    img = Image.open(image_path)

    frame_name, altitude = parse_img_name(image_path)
    print(frame_name)
    # Convert to RGB (if not already)
    img = img.convert("RGB")
    # Convert image to numpy array
    img_array = np.array(img)

    print(img_array.shape)

    # Reshape array to a list of RGB tuples
    pixels = img_array.reshape(-1, 3)
    # Get unique colors
    unique_colors = np.unique(pixels, axis=0)
    avg_color = np.mean(unique_colors, axis=0)

    # map into int but a list
    avg_color = list(map(int, avg_color))

    frame_result = {
        "name": frame_name,
        "average_color": avg_color,
        "altitude": altitude,
    }
    # average
    # for y in range(img_array.shape[0]):
    #     for x in range(img_array.shape[1]):
    #         pixel_id = get_pixel_id(x, y)
    #         pixel_color = img_array[y][x]
    #         frame_result[pixel_id] = pixel_color.tolist()

    print(f"Average color: {avg_color}")

    return avg_color, frame_result


def parse_img_name(image_name):
    frame_name = image_name.split("/")[-1].split("_")[0]
    depth = image_name.split("/")[-1].split("_")[1]
    return frame_name, depth


def get_pixel_id(x, y):
    return f"{x}_{y}"


def parse_pixel_id(pixel_id):
    return tuple(map(int, pixel_id.split("_")))


def create_image_block(rgb_array, img_name):
    global output_dir
    width = 100
    height = 100
    color = (rgb_array[0], rgb_array[1], rgb_array[2])
    # make into int
    color = tuple(map(int, color))
    img = Image.new("RGB", (width, height), color)

    img.save(f"{output_dir}/{img_name}.png")


output = {}

initial_image = os.path.join(folder_dir, image_files[0])

initial_image = Image.open(initial_image)

initial_image_rgb = initial_image.convert("RGB")

initial_image_rgb = np.array(initial_image_rgb)

category = {}

for file in image_files:
    image_path = os.path.join(folder_dir, file)
    frame_name, altitude = parse_img_name(image_path)
    avg_color, frame_result = get_image_colors(image_path)

    if frame_result["altitude"] not in category:
        category[frame_result["altitude"]] = []
    category[frame_result["altitude"]].append(frame_result)

    # create_image_block(
    #     avg_color,
    #     frame_name
    #     + "_"
    #     + str(avg_color[0])
    #     + "_"
    #     + str(avg_color[1])
    #     + "_"
    #     + str(avg_color[2]),
    # )
    # break

# for each category get the average color
for alt in category:
    alt_category = category[alt]
    frequency = len(alt_category)
    alt_avg_color = np.mean([x["average_color"] for x in alt_category], axis=0)
    alt_avg_color = list(map(int, alt_avg_color))
    create_image_block(alt_avg_color, alt + "frequency" + "_" + str(frequency))
