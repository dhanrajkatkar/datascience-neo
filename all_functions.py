from os import listdir, path, scandir, walk
from tqdm import tqdm
from queue import Queue

# TODO dynamic Thread execution 

q0 = Queue()
q1 = Queue()
q2 = Queue()
q3 = Queue()


#  Read operation using listdir
def read_folders_listdir(data_dir, destiantion_dir):
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
            read_folders_listdir(element_path,destiantion_dir)


#  Read operation using scandir
def read_folders_scandir(data_dir, destiantion_dir):
    folder_elements = scandir(data_dir)
    counter = 0
    # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
    for element in folder_elements:
        element_path = path.join(data_dir, element)
        destination_path = path.join(destiantion_dir, element)
        if element.is_file() and element_path[-4:] in ['.jpg', '.png', '.bmp']:
            if counter % 4 == 0:
                q0.put(element_path, destination_path)
            elif counter % 4 == 1:
                q1.put(element_path, destination_path)
            elif counter % 4 == 2:
                q2.put(element_path, destination_path)
            elif counter % 4 == 3:
                q3.put(element_path, destination_path)
            counter += 1
        elif element.is_dir():
            read_folders_scandir(element_path,destination_path)



#  Read operation using walkdir
def read_folders_walkdir(data_dir, destiantion_dir):
    folder_elements = walk(data_dir)
    counter = 0
    # reading all sub-folders of the dataset & tqdm is used for creating a progress bar
    for root,dirs,files in folder_elements:
        for element in files:
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
                    q3.put(element_path, destiantion_dir)
                    counter += 1
                else:
                    break
            



if __name__ == '__main__':
    dataset_folder = "E:\\Imagesforscan"
    destination_folder = "E:\\folder1"
    read_folders_listdir(dataset_folder,destination_folder)
    read_folders_walkdir(dataset_folder,destination_folder)
    read_folders_scandir(dataset_folder,destination_folder)
    





