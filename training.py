import os
import numpy as np
from PIL import Image
import cv2

def train_classifier(data_dir):
    path = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
    faces = []
    ids = []
    for image in path:
        img = Image.open(image).convert('L')
        imageNP = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])  # Convert id to integer

        faces.append(imageNP)
        ids.append(id)
    ids = np.array(ids)

    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("classifier.xml")
    print("Dataset Model Training Completed ")


