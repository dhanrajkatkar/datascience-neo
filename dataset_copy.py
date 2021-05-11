import pandas as pd
from os import listdir, path
from tqdm import tqdm
from datetime import datetime
from numpy import ndarray
from threading import Thread
from queue import Queue
import shutil
import os


# Number of threads to execute
NO_OF_THREADS = 4
queue_objects = [Queue() for i in range(NO_OF_THREADS)]


# TODO File copy code with all exceptions
def copy_data(q):
    '''
    Take source destination from queue and copy to the given destination 

    Args:
            q(queue): Single queue containing source path of files

    Returns:
            None
    '''
    pbar = tqdm(total=q.qsize(), position=0, leave=True)
    while not q.empty():
        image_path, dest_path = q.get()
        # copy code
        # split("/")[-1] split file name from path
        shutil.copy(image_path,
                    os.path.join(destination_dir, image_path.split("/")[-1]))
        pbar.update(1)
    pbar.close()

# TODO efficient read operation


def read_folders(data_dir, destination_dir):
    '''
    Read folders recursively and put files into queues

    Args:
            data_dir(str): Source path
            destination_dir(str): Destination path

    Returns:
            None
    '''
    folder_elements = listdir(data_dir)
    counter = 0
    # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
    for element in folder_elements:
        element_path = path.join(data_dir, element)
        destination_path = path.join(destination_dir, element)

        if path.isfile(element_path) and element_path[-4:] in ['.jpg', '.png', '.bmp']:
            queue_objects[counter % NO_OF_THREADS].put(
                (element_path, destination_path))

            counter += 1
        elif path.isdir(element_path):
            read_folders(element_path, destination_path)


if __name__ == '__main__':
    dataset_folder = "#"
    destination_dir = "#"
    read_folders(dataset_folder, destination_dir)

    # Start n separate threads
    for obj in queue_objects:
        Thread(target=copy_data, args=(obj,)).start()
