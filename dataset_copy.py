import filecmp
from tqdm import tqdm
import numpy as np
import shutil
from os import path, scandir, remove, cpu_count, stat
from queue import Queue
from threading import Thread


class FileOperations:

    def __init__(self):
        # Number of threads to execute
        self.NO_OF_THREADS = cpu_count()
        self.queue_objects = [Queue() for i in range(self.NO_OF_THREADS)]
        self.dataset_folder = r"/home/webwerks/Desktop/test/source/"
        self.destination_folder = r"/home/webwerks/Desktop/test/destination/"
        self.src_list = []
        self.dst_list = []
        self.read_folders(self.dataset_folder, self.destination_folder)
        self.read_destination_files()
        self.source_check()

    @staticmethod
    def check_file(image_path, dest_path):
        """
        Take source destination and copy destination check if file exists

        Args:
                image_path(str): Source file path
                dest_path(str): Destination path
        Returns:
                0: File doesn't exist or file exist but content is different
                1: File exist
        """
        if path.exists(dest_path):
            dest_size = stat(dest_path).st_size
            # take the size of source file
            src_size = stat(image_path).st_size
            if dest_size == src_size:
                # same files(including content)
                print("same files(including content)")
                return 1
            else:
                # same file name, different content
                print("same file name, different content")
                return 0

    # File copy code
    def copy_data(self, q):
        """
        Take source destination from queue and copy to the given destination
        Args:
                q(queue): Single queue containing source path of files
        Returns:
                None
        """
        pbar = tqdm(total=q.qsize(), position=0, leave=True)
        while not q.empty():
            image_path, dest_path = q.get()
            if self.check_file(image_path, dest_path):
                pbar.update(1)
                continue
            else:
                # shutil.copy always overights the file if exists at dest
                shutil.copy(image_path, dest_path)
                pbar.update(1)
        pbar.close()

    #  Read all folders recursively
    def read_folders(self, data_dir, destination_folder):
        """
        Read folders recursively and put files into queues
        Args:
                data_dir(str): Source path
                destination_folder(str): Destination path
        Returns:
                None
        """
        folder_elements = scandir(data_dir)
        counter = 0
        # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
        for element in folder_elements:
            element_path = element.path

            destination_path = path.join(destination_folder, element.name)

            if element.is_file() and element_path[-4:] in ['.jpg', '.png', '.bmp']:
                self.queue_objects[counter % self.NO_OF_THREADS].put(
                    (element_path, destination_path))
                counter += 1
                self.src_list.append(element.name)

            elif element.is_dir():
                self.read_folders(element_path, destination_path)

    #  reading the destination files
    def read_destination_files(self):
        folder_elements = scandir(self.destination_folder)
        for element in folder_elements:
            self.dst_list.append(element.name)

    #  checking if source file is deleted if any
    def source_check(self):
        diff_list = [
            deleted_file for deleted_file in self.dst_list if deleted_file not in self.src_list]
        return diff_list

    #  Reading the full path and deleting the file present in the path
    @staticmethod
    def delete_from_destination(path_name):
        file_path = path.join(path_name)
        remove(file_path)

    #  if file not present in Source deleting it in destination too(Syncing)
    def sync_source_destination(self):
        folder_elements = scandir(self.destination_folder)
        for element in folder_elements:
            if element.name not in self.src_list:
                self.delete_from_destination(element.path)

    # Start n separate threads
    def run(self):
        for obj in self.queue_objects:
            Thread(target=self.copy_data, args=(obj,)).start()
        self.sync_source_destination()

    
if __name__ == '__main__':
    cls_obj = FileOperations()
    cls_obj.run()
