#import pandas as pd
from os import listdir, path, scandir
#from tqdm import tqdm
from datetime import datetime
#from numpy import ndarray
#from threading import Thread
from queue import Queue

# TODO dynamic Thread execution 
no_of_threads = 4
q0 = Queue()
q1 = Queue()
q2 = Queue()
q3 = Queue()

# TODO File copy code with all exceptions
#def copy_data(q):
#    pbar = tqdm(total=q.qsize(), position=0, leave=True)
#   while not q.empty():
#        image_path, dest_path = q.get()
        # copy code
#       pbar.update(1)
#    pbar.close()


# TODO efficient read operation 
def read_folders(data_dir, destiantion_dir):
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
                q3.put(element_path, destination_path,)
            counter += 1
        elif element.is_dir():
            read_folders(element_path,destination_path)


if __name__ == '__main__':
    dataset_folder = "E:\\Imagesforscan"
    destination_folder = "E:\\folder1"
    begin_time = datetime.now()
    read_folders(dataset_folder,destination_folder)
    print(datetime.now() - begin_time)  


#    Thread(target=copy_data, args=(q0,)).start()
#    Thread(target=copy_data, args=(q1,)).start()
#    Thread(target=copy_data, args=(q2,)).start()
#    Thread(target=copy_data, args=(q3,)).start()
    

