from tqdm import tqdm
import numpy as np
import shutil
from os import path, scandir, remove, cpu_count, stat
from queue import Queue
from threading import Thread


# Number of threads to execute

NO_OF_THREADS = cpu_count()
queue_objects = [Queue() for i in range(NO_OF_THREADS)]

src_list = []
dst_list = []


def check_file(image_path, dest_path):
    '''
    Take source destination and copy destination check if file exists 

    Args:
            image_path(str): Source file path
            dest_path(str): Destination path
    Returns:
            0: File doesn't exist or file exist but content is different
            1: File exist
    '''

    try:
        '''
        os.stat searches for file, if exists then returns the attributes of file, otherwise OSError 
        Take size from the attributes of the file
        '''
        dest_size = stat(dest_path).st_size
        # take the size of source file
        src_size = stat(image_path).st_size
        if(dest_size == src_size):
            # same files(including content)
            print("same files(including content)")
            return 1
        else:
            # same file name, different content
            print("same file name, different content")
            return 0
    except OSError:
        # file doesn't exist if OSError
        print("file doesn't exist if OSError")
        return 0


# File copy code
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
        if (check_file(image_path, dest_path)):
            pbar.update(1)
            continue
        else:
            # shutil.copy always overights the file if exists at dest
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
            src_list.append(element.name)

        elif element.is_dir():
            read_folders(element_path, destination_path)


#  reading the destination files
def read_destination_files(destination_dir):
    folder_elements = scandir(destination_dir)
    for element in folder_elements:
        dst_list.append(element.name)


#  checking if source file is deleted if any
def source_check(dst_list, src_list):
    diff_list = np.setdiff1d(dst_list, src_list)
    return diff_list


#  Reading the full path and deleting the file present in the path
def delete_from_destination(path_name):
    file_path = path.join(path_name)
    remove(file_path)
    print("file named", file_path, "is deleted")


if __name__ == '__main__':

    dataset_folder = "#"
    destination_dir = "#"
    read_folders(dataset_folder, destination_dir)

    # Start n separate threads
    for obj in queue_objects:
        Thread(target=copy_data, args=(obj,)).start()
    read_destination_files(destination_dir)
    source_check()

    # Calling delete function
    delete_from_destination(dest_img_path)
