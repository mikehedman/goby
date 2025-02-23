# copies original images to the converted folder
# and makes appropriate mirror images
# copies generated images

import os
import cv2
import shutil
from os.path import abspath, dirname, join
from random import sample
import sys
ai_dir = dirname(dirname(abspath(__file__)))
sys.path.append(ai_dir)
import shared

VERTICAL = 0
HORIZONTAL = 1

#moves one set of images from the originals folder to the training folder
def collect_original_images():
    source_dir_index = 0 #used so that there are no name conflicts in the converted folder

    #loop through the directories in the originals folder. Each set typically represents one session of collecting images
    for set_dir in [ f1.path for f1 in os.scandir(shared.ORIGINALS_DIR) if f1.is_dir() ]:

        print(set_dir)
        for classification in [ f2.name for f2 in os.scandir(set_dir) if f2.is_dir() ]:
            dir_to_process = join(set_dir, classification)
            print(dir_to_process)
            source_dir_index += 1
            files = os.listdir(dir_to_process)
            for file_name in files:
                if file_name.startswith('.'):
                    continue
                if not file_name.endswith('.png'):
                    continue

                # print(file_name)
                im_cv = cv2.imread(join(dir_to_process, file_name))
                #copy over the original image
                if classification != "flippable":
                    cv2.imwrite(join(shared.TRAINING_DIR, classification, f"{source_dir_index}_{file_name}"), im_cv)

                #save "flippable" images to the "good" folder with a special name so we can find them later
                if classification == "flippable":
                    #"flippable" images have a cross, but are when leaving the wall, so are "good", and can also be walls when vertically flipped
                    cv2.imwrite(join(shared.TRAINING_DIR, "good", f"{source_dir_index}_flippable_{file_name}"), im_cv)
def perform_augmentation():
    for classification in [ f2.name for f2 in os.scandir(shared.TRAINING_DIR) if f2.is_dir() ]:
        dir_to_process = join(shared.TRAINING_DIR, classification)
        print(dir_to_process)

        files = os.listdir(dir_to_process)
        for file_name in files:
            # print(file_name)
            im_cv = cv2.imread(join(dir_to_process, file_name))
            #create additional images by manipulating the original
            if classification == "good" and "flippable" in file_name:
                #"flippable" images have a cross, but are when leaving the wall, so are "good", and can also be walls when vertically flipped
                im_mirror = cv2.flip(im_cv, HORIZONTAL)
                cv2.imwrite(join(shared.TRAINING_DIR, classification, f"mirror{HORIZONTAL}_{file_name}"), im_mirror)

                im_mirror = cv2.flip(im_cv, VERTICAL)
                cv2.imwrite(join(shared.TRAINING_DIR, "wall", f"mirror{VERTICAL}_{file_name}"), im_mirror)
                im_mirror = cv2.flip(im_mirror, HORIZONTAL)
                cv2.imwrite(join(shared.TRAINING_DIR, "wall", f"mirror{VERTICAL}{HORIZONTAL}_{file_name}"), im_mirror)
            if classification == "left":
                im_mirror = cv2.flip(im_cv, HORIZONTAL)
                cv2.imwrite(join(shared.TRAINING_DIR, "right", f"mirror{HORIZONTAL}_{file_name}"), im_mirror)
            if classification == "right":
                im_mirror = cv2.flip(im_cv, HORIZONTAL)
                cv2.imwrite(join(shared.TRAINING_DIR, "left", f"mirror{HORIZONTAL}_{file_name}"), im_mirror)
            if classification == "good":
                im_mirror = cv2.flip(im_cv, HORIZONTAL)
                cv2.imwrite(join(shared.TRAINING_DIR, classification, f"mirror{HORIZONTAL}_{file_name}"), im_mirror)
                im_mirror = cv2.flip(im_cv, VERTICAL)
                cv2.imwrite(join(shared.TRAINING_DIR, classification, f"mirror{VERTICAL}_{file_name}"), im_mirror)
            if classification == "wall":
                im_mirror = cv2.flip(im_cv, HORIZONTAL)
                cv2.imwrite(join(shared.TRAINING_DIR, classification, f"mirror{HORIZONTAL}_{file_name}"), im_mirror)

#recursively move a percentage of the training set to the prediction set
def move_files_to_prediction_set(percentage):
    source_dir = shared.TRAINING_DIR
    destination_dir = shared.PREDICTION_DIR
    for root, dirs, files in os.walk(source_dir):
        # Determine the path to the destination directory
        dest_path = root.replace(source_dir, destination_dir, 1)

        # Calculate the number of files to move, but no more than 5
        # num_files_to_move = min(int(len(files) * (percentage / 100)), 5)
        num_files_to_move = int(len(files) * (percentage / 100))  ## no limit

        # Randomly select files to move
        selected_files = sample(files, num_files_to_move)

        # Create the destination directory if it does not exist
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        # Copy each file to the destination directory
        for file in selected_files:
            src_file = join(root, file)
            dest_file = join(dest_path, file)
            shutil.move(src_file, dest_file)


def main():
    shared.setup_dirs(shared.TRAINING_DIR)
    shared.setup_dirs(shared.PREDICTION_DIR)

    collect_original_images()
    move_files_to_prediction_set(5)
    perform_augmentation()
main()

