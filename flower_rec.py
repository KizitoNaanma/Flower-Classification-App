# import matplotlib.pyplot as plt
import os
import tensorflow as tf
import PIL
import numpy as np

import pickle

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import tensorflow_datasets as tfds
import pathlib

dataset_root = os.path.abspath('./'+'flower_photos.tgz')

data_dir = tf.keras.utils.get_file("flower_photos", origin = 'file://'+dataset_root, untar=True)

data_dir = pathlib.Path(data_dir)
image_count = len(list(data_dir.glob('*/*.jpg')))

# roses = list(data_dir.glob('roses/*'))
# PIL.Image.open(str(roses[1]))

batch_size = 32
img_height = 180
img_width = 180

train_ds = tf.keras.preprocessing.image_dataset_from_directory(data_dir,validation_split=0.2, subset="training", seed=123, image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(data_dir,validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_name = train_ds.class_names

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixels values are now in `[0,1]`.
# print(np.min(first_image), np.max(first_image))

# def create_model():
#     num_classes = 5
#     model = Sequential([
#             layers.experimental.preprocessing.Rescaling(1./255, input_shape=(img_height, img_width,3)),
#             layers.Conv2D(16, 3, padding='same', activation='relu'),
#             layers.MaxPooling2D(),
#             layers.Conv2D(32, 3, padding='same', activation='relu'),
#             layers.MaxPooling2D(),
#             layers.Conv2D(64, 3, padding='same', activation='relu'),
#             layers.MaxPooling2D(),
#             layers.Flatten(),
#             layers.Dense(128, activation='relu'),
#             layers.Dense(num_classes)
#     ])
#
#     model.compile(optimizer='adam',
#                 loss = tf.losses.SparseCategoricalCrossentropy(from+from_logits=True),
#                 metrics=['accuracy'])
#
#     return model
#
# model = create_model()


num_classes = 5

model = Sequential([
  layers.experimental.preprocessing.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

epochs=10
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)


data_augmentation = keras.Sequential(
  [
    layers.experimental.preprocessing.RandomFlip("horizontal_and_vertical", input_shape=(img_height,img_width,3)),
    layers.experimental.preprocessing.RandomRotation(0.1),
    layers.experimental.preprocessing.RandomZoom(0.1),
  ]
)

model = Sequential([
  data_augmentation,
  layers.experimental.preprocessing.Rescaling(1./255),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.2),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])


model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

checkpoint_path = "training_1/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1)
                                                 
epochs = 15
model.fit(train_ds, validation_data=val_ds, epochs=epochs)
print("Augmented Model Fitting Complete")



def img_pred(image_url):

    image_path = tf.keras.utils.get_file('IMG', origin=image_url)
    img = keras.preprocessing.image.load_img(
        image_path, target_size=(img_height, img_width)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    text = 'This image most likely belongs to {} with a {:.2f} percent confidence.'.format(class_name[np.argmax(score)], 100 * np.max(score))

    return text




with open('model.pkl', 'wb') as f:
  pickle.dump(model, f)
