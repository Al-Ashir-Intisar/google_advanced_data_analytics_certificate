# -*- coding: utf-8 -*-
"""manual_preprocessing_800img_test_ac28_AL

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uVgp9DyQHSyN6OxbqiVbrEbzIJjxEEmV
"""

import os
import zipfile
import shutil
from sklearn.model_selection import train_test_split
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# Model traning, image processing
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, GlobalAveragePooling2D, BatchNormalization, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
import pandas as pd
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder

def extract_and_split(zip_path, output_dir, split_ratio=0.8):
    """
    Extracts a zip file, merges class folders from training and testing, and performs a stratified train-test split.

    Parameters:
        zip_path (str): Path to the archive.zip file.
        output_dir (str): Path to the output directory where the train-test split will be stored.
        split_ratio (float): Proportion of data to use for training (default is 0.8).
    """
    # Temporary extraction path
    temp_dir = os.path.join(output_dir, "temp")

    # Ensure output and temp directories exist
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Extract zip file
    print("Extracting zip file...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Paths to class folders inside the training and testing directories
    class_folders = ['glioma', 'meningioma', 'notumor', 'pituitary']
    dataset_folder = os.path.join(output_dir, "dataset")
    os.makedirs(dataset_folder, exist_ok=True)

    # Merge all class folders from training and testing
    print("Merging training and testing folders...")
    for class_name in class_folders:
        class_dir = os.path.join(dataset_folder, class_name)
        os.makedirs(class_dir, exist_ok=True)
        for base_folder in ['Training', 'Testing']:
            base_path = os.path.join(temp_dir, base_folder, class_name)
            if os.path.exists(base_path):
                for file_name in os.listdir(base_path):
                    src_file = os.path.join(base_path, file_name)
                    dest_file = os.path.join(class_dir, file_name)
                    if os.path.isfile(src_file):
                        shutil.copy(src_file, dest_file)

    # Create train-test split directories
    train_folder = os.path.join(output_dir, "train")
    test_folder = os.path.join(output_dir, "test")
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Perform stratified splitting for each class
    print("Performing stratified train-test split...")
    for class_name in class_folders:
        class_dir = os.path.join(dataset_folder, class_name)
        all_files = os.listdir(class_dir)

        # Stratified train-test split
        train_files, test_files = train_test_split(
            all_files, train_size=split_ratio, random_state=42
        )

        # Copy files to train/test directories for the respective class
        class_train_dir = os.path.join(train_folder, class_name)
        class_test_dir = os.path.join(test_folder, class_name)
        os.makedirs(class_train_dir, exist_ok=True)
        os.makedirs(class_test_dir, exist_ok=True)

        for file_name in train_files:
            shutil.copy(os.path.join(class_dir, file_name), class_train_dir)
        for file_name in test_files:
            shutil.copy(os.path.join(class_dir, file_name), class_test_dir)

    print("Cleaning up temporary files...")
    shutil.rmtree(temp_dir)

    print("Train-test split completed.")

zip_path = "archive.zip"  # Path to your zip file
output_dir = "data"    # Path to the output directory

extract_and_split(zip_path, output_dir)
# if you get a zip file error, it hasn't finished uploading. Wait a few minutes

def get_dataframe(file_dir):
    """
    Creates a pandas DataFrame from the training directory with file paths and labels.

    Parameters:
        train_dir (str): Path to the train directory.

    Returns:
        pd.DataFrame: A DataFrame with columns ['filepath', 'label'].
    """
    data = []
    for class_name in os.listdir(file_dir):
        class_path = os.path.join(file_dir, class_name)
        if os.path.isdir(class_path):  # Check if it's a folder (class directory)
            for file_name in os.listdir(class_path):
                file_path = os.path.join(class_path, file_name)
                if os.path.isfile(file_path):  # Ensure it's a file
                    data.append({"filepath": file_path, "label": class_name})

    # Create a DataFrame
    df = pd.DataFrame(data)
    return df

train_dir = os.path.join("data", "train")  # Path to the train directory
train_df = get_dataframe(train_dir)

test_dir = os.path.join("data", "test")  # Path to the test directory
test_df = get_dataframe(test_dir)

len(train_df)

len(test_df)

# display label counts
train_df['label'].value_counts()

test_df['label'].value_counts()

def view_image_from_dataframe(df, image_column, index):
    """
    Displays an image from a dataframe based on the specified column and index.

    Args:
        df (pd.DataFrame): The dataframe containing image paths.
        image_column (str): The column name containing image file paths.
        index (int): The index of the image to view in the dataframe.

    Returns:
        None
    """
    try:
        # Get the image path from the dataframe
        image_path = df.loc[index, image_column]
        if not os.path.exists(image_path):
            print(f"Image path does not exist: {image_path}")
            return

        # Load and display the image
        img = Image.open(image_path)
        plt.imshow(img)
        plt.axis('off')  # Turn off axis
        plt.title(f"Image at Index {index}")
        plt.show()
    except Exception as e:
        print(f"Error: {e}")

# Example Usage:
# Assuming `df` is a dataframe with a column 'image_path' containing file paths to images
# view_image_from_dataframe(df, 'image_path', 0)  # Displays the image at index 0

view_image_from_dataframe(train_df, 'filepath', 0)

def find_max_dimensions(image_paths):
    max_width = 0
    max_height = 0

    for image_path in image_paths:
        try:
            with Image.open(image_path) as img:
                width, height = img.size  # Get image dimensions
                max_width = max(max_width, width)
                max_height = max(max_height, height)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")

    return max_width, max_height

# Example Usage:
# Assuming `image_files` is a list of image file paths
# max_width, max_height = find_max_dimensions(image_files)
# print(f"Maximum Width: {max_width}, Maximum Height: {max_height}")

max(find_max_dimensions(train_df.iloc[:,0]))

target_size = (1000, 1000)

def parse_function(file_name, label):
    """
    Resize and pad an image to match the target size while maintaining aspect ratio.
    """
    target_size = max(find_max_dimensions(train_df.iloc[:,0])) # update with target size
    target_size = (target_size, target_size)
    image = tf.io.read_file(file_name)
    if image is None:
        raise FileNotFoundError(f"File not found: {file_name}")
    image = tf.image.decode_jpeg(image, channels=1)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize_with_pad(image, 1000, 1000)

    # Normalize pixel values to [0, 1]
    image = image / 255.0

    label = to_categorical(label, 4)

    return image, label

len(train_df)

# Shuffle the DataFrame
train_df = train_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Divide the shuffled DataFrame into chunks of 200 rows each
chunk_size = 100
chunks = [train_df.iloc[i:i + chunk_size] for i in range(0, len(train_df), chunk_size)]

# Check the number of chunks
print(f"Total chunks created: {len(chunks)}")

# Example: Access the first chunk
chunk_1 = chunks[0]
print(chunk_1.head())

len(chunks[56])

def process_chunk(dataset):
    """
    Processes a chunk of the dataset to extract X_train and y_train.

    Parameters:
    - dataset (pd.DataFrame): A DataFrame chunk containing 'filepath' and 'label' columns.

    Returns:
    - X_train (np.ndarray): Array of processed images.
    - y_train (np.ndarray): Array of corresponding labels.
    """
    # Encode labels
    label_encoder = LabelEncoder()
    dataset['label'] = label_encoder.fit_transform(dataset['label'])

    # Parse data and store in arrays
    X_train, y_train = [], []
    for index, row in dataset.iterrows():
        image_path = row['filepath']
        label = row['label']

        # Call the user-defined parse_function to process the image and label
        img, lbl = parse_function(image_path, label)

        X_train.append(img)
        y_train.append(lbl)

    # Convert lists to numpy arrays
    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train

print(target_size)

num_classes = 4
img_rows, img_cols = target_size


model = Sequential([
    Input(shape=(img_rows, img_cols, 1)),  # Input for grayscale images
    # Convolutional Layer 1
    Conv2D(4, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Convolutional Layer 2
    Conv2D(8, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Convolutional Layer 3
    Conv2D(16, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Global Average Pooling (replaces Flatten)
    GlobalAveragePooling2D(),

    # Fully Connected Layers
    Dense(32, activation='relu'),  # Reduce units to manage parameters
    Dropout(0.4),
    Dense(num_classes, activation='softmax')  # Output layer
])

# Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

for i in range(10):
    X_train, y_train = process_chunk(chunks[i])
    history = model.fit(
    X_train,
    y_train,
    epochs=3,
    verbose = 1
)
model.save('brain_tumor_classification_model_img800_by_1000.h5')

#Checking what the history stores after training in multiple chunks
print("accuracy: ", history.history['accuracy'], "\n loss: ", history.history['loss'])

X_train, y_train = process_chunk(chunks[30])

# Train the model with multiple epoch to see the accuracy changes
epochs = 10

model_1 = model
# Train the model using the generator
history = model_1.fit(
    X_train,
    y_train,
    epochs=epochs,
    verbose = 1
)

len(test_df.iloc[:5])

#from tensorflow.keras.models import load_model

# Specify the path to your model file
#model_path = './brain_tumor_classification_model_img800_by_train1000.h5'

# Load the model
#model = load_model(model_path)

# Verify the model has been loaded
#model.summary()

# Shuffle the DataFrame
test_df = test_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Divide the shuffled DataFrame into chunks of 200 rows each
test_chunk_size = 100
test_chunks = [test_df.iloc[i:i + chunk_size] for i in range(0, len(test_df), test_chunk_size)]

# Check the number of chunks
print(f"Total chunks created: {len(test_chunks)}")

# Example: Access the first chunk
test_chunk_1 = test_chunks[0]
print(test_chunk_1.head())

len(test_chunks[14])

# prepaing test_df for evaluating the model
X_test, y_test = process_chunk(test_chunks[0])

test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=1)
print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")

test_loss, test_accuracy = model_1.evaluate(X_test, y_test, verbose=1)
print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")

# Initialize variables for accumulating correct predictions and total samples
total_correct_predictions = 0
total_samples = 0

# Loop through all test_chunks
for chunk in test_chunks:
    # Process the chunk to get X_test and y_test
    X_test, y_test = process_chunk(chunk)

    # Evaluate the model on the current chunk
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=1)

    # Calculate the number of correct predictions for this chunk
    correct_predictions = test_accuracy * len(y_test)

    # Update totals
    total_correct_predictions += correct_predictions
    total_samples += len(y_test)

# Calculate overall accuracy
overall_test_accuracy = total_correct_predictions / total_samples

# Print the combined accuracy
print(f"Combined Test Accuracy: {overall_test_accuracy:.4f}")

# Print the combined accuracy
print(f"Combined Test Accuracy: {overall_test_accuracy:.4f}")