from os import listdir, path
from threading import Thread
import cv2

# Folder path of the images
folder_path = '/home/webwerks/test_data_for_crop'

# Splitting the list to append filename
list0, list1, list2, list3 = [], [], [], [] 
counter = 0
for f in listdir(folder_path):
    file_name = path.join(folder_path, f)
    # Checking file extection & if the file exists in given path
    if path.isfile(file_name) and (file_name[-4:] in ['.jpg', 'jpeg', '.bmp', '.png']):
        if counter % 4 == 0:
            list0.append(file_name)
        elif counter % 4 == 1:
            list1.append(file_name)
        elif counter % 4 == 2:
            list2.append(file_name)
        elif counter % 4 == 3:
            list3.append(file_name)
        counter += 1
len(list0)

# Importing tqdm to create progress bar to check execution of each thread
from tqdm import tqdm

# Defining a function to crop an image
def crop_images(list_images, output_path):
    for image_path in tqdm(list_images):
    
        # Reading an image
        img = cv2.imread(image_path)
        
        # Getting shape of the image
        w, h, c = img.shape
        left, top, right, bottom = 0, 0, w, h
        factor = .02
        left = int(left + w * factor)
        top = int(top + h * factor)
        right = int(right - w * factor)
        bottom = int(bottom - h * factor)
        
        # Cropping an image
        cropped = img[left:right, top:bottom]
        file_name = path.join(output_path, image_path.split('/')[-1])
        
        # Writing image data to given path
        cv2.imwrite(file_name, cropped)
        
 
# Output path to store the cropped images        
output_path = '/home/webwerks/test_data_for_crop/cropped'

# Executing the thread for every list
Thread(target=crop_images, args=(list0, output_path)).start()
Thread(target=crop_images, args=(list1, output_path)).start()
Thread(target=crop_images, args=(list2, output_path)).start()
Thread(target=crop_images, args=(list3, output_path)).start()


