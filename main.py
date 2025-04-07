import cv2
import numpy as np
import random
import dlib
from math import hypot

pjt = ["black", "blue", "green", "orange", "red"]
pturb = pjt[random.randint(0, len(pjt) - 1)]

cap = cv2.VideoCapture(0)
pt = cv2.imread(f"pj/{pturb}.png", cv2.IMREAD_UNCHANGED)
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


def overlay(background, overlay_img, x, y):
    h, w = overlay_img.shape[:2]

    if x < 0:
        overlay_img = overlay_img[:, -x:]
        w = overlay_img.shape[1]
        x = 0
    if y < 0:
        overlay_img = overlay_img[-y:, :]
        h = overlay_img.shape[0]
        y = 0
    if y + h > background.shape[0]:
        h = background.shape[0] - y
        overlay_img = overlay_img[:h]
    if x + w > background.shape[1]:
        w = background.shape[1] - x
        overlay_img = overlay_img[:, :w]

    overlay_rgb = overlay_img[:, :, :3]
    alpha_mask = overlay_img[:, :, 3:] / 255.0
    background[y:y+h, x:x+w] = (1 - alpha_mask) * background[y:y+h, x:x+w] + alpha_mask * overlay_rgb
    return background


def filt():
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect(gray)

        for face in faces:
            landmarks = predict(gray, face)
            left = (landmarks.part(1).x, landmarks.part(1).y)
            right = (landmarks.part(15).x, landmarks.part(15).y)

            width = int(hypot(right[0] - left[0], right[1] - left[1])) + 100
            height = int(width * 0.8999)
            turban = cv2.resize(pt, (width + 150, height))

            center_x = ((left[0] + right[0]) // 2 - (width // 2)) - 50
            top_y = (landmarks.part(24).y - height) + 100

            if pt.shape[2] == 4:
                frame = overlay(frame, turban, center_x, top_y)

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

filt()
