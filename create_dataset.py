import cv2
import os
from tqdm import tqdm


class CreateDataset:
    def __init__(self, video_path, annotation_path, classfile_path, export_dataset_path):
        self.video_path = video_path
        self.annotation_path = annotation_path
        self.classfile_path = classfile_path
        self.export_dataset_path = export_dataset_path
        self.classes = []

    def read_class_file(self):
        with open(self.classfile_path, "r") as f_class:
            for line in f_class:
                line = line.rstrip()
                self.classes.append(line)

    def create_dataset(self):
        self.read_class_file()
        with open(self.annotation_path, "r") as f:
            cap = cv2.VideoCapture(self.video_path)
            for line in tqdm(f):
                line = line.rstrip()
                tokenized_line = line.split(",")
                image_name = tokenized_line[0]
                no_of_objects = int(tokenized_line[1])
                frame_number = int(image_name)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
                res, frame = cap.read()
                frame_height, frame_width, _ = frame.shape
                frame_copy = frame.copy()
                video_name = os.path.split(self.video_path)
                with open(self.export_dataset_path + "/" + video_name[1] + "_" + str(frame_number) + ".txt",
                          "w+") as f_txt:
                    for i in range(0, no_of_objects):
                        cx = int(tokenized_line[5 * i + 2])
                        cy = int(tokenized_line[5 * i + 3])
                        width = int(tokenized_line[5 * i + 4])
                        height = int(tokenized_line[5 * i + 5])
                        class_name = tokenized_line[5 * i + 6]
                        # cv2.rectangle(frame, (int(cx - width / 2), int(cy - height / 2)),(int(cx + width / 2),
                        # int(cy + height / 2)), (255, 0, 0), 2)
                        x = round((cx / frame_width), 4)
                        y = round((cy / frame_height), 4)
                        width_normalized = round((width / frame_width), 4)
                        height_normalized = round((height / frame_height), 4)
                        f_txt.write(
                            str(self.classes.index(class_name)) + " " + str(x) + " " + str(y) + " " + str(
                                width_normalized) + " " +
                            str(height_normalized) + "\n")
                    # cv2.imshow("image", frame)
                    im_write_path = os.path.join(self.export_dataset_path,
                                                 video_name[1]) + "_" + str(frame_number) + ".jpg"
                    cv2.imwrite(im_write_path, frame_copy)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     cap.release()
                #     cv2.destroyAllWindows()
                #     break
            cap.release()
            cv2.destroyAllWindows()
            return True
