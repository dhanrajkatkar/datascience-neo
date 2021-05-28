import filecmp
from tqdm import tqdm
import numpy as np
import shutil
from os import path, scandir, remove, cpu_count, stat, walk
from queue import Queue
from threading import Thread
from tkinter import Tk, Button, Frame, filedialog
import cv2


class FileOperations:

    def __init__(self, master):
        # Number of threads to execute
        frame = Frame(master)
        frame.pack()

        self.NO_OF_THREADS = cpu_count()
        self.queue_objects = [Queue() for i in range(self.NO_OF_THREADS)]
        self.dataset_folder = r"E:\images"
        self.destination_folder = r"E:\destination"
        self.src_list = []
        self.dst_list = []
        self.read_folders(self.dataset_folder, self.destination_folder)
        self.read_destination_files()
        self.source_check()
        self.Transfer = Button(master, text="Copy", command=lambda: self.run())
        self.Transfer.pack(pady=20)

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


'''Class Logic for Validation of the data '''


class DS_Class:
    def __init__(self):
        pass

    def iter_valid_files(self, path1):
        for subdir, dirs, files in walk(path1):
            for file in files:
                file_path = path.join(subdir, file)
                aux = file_path.rpartition("_")
                file_name = aux[0]
                file_number, delimiter, file_ext = aux[2].rpartition(".")
                yield file_path, file_name, file_number, file_ext

    def is_extension_valid(self, file_ext):
        if file_ext == 'jpg' or file_ext == 'txt':
            return True
        return False

    def pair_file_exists(self, file_name, file_number, file_ext):
        file_ext_to_check = 'txt' if file_ext == 'jpg' else 'jpg'
        if path.isfile(file_name + "_" + file_number + "." + file_ext_to_check):
            return True
        return False


class DS_Creator_NNReadable(DS_Class):
    """
    Creates a folder in which there will be all necessary files to train the neural network
    """

    def __init__(self):
        pass


class DS_Validator(DS_Class):
    """
    Validates that a given path contains a dataset was correctly labelled
    """

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.Validate = Button(master, text="Validate",
                               command=lambda: self.visual_inspection("E:\coco dataset\coco_v0"))
        self.Validate.pack(pady=20)

    def visual_inspection(self, path):
        filepaths_dict = {}
        for file_path, file_name, file_number, file_ext in self.iter_valid_files(path):
            if not self.is_extension_valid(file_ext):
                print("not a valid extension")
                continue

            if not self.pair_file_exists(file_name, file_number, file_ext):
                print("doesnt have pair file")
                continue

            if file_name in filepaths_dict:
                filepaths_dict[file_name] += 0.5
            else:
                filepaths_dict[file_name] = 0.5
                image = cv2.imread(file_name + "_" + file_number + ".jpg")
                img_height, img_width, img_channels = image.shape
                image = cv2.resize(image, (800, int(800 / img_width * img_height)))
                img_height, img_width, img_channels = image.shape
                with open(file_name + "_" + file_number + ".txt", 'r') as fh:
                    for line in fh:
                        cat, cx, cy, w, h = line.split(" ")
                        cx, cy, w, h = float(cx), float(cy), float(w), float(h)
                        start_point = (int((cx - w / 2) * img_width), int((cy - h / 2) * img_height))
                        end_point = (int((cx + w / 2) * img_width), int((cy + h / 2) * img_height))
                        labeled_img = cv2.rectangle(image, start_point, end_point, (255, 0, 0), 2)
                cv2.imshow("Checking bounding boxes", labeled_img)
                print(filepaths_dict)
                # cv2.destroyAllWindows(1000)
                cv2.waitKey()

        print(filepaths_dict)


if __name__ == '__main__':
    root = Tk()
    box_widht = 400
    box_height = 250
    root.title('Copying the Data')
    root.geometry("400x200")
    WS = root.winfo_screenwidth()
    HS = root.winfo_screenheight()
    x = (WS / 2) - (400 / 2)
    y = (HS / 2) - (250 / 2)
    root.geometry('%dx%d+%d+%d' % (box_widht, box_height, x, y))
    root.resizable(1, 1)
    root.configure(background="#515151")
    cls_obj = FileOperations(root)
    validator = DS_Validator(root)
    root.mainloop()
