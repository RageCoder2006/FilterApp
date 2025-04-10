import random
import cv2
import dlib
from math import hypot


class Turb:
    def __init__(self, state, imdir, options, offsets):
        self.state = state
        self.imdir = imdir
        self.options = options
        self.color = options[random.randint(0, len(self.options) - 1)]
        self.tpath = f"{self.imdir}/{self.color}.png"
        self.turbimg = cv2.imread(self.tpath, cv2.IMREAD_UNCHANGED)
        self.offsets = offsets


pj = Turb("Punjab", "pj", ["black", "blue", "green", "orange", "red"],
          {"width_offset": 100, "turban_height_offset": 0, "turban_width_offset": 150, "center_x_offset": -50,
           "top_y_offset": 100})
mh = Turb("Maharashtra", "mh", ["blue", "green", "orange", "pink"],
          {"width_offset": 100, "turban_height_offset": 220, "turban_width_offset": 220, "center_x_offset": -50,
           "top_y_offset": -30})
rj = ("Rajasthan", "rj", [])
misc = ("", "misc", [])

cap = cv2.VideoCapture(0)
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
    background[y:y + h, x:x + w] = (1 - alpha_mask) * background[y:y + h, x:x + w] + alpha_mask * overlay_rgb
    return background


def filt(turbIMG, offset):
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect(gray)

        for face in faces:
            landmarks = predict(gray, face)
            left = (landmarks.part(1).x, landmarks.part(1).y)
            right = (landmarks.part(15).x, landmarks.part(15).y)

            width = int(hypot(right[0] - left[0], right[1] - left[1])) + offset.get("width_offset")
            height = int(width * 0.8999)
            turban = cv2.resize(turbIMG, (
            width + offset.get("turban_width_offset"), height + offset.get("turban_height_offset")))

            center_x = ((left[0] + right[0]) // 2 - (width // 2)) + offset.get("center_x_offset")
            top_y = (landmarks.part(24).y - height) + offset.get("top_y_offset")

            if turbIMG.shape[2] == 4:
                frame = overlay(frame, turban, center_x, top_y)

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


filt(mh.turbimg, mh.offsets)
