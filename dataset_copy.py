import pandas as pd
import shutil
from os import listdir, path
from tqdm import tqdm
from datetime import datetime
from numpy import ndarray
from threading import Thread
from queue import Queue

source_dir = ''
target_dir = ''
file_names = os.listdir(source_dir)

# TODO dynamic Thread execution 
no_of_threads = 4
q0 = Queue()
q1 = Queue()
q2 = Queue()
q3 = Queue()

# TODO File copy code with all exceptions
def copy_data(q):
    pbar = tqdm(total=q.qsize(), position=0, leave=True)
    while not q.empty():
        image_path, dest_path = q.get()
        # copy code
        for file_name in file_names:
        shutil.copy(os.path.join(source_dir, file_name), os.path.join(target_dir, file_name))
        pbar.update(1)
    pbar.close()


# TODO efficient read operation 
def read_folders(data_dir, destiantion_dir):
    folder_elements = listdir(data_dir)
    counter = 0
    # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
    for element in folder_elements:
        element_path = path.join(data_dir, element)
        destination_path = path.join(destiantion_dir, element)
        if path.isfile(element_path) and element_path[-4:] in ['.jpg', '.png', '.bmp']:
            if counter % 4 == 0:
                q0.put(element_path, destination_path)
            elif counter % 4 == 1:
                q1.put(element_path, destination_path)
            elif counter % 4 == 2:
                q2.put(element_path, destination_path)
            elif counter % 4 == 3:
                q3.put(element_path, destination_path,)
            counter += 1
        elif path.isdir(element_path):
            read_folders(element_path)


if __name__ == '__main__':
    dataset_folder = ""
    read_folders(dataset_folder)
    Thread(target=copy_data, args=(q0,)).start()
    Thread(target=copy_data, args=(q1,)).start()
    Thread(target=copy_data, args=(q2,)).start()
    Thread(target=copy_data, args=(q3,)).start()
    
