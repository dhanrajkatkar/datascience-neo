from tqdm import tqdm
import shutil
from os import path, scandir, remove, cpu_count, stat, walk, makedirs, getcwd, rmdir
from queue import Queue
from threading import Thread
from tkinter import Tk, Button, Frame, StringVar, Message
import cv2
import logging
from datetime import datetime
from create_dataset import CreateDataset
import config
from glob import glob
from sys import platform
import subprocess
from scripts.gen_anchors import genrate_anchor_file


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

#  validate button todo
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
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.NO_OF_THREADS = cpu_count()
        self.queue_objects = [Queue() for _ in range(self.NO_OF_THREADS)]
        self.Transfer = Button(master, text="sync", command=lambda: self.run())
        self.Transfer.pack(pady=20)
        # self.font_style = ('tahoma', 9, 'bold')
        #
        # # dashboard subframes
        # self.frame_dboard = Frame(self.window)
        # self.frame_a = Frame(self.frame_dboard, height=10, bd=1)
        # self.frame_b = Frame(self.frame_dboard, height=5, bd=1)
        #
        # # status message widget
        # self.status_msg = StringVar()
        # self.status = Message(self.frame_dboard, textvariable=self.status_msg)
        # self.status.config(font=self.font_style, width=500, fg="red")

        self.classes = []
        self.video_data = []
        self.dataset_path = config.DATASET_PATH
        self.project_name = config.PROJECT_NAME
        self.training_path = path.join("training", self.project_name)
        self.class_file_path = config.CLASS_FILE_PATH
        self.dataset_export_path = config.DATASET_EXPORT_PATH
        self.cfg_file_yolo = path.join(self.training_path, self.project_name + ".cfg")
        self.data_file_yolo = path.join(self.training_path, self.project_name + ".data")
        self.names_file_yolo = path.join(self.training_path, self.project_name + ".names")
        self.training_images_list = path.join(self.training_path, "train.txt")
        self.test_images_list = path.join(self.training_path, "test.txt")
        print("Initialized...")

        self.no_of_classes = 0
        self.select_classfile = ""
        self.no_of_anchors = config.NO_OF_ANCHORS
        self.select_video_file = ""
        self.select_annotation_file = ""
        self.select_export_path = ""
        self.yolo_path = config.YOLOPATH
        self.export_classes_file()
        logging.basicConfig(
            filename=config.LOG_FILE,
            filemode='a',
            level=logging.DEBUG,
            format=f'%(levelname)s → {datetime.now()} → %(name)s:%(message)s')

        # remove previous dataset
        if path.exists(self.dataset_export_path):
            rmdir(self.dataset_export_path)
        makedirs(self.dataset_export_path)

        if not path.exists(path.join("training", self.project_name)):
            base_path = getcwd()
            new_dir = path.join(base_path, "training")
            proj_dir = path.join(new_dir, self.project_name)
            makedirs(proj_dir)
            bak_dir = path.join(proj_dir, "backup")
            makedirs(bak_dir)

    def fast_scandir(self, dir_name):
        sub_folders = [f for f in scandir(dir_name) if f.is_dir()]
        for dir_name in list(sub_folders):
            sub_folders.extend(self.fast_scandir(dir_name))
        return sub_folders

    def export_classes_file(self):
        with open(self.class_file_path, 'w') as cls_file:
            for fl in self.fast_scandir(self.dataset_path):
                try:
                    if len(fl.name) == 13 and int(fl.name):
                        for i in scandir(fl.path):
                            for vid_file in scandir(i.path):
                                txt = vid_file.path.split('.')[0] + '_gt.txt'
                                if vid_file.name[-4:] in ['.mp4', '.avi', '.mkv'] and path.exists(txt):
                                    self.video_data.append((vid_file.path, txt))
                                else:
                                    logging.debug(vid_file.path + ' ' + 'pair file not found')
                        self.classes.append(fl.name)
                        cls_file.write(fl.name + '\n')
                except ValueError:
                    continue

    # display status message
    def display_message(self, msg):
        print(msg)
        # self.status_msg.set(msg)

    def save_paths(self, q):
        pbar = tqdm(total=q.qsize(), position=0, leave=True)
        while not q.empty():
            data = q.get()
            # data : (video_path, txt_path)
            if bool(data[0]) & bool(data[1]) & bool(self.class_file_path) & bool(
                    self.dataset_export_path):
                # self.status_msg.set("Generating normalized dataset...")
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
            pbar.update(1)

    # creating train and test dataset from obtained normalized dataset
    def create_train_test_data(self):
        with open(self.training_images_list, "w+") as train_txt, open(self.test_images_list, "w+") as test_txt:
            image_counter = 0
            for image in glob(self.select_export_path + "/*jpg"):
                txt_file = image.replace("jpg", "txt")
                if path.exists(txt_file):
                    if image_counter % 10 == 0:
                        print(image, image_counter)
                        test_txt.write(image + "\n")
                        image_counter += 1
                    else:
                        train_txt.write(image + "\n")
                        image_counter += 1

    # creating and writing into yolo_objects.names file from class.txt file
    def create_name_file(self):
        with open(self.names_file_yolo, "w+") as names_file:
            with open(self.select_classfile, "r") as classfile:
                for line in classfile:
                    self.no_of_classes += 1
                    names_file.write(line)

    # create and writing into yolo_objects.data file
    def create_data_file(self):
        with open(self.data_file_yolo, "w+") as data_file:
            data_file.write("classes= " + str(self.no_of_classes) + "\n")
            data_file.write("names= " + self.names_file_yolo + "\n")
            data_file.write("train= " + self.training_images_list + "\n")
            data_file.write("valid= " + self.test_images_list + "\n")
            data_file.write("backup= " + self.training_path + "\\backup")

    # create and writing into yolo_objects.cfg from yolov3.cfg
    def create_cfg_file(self):

        yolo_layer_lines = [602, 688, 775]
        filter_line_list = [i - 4 for i in yolo_layer_lines]
        class_line_list = [i + 3 for i in yolo_layer_lines]
        anchors_line_list = [i + 2 for i in yolo_layer_lines]

        with open("sample_yolov3.cfg", "r") as cfg_yolo, open(self.cfg_file_yolo, "w+") as new_cfg:
            anchors_path = self.training_path
            genrate_anchor_file(self.training_images_list, self.training_path, int(self.no_of_anchors))
            with open(anchors_path + "\\anchors" + self.no_of_anchors + ".txt") as anchorfile:
                anchors = anchorfile.readline()
                print(anchors)
            for i, line in enumerate(cfg_yolo):
                if i in filter_line_list:
                    filters = (self.no_of_classes + 5) * 3
                    new_cfg.write("filters=" + str(filters) + "\n")
                elif i in class_line_list:
                    new_cfg.write("classes=" + str(self.no_of_classes) + "\n")
                elif i in anchors_line_list:
                    new_cfg.write("anchors = " + anchors)
                else:
                    new_cfg.write(line)

    # todo train button
    def start_training(self):
        self.display_message("Generating normalized dataset...")

        self.create_train_test_data()
        self.create_name_file()
        self.create_data_file()
        self.create_cfg_file()

        # initiate training
        if platform == "win32":
            command_win = [self.yolo_path + "\\darknet.exe", "detector", "train", self.data_file_yolo,
                           self.cfg_file_yolo,
                           self.yolo_path + "\\darknet53.conv.74"]
            subprocess.call(command_win)

    # todo dataset sync button
    # Start n separate threads
    def run(self):
        counter = 0
        # reading all sub-folders of the dataset
        for element in self.video_data:
            self.queue_objects[counter % self.NO_OF_THREADS].put(element)
            counter += 1
        for obj in self.queue_objects:
            Thread(target=self.save_paths, args=(obj,)).start()


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
    # cls_obj = FileOperations(root)
    cls_obj = DatasetValidator(root)
    export_annos_obj = ExportAnnotations(root)
    root.mainloop()
