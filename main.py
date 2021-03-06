import cv2
import numpy as np
from tensorflow.keras.models import load_model

def init():
    """
    Loading the classifier, model and initializing the attributes vector
    """
    global face_cascade
    global model
    global attributes

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    model = load_model('model.hdf5')

    attributes = np.array(['5_o_Clock_Shadow', 'Arched_Eyebrows', 'Bags_Under_Eyes',
                           'Bald', 'Bangs', 'Big_Lips', 'Big_Nose', 'Black_Hair', 'Blond_Hair',
                           'Brown_Hair', 'Bushy_Eyebrows', 'Chubby', 'Double_Chin', 'Eyeglasses',
                           'Goatee', 'Gray_Hair', 'Heavy_Makeup', 'High_Cheekbones', 'Male',
                           'Mouth_Slightly_Open', 'Mustache', 'Narrow_Eyes', 'No_Beard', 'Oval_Face',
                           'Pointy_Nose', 'Receding_Hairline', 'Rosy_Cheeks', 'Sideburns',
                           'Smiling', 'Straight_Hair', 'Wavy_Hair', 'Wearing_Earrings', 'Wearing_Hat',
                           'Wearing_Lipstick', 'Wearing_Necklace', 'Wearing_Necktie', 'Young'])


def detect_faces(image):
    """
    Face detection using the cascade classifier
    """
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img, 1.2, 6, minSize=(50, 50))

    return faces


def crop_face(image, pos):
    """
    Cropping the face from the image
    
    exp_val - values responsible for expanding the face, can be changed
    """
    (x, y, w, h) = pos
    W, H, _ = image.shape

    x1, x2 = (max(0, x - int(w * 0.35)), min(x + int(1.35 * w), W))
    y1, y2 = (max(0, y - int(0.35 * h)), min(y + int(1.35 * h), H))
    
    
    return image[y1:y2, x1:x2]  # returning the expanded face


def preprocess_face(image):
    """
    Preprocessing the face in the way that's suitable for the model
    """
    prep_face = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # opencv stores images in BGR format
    prep_face = cv2.resize(image, (224, 224))
    prep_face = prep_face/255
    prep_face = prep_face.reshape(-1, 224, 224, 3)

    return prep_face


def contour_face(image, face):
    """
    Drawing a rectangle around the face
    """
    (x, y, w, h) = face
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)


def describe_face(image, face, level):
    """
    Write attributes next to the face
    """
    (x, y, w, _) = face
    text = str(level+1)
    cv2.putText(image, text, (int(x+w/2 - 30), y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)


def print_attributes(image, level, attrib):
    #  TODO
    text = f"{level+1}: "
    for x in range(0, len(attrib),5):
        text += ' '.join(attrib[x:x+5])
        text += "\n"
    for i, line in enumerate(text.split('\n')):
        cv2.putText(image, line, (5, int((image.shape[0]/6)*(level+1))+i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


def make_prediction(face):
    """
    Making attributes prediction for a face
    Return: a list/array of attributes
    """
    pred = model.predict(face).reshape(-1)
    mask = pred >= 0.5  # creating a boolean mask for attributes, the threshold can be changed
    face_attributes = attributes[mask]
    if 'Male' not in face_attributes: face_attributes = np.append(face_attributes, 'Female')
    if 'No_Beard' not in face_attributes: face_attributes = np.append(face_attributes, 'Beard')
    if 'Young' not in face_attributes: face_attributes = np.append(face_attributes, 'Old')

    return face_attributes


def main():
    cam = cv2.VideoCapture(0)
    while True:
        _, img = cam.read()
        img2 = np.zeros((int(img.shape[0]/2), int(img.shape[1]), 3), np.uint8)
        faces = detect_faces(img)

        for idx, face_pos in enumerate(faces):
            cropped_face = crop_face(img, face_pos)
            prep_face = preprocess_face(cropped_face)
            prediction = make_prediction(prep_face)
            contour_face(img, face_pos)
            describe_face(img, face_pos, idx)
            print_attributes(img2, idx, prediction)

        img_v = cv2.vconcat([img, img2])
        cv2.imshow('img', img_v)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cv2.destroyAllWindows()


def predict_from_photo(img_name):
    img = cv2.imread(img_name)
    faces = detect_faces(img)
    img2 = np.zeros((int(img.shape[0]/2), int(img.shape[1]), 3), np.uint8)
    for idx, face_pos in enumerate(faces):
        cropped_face = crop_face(img, face_pos)
        prep_face = preprocess_face(cropped_face)
        prediction = make_prediction(prep_face)
        contour_face(img, face_pos)
        describe_face(img, face_pos, idx)
        print_attributes(img2, idx, prediction)

    img_v = cv2.vconcat([img, img2])
    cv2.imshow('img', img_v)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    init()
    # main()
    predict_from_photo('sample_images/02.png')