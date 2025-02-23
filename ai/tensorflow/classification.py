# Ideas borrowed from https://www.tensorflow.org/tutorials/images/classification
import os
import pathlib
import sys
from os.path import abspath, dirname, join

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

ai_dir = dirname(dirname(abspath(__file__)))
sys.path.append(ai_dir)
import shared

project_dir = dirname(dirname(dirname(abspath(__file__))))
data_dir = pathlib.Path(shared.TRAINING_DIR).with_suffix('')
image_count = len(list(data_dir.glob('*/*.png')))

BATCH_SIZE = 32
EPOCHS = 29
HIDDEN_UNITS = 1000
IMG_HEIGHT = 640
IMG_WIDTH = 480
VALIDATION_SPLIT = 0.4

MODEL_FILENAME = 'lane_classification_model.keras'
LITE_MODEL_FILENAME = 'lane_classification_model.tflite'
LABELS_FILENAME = 'labels.txt'

def normalize_image(image, label):
  # Normalizes images: `uint8` -> `float32`.
  return (image / 255.0), label

def save_labels(labels):
  with open(LABELS_FILENAME, 'w') as f:
    for label in labels:
      f.write(f"{label}\n")

def convert_model_to_tflite(model):
  # Convert the model to TensorFlow Lite format
  converter = tf.lite.TFLiteConverter.from_keras_model(model)
  tflite_model = converter.convert()
  with open(LITE_MODEL_FILENAME, 'wb') as f:
    f.write(tflite_model)

def check_predictions(model, predict_dir, results_file):
  count = 0
  corrects = 0

  for root, dirs, files in os.walk(predict_dir):
    for file in files:
      predict_file = join(root, file)

      # get dir name
      expected_class = os.path.basename(root)

      # ignore hidden files like .DS_Store
      if file.startswith('.'):
        continue
      img = tf.keras.utils.load_img(
        predict_file, target_size=(IMG_HEIGHT, IMG_WIDTH)
      )
      img_array = tf.keras.utils.img_to_array(img)
      img_array = img_array / 255.0
      img_array = tf.expand_dims(img_array, 0)  # Create a batch

      predictions = model(img_array)
      score = tf.nn.softmax(predictions[0])

      correct = shared.CLASSES[np.argmax(score)] == expected_class
      count += 1
      if correct:
        corrects += 1
  results_file.write("precision: {:.2f}\n\n".format(100 * corrects / count))

def get_min_number_of_images_per_class(dataset):
  class_names = dataset.class_names
  class_counts = {}

  for images, labels in dataset:
    for label in labels:
      class_name = class_names[label.numpy()]
      class_counts[class_name] = class_counts.get(class_name, 0) + 1
  print("class_counts: ", class_counts)
  return min(class_counts.values())

def build_model():
  train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=VALIDATION_SPLIT,
    subset="training",
    seed=123,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE)

  val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=VALIDATION_SPLIT,
    subset="validation",
    seed=123,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE)

  class_names = train_ds.class_names
  print(class_names)

  # use the same number of images per class
  # min_count = get_min_number_of_images_per_class(train_ds)
  # train_ds = train_ds.take(min_count)

  for image_batch, labels_batch in train_ds:
    print(image_batch.shape)
    print(labels_batch.shape)
    break

  AUTOTUNE = tf.data.AUTOTUNE

  train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
  val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

  # standardize data
  normalization_layer = layers.Rescaling(1. / 255, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3))

  train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
  val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

  num_classes = len(class_names)

  results = open("results.txt", "w")

  ##this was put in a loop to test different dropout values
  for i in range(4, 5):
    dropout = i / 10

  # dropout = 0.8
    print("dropout: ", dropout)
    model = Sequential([
      layers.Conv2D(16, 3, padding='same', activation='relu'),
      layers.MaxPooling2D(),
      layers.Dropout(dropout),
      layers.Conv2D(32, 3, padding='same', activation='relu'),
      layers.MaxPooling2D(),
      layers.Dropout(dropout),
      layers.Conv2D(64, 3, padding='same', activation='relu'),
      layers.MaxPooling2D(),
      layers.Dropout(dropout),
      layers.Flatten(),
      layers.Dense(HIDDEN_UNITS, activation='relu'),
      layers.Dense(num_classes)
    ])

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    history = model.fit(
      train_ds,
      validation_data=val_ds,
      epochs=EPOCHS
    )

    results.write(f"dropout: {dropout}\n")
    for key, value in history.history.items():
      results.write(f"{key}: {value}\n")

    check_predictions(model, shared.PREDICTION_DIR, results)
  results.close()

  model.summary()

  # Save the entire model as a `.keras` zip archive.
  model.save(MODEL_FILENAME)

  # save files that will be used on the Pi
  save_labels(class_names)

  plot_charts(history)

  return model


def plot_charts(history):
  acc = history.history['accuracy']
  val_acc = history.history['val_accuracy']
  loss = history.history['loss']
  val_loss = history.history['val_loss']
  epochs_range = range(EPOCHS)
  plt.figure(figsize=(8, 8))
  plt.subplot(1, 2, 1)
  plt.plot(epochs_range, acc, label='Training Accuracy')
  plt.plot(epochs_range, val_acc, label='Validation Accuracy')
  plt.legend(loc='lower right')
  plt.title('Training and Validation Accuracy')
  plt.subplot(1, 2, 2)
  plt.plot(epochs_range, loss, label='Training Loss')
  plt.plot(epochs_range, val_loss, label='Validation Loss')
  plt.legend(loc='upper right')
  plt.title('Training and Validation Loss')
  plt.show()

model_location = pathlib.Path(MODEL_FILENAME)
# if model_location.exists():
#   if we don't want to retrain the model, we can load it from disk
#   model = tf.keras.models.load_model(model_filename)
# else:
model = build_model()
convert_model_to_tflite(model)


# Visualize the weights of a specific layer
# layer = model.get_layer(name='dense')  # Replace 'dense' with your layer name
# weights = layer.get_weights()[0]  # Get the weights (without biases)
# # Plot the weights
# plt.hist(weights.flatten(), bins=50)
# plt.xlabel('Weight value')
# plt.ylabel('Frequency')
# plt.title('Weight Distribution of Dense Layer')
# plt.show()
