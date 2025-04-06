import cv2
import numpy as np
import dlib
from math import hypot

cap = cv2.VideoCapture(0)
pt = cv2.imread("turban.png", cv2.IMREAD_UNCHANGED)
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


def overlay(face, turban, tlx, tly):
    h, w = turban.shape[:2]
    for i in range(h):
        for j in range(w):
            if tly + i > face.shape[0] or tlx + j > face.shape[1] or tly + i < 0 or tlx + j < 0:
                continue
            alpha = turban[i, j, 3] / 255.0
            for c in range(3):
                face[tly + i, tlx + j, c] = alpha * turban[i, j, c] + (1 - alpha) * face[tly + i, tlx + j, c]
    return face


while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detect(gray_frame)
    for face in faces:
        landmarks = predict(gray_frame, face)
        left = (landmarks.part(1).x, landmarks.part(1).y)
        right = (landmarks.part(15).x, landmarks.part(15).y)
        head_width = int(hypot((left[0] - right[0]), (left[1] - right[1]))) + 100
        aspect_ratio = pt.shape[0] / pt.shape[1]
        head_height = int(head_width * 0.8999)
        turban = cv2.resize(pt, (head_width + 150, head_height))

        center_x = ((left[0] + right[0]) // 2 - (head_width // 2)) - 50
        top_y = (landmarks.part(24).y - int(head_height)) + 100

        if pt.shape[2] == 4:
            frame = overlay(frame, turban, center_x, top_y)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)

        if key == 27:
            break
