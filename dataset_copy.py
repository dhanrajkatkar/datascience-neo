import pandas as pd
from os import listdir, path
from tqdm import tqdm
from datetime import datetime
from numpy import ndarray
from threading import Thread
from queue import Queue


# TODO dynamic Thread execution
no_of_threads = 4
queue_objects = [Queue() for i in range(no_of_threads)]


# TODO File copy code with all exceptions
def copy_data(q):
    pbar = tqdm(total=q.qsize(), position=0, leave=True)
    while not q.empty():
        image_path = q.get()
        # copy code
        shutil.move(os.path.join(source_dir, file_name), os.path.join(target_dir, file_name))

        pbar.update(1)
    pbar.close()


# TODO efficient read operation
def read_folders(data_dir, destination_dir):
    folder_elements = listdir(data_dir)
    counter = 0
    # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
    for element in folder_elements:
        element_path = path.join(data_dir, element)
        destination_path = path.join(destination_dir, element)

        if path.isfile(element_path) and element_path[-4:] in ['.jpg', '.png', '.bmp']:
            queue_objects[counter % no_of_threads].put(
                (element_path, destination_path))
            counter += 1
        elif path.isdir(element_path):
            read_folders(element_path, destination_path)


if __name__ == '__main__':
    dataset_folder = "read_images"
    destination_dir = "dest"
    read_folders(dataset_folder, destination_dir)
    for obj in queue_objects:
        Thread(target=copy_data, args=(obj,)).start()
