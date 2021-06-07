from tqdm import tqdm
import shutil
from os import path, scandir, remove, cpu_count, stat, walk, makedirs, getcwd
from queue import Queue
from threading import Thread
from tkinter import Tk, Button, Frame
import cv2
from create_dataset import CreateDataset
from project_config import *


class FileOperations:

    def __init__(self, master):
        # Number of threads to execute
        frame = Frame(master)
        frame.pack()

        self.NO_OF_THREADS = cpu_count()
        self.queue_objects = [Queue() for _ in range(self.NO_OF_THREADS)]
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
        """
                Deletes the specified file
                Args:
                        path_name(str): File path
                Returns:
                        None
                """
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


class DatasetClass:
    """ Class Logic for Validation of the data """

    @staticmethod
    def iter_valid_files(path1):
        for subdir, dirs, files in walk(path1):
            for file in files:
                file_path = path.join(subdir, file)
                aux = file_path.rpartition("_")
                file_name = aux[0]
                file_number, delimiter, file_ext = aux[2].rpartition(".")
                yield file_path, file_name, file_number, file_ext

    @staticmethod
    def is_extension_valid(file_ext):
        if file_ext == 'jpg' or file_ext == 'txt':
            return True
        return False

    @staticmethod
    def pair_file_exists(file_name, file_number, file_ext):
        file_ext_to_check = 'txt' if file_ext == 'jpg' else 'jpg'
        if path.isfile(file_name + "_" + file_number + "." + file_ext_to_check):
            return True
        return False


class DatasetValidator(DatasetClass):
    """
    Validates that a given path contains a dataset was correctly labelled
    """

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.Validate = Button(master, text="Validate",
                               command=lambda: self.visual_inspection(r"E:\coco dataset\coco_v0"))
        self.Validate.pack(pady=20)

    def visual_inspection(self, dataset_dir):
        filepaths_dict = {}
        for file_path, file_name, file_number, file_ext in self.iter_valid_files(dataset_dir):
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
                img_path = "{}_{}.jpg".format(file_name, file_number)
                image = cv2.imread(img_path)
                img_height, img_width, img_channels = image.shape
                image = cv2.resize(image, (800, int(800 / img_width * img_height)))
                img_height, img_width, img_channels = image.shape
                with open(img_path, 'r') as fh:
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


class ExportAnnotations:
    def __init__(self):
        self.status_msg = None
        self.classes = []
        self.project_name = PROJECT_NAME
        self.training_path = path.join("training", self.project_name)
        self.video_file_path = r''
        self.annotation_file_path = r''
        self.class_file_path = r''
        self.dataset_export_path = r''
        self.cfg_file_yolo = path.join(self.training_path, self.project_name + ".cfg")
        self.data_file_yolo = path.join(self.training_path, self.project_name + ".data")
        self.names_file_yolo = path.join(self.training_path, self.project_name + ".names")
        self.training_images_list = path.join(self.training_path, "train.txt")
        self.test_images_list = path.join(self.training_path, "test.txt")
        self.video_data = []
        print("Initialized...")

        self.default_lookup_path = DEFAULT_LOOKUP_PATH

        if not path.exists(path.join("training", self.project_name)):
            base_path = getcwd()
            new_dir = path.join(base_path, "training")
            proj_dir = path.join(new_dir, self.project_name)
            makedirs(proj_dir)
            bak_dir = path.join(proj_dir, "backup")
            makedirs(bak_dir)
        self.training_path = path.join("training", self.project_name)

    def fast_scandir(self, dirname):
        subfolders = [f for f in scandir(dirname) if f.is_dir()]
        for dirname in list(subfolders):
            subfolders.extend(self.fast_scandir(dirname))
        return subfolders

    def export_classes_file(self):
        with open(self.class_file_path, 'w') as cls_file:
            for fl in self.fast_scandir('/home/webwerks/Desktop/cemtrex'):
                if len(fl.name) == 13:
                    try:
                        if int(fl.name):
                            # scan for videos
                            for i in scandir(fl.path):
                                for vid_file in scandir(i.path):
                                    txt = i.path.split('.')[0]+'txt'
                                    if i.name[-4:] in ['.mp4', '.avi', '.mkv'] and path.exists(txt):
                                        self.video_data.append((i.path, txt))
                                    else:
                                        # log this
                                        pass
                            self.classes.append(fl.name)
                            cls_file.write(fl + '\n')
                    except ValueError:
                        continue

    # display status message
    def display_message(self, msg):
        print(msg)
        self.status_msg.set(msg)

    # check if all paths are selected before proceeding
    def paths_saved(self):
        return bool(self.video_file_path) & bool(self.annotation_file_path) & bool(self.class_file_path) & bool(
            self.dataset_export_path)

    def save_paths(self):
        for data in self.video_data:
            if self.paths_saved():
                self.status_msg.set("Generating normalized dataset...")
                object_dataset = CreateDataset(data[0], data[1], self.class_file_path,
                                               self.dataset_export_path)
                created = object_dataset.create_dataset() or None
                if created:
                    self.display_message("Normalized dataset generated for training!")
                else:
                    self.display_message("Something went wrong!")
            else:
                msg = "Please select valid paths !"
                self.display_message(msg)


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
    root.mainloop()
