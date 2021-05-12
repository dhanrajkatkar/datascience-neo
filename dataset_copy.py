import shutil
from os import path, scandir
from queue import Queue
from threading import Thread
import os

from tqdm import tqdm

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
        shutil.copy(image_path, dest_path)
        pbar.update(1)
    pbar.close()


#  Read all folders recursively
def read_folders(data_dir, destination_dir):
    '''
    Read folders recursively and put files into queues

    Args:
            data_dir(str): Source path
            destination_dir(str): Destination path

    Returns:
            None
    '''
    folder_elements = scandir(data_dir)
    counter = 0
    # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
    for element in folder_elements:
        element_path = path.join(data_dir, element.path)

        destination_path = path.join(destination_dir)

        if element.is_file() and element_path[-4:] in ['.jpg', '.png', '.bmp']:
            queue_objects[counter % NO_OF_THREADS].put(
                (element_path, destination_path))
            counter += 1

        elif element.is_dir():
            read_folders(element_path, destination_path)


def delete_from_destination(file_name, destination_dir):
    path = os.path.join(destination_dir, file_name)
    os.remove(path)
    print("file named", path, "is deleted")


if __name__ == '__main__':
    dataset_folder = r"E:\\Imagesforscan"
    destination_dir = r"E:\\folder1"
    #  dataset_folder = '/home/webwerks/Desktop/Neosoft_Training/PETA/Reviewed/3DPeS/normal_data'
    #  destination_dir = "/home/webwerks/Desktop/Neosoft_Training/PETA/Reviewed/3DPeS/test"
    file_name = "#"

    read_folders(dataset_folder, destination_dir)
    #  delete_from_destination(file_name, destination_dir)

    # Start n separate threads
    for obj in queue_objects:
        Thread(target=copy_data, args=(obj,)).start()
