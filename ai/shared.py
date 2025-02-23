from os import mkdir
from os.path import abspath, dirname, exists, join
import shutil

PROJECT_DIR = dirname(abspath(__file__))

ORIGINALS_DIR = join(PROJECT_DIR, "images", "originals")
GENERATED_DIR = join(ORIGINALS_DIR, "generated_images")

TRAINING_DIR = join(PROJECT_DIR, "images", "training_set")
PREDICTION_DIR = join(PROJECT_DIR, "images", "prediction_set")

#load the classes. needs to be in a file since it's needed on the Pi
labels_filename = join(PROJECT_DIR, "tensorflow", "labels.txt")
with open(labels_filename, 'r') as f:
  CLASSES = [line.strip() for line in f.readlines()]


HEIGHT = 640
WIDTH = 480


def setup_dirs(base_dir):
  if exists(base_dir):
    shutil.rmtree(base_dir)
  mkdir(base_dir)
  mkdir(join(base_dir, "right"))
  mkdir(join(base_dir, "left"))
  mkdir(join(base_dir, "good"))
  mkdir(join(base_dir, "bad"))
  mkdir(join(base_dir, "wall"))
