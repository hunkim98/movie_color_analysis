import os

col_length = 10


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
            pass
