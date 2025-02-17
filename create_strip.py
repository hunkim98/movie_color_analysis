import os
from PIL import Image
import math


def create_image_strip():
    movies = [
        "under_the_sea",
        "prince",
        "part_of_your_world",
        "poor_unfortunate_souls",
        "vanessa_trick",
        "kiss_the_girl",
        "for_the_first_time",
        # "the_scuttlebutt",
        "llm",
    ]

    width_cnt = 30  # each palette image will have 4 x 4 = 16 blocks
    height_cnt = 0

    movies_frames_cnt = {}

    for mov in movies:
        movies_frames_cnt[mov] = 0
        main_dir = f"./output/videos/{mov}/frames"
        folders = os.listdir(main_dir)

        movie_total_frames = 0
        for folder in folders:
            folder_path = os.path.join(main_dir, folder)

            # check if it is a directory
            if not os.path.isdir(folder_path):
                continue

            for fname in os.listdir(folder_path):
                chunk_num = folder_path.split("_")[-1]
                if fname.lower().endswith(".jpg") and fname.startswith("palette_"):
                    frame_num = fname.split("_")[-1].split(".")[0]
                    path = os.path.join(folder_path, fname)
                    movie_total_frames += 1

            # now we should // width_cnt to get the number of rows
        rows = math.floor(movie_total_frames / width_cnt)
        movies_frames_cnt[mov] = rows * width_cnt
        # print(mov, rows * width_cnt)
        height_cnt += rows
        print(height_cnt * 4)

    # since we have a 4 x 4 grid we should create an image of width_cnt * 4 and height_cnt * 4
    total_width = width_cnt * 4
    total_height = height_cnt * 4
    strip_image = Image.new("RGB", (total_width, total_height), (255, 255, 255))
    color_index = 0

    im_height = strip_image.height
    im_width = strip_image.width
    print()
    print("This is image", im_width, "x", im_height)
    finished_movies = []
    for i in range(len(movies)):
        # now we need to fill in the strip image
        mov = movies[i]
        main_dir = f"./output/videos/{mov}/frames"
        folders = os.listdir(main_dir)

        row_start_y = sum(
            [int((movies_frames_cnt[m] / width_cnt)) * 4 for m in finished_movies]
        )

        print(row_start_y)

        # print(mov, row_start_y)

        img_cnt = 0
        for folder in folders:
            folder_path = os.path.join(main_dir, folder)
            # check if it is a directory
            if not os.path.isdir(folder_path):
                continue
            max_cnt = movies_frames_cnt[mov]
            if img_cnt >= max_cnt:
                print("break")

                break
            for fname in os.listdir(folder_path):
                chunk_num = folder_path.split("_")[-1]
                if img_cnt >= max_cnt:
                    print("break")
                    break
                if fname.lower().endswith(".jpg") and fname.startswith("palette_"):
                    frame_num = fname.split("_")[-1].split(".")[0]
                    path = os.path.join(folder_path, fname)
                    img = Image.open(path)
                    img_4x4 = img.resize((4, 4))
                    # get the position to paste the image
                    top_left_y = row_start_y + (img_cnt // width_cnt) * 4
                    top_left_x = (img_cnt % width_cnt) * 4
                    for y_i in range(4):
                        y = top_left_y + y_i
                        for x_i in range(4):
                            x = top_left_x + x_i
                            color = img_4x4.getpixel((x_i, y_i))
                            # print(color)
                            # print(color)
                            # strip_image.putpixel((x, y), color)
                            # print(x, y, color)
                            try:
                                strip_image.putpixel((x, y), color)
                            except:
                                raise Exception(f"Error at {x}, {y} for {mov}")
                            color_index += 1
                    img_cnt += 1
        finished_movies.append(mov)
        if i > 0:
            # draw a line
            for x in range(im_width):
                strip_image.putpixel((x, row_start_y), (255, 0, 0, 10))

    # enlarge the image
    scale_size = 50
    strip_image = strip_image.resize(
        (total_width * scale_size, total_height * scale_size), Image.NEAREST
    )
    strip_image.save("strip_image.png")


if __name__ == "__main__":
    create_image_strip()
    # create_image_strip("vanessa_trick")
    # create_image_strip("part_of_your_world")
    # create_image_strip("poor_unfortunate_souls")
    # create_image_strip("price")
    # create_image_strip("under_the_sea")
    # create_image
