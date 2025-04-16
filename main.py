import tkinter as tk
import datetime
from PIL import Image, ImageTk
import random
import cv2
import dlib
from math import hypot


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


class Turb:
    def __init__(self, state, imdir, options, offsets):
        self.state = state
        self.imdir = imdir
        self.options = options
        self.color = options[random.randint(0, len(options) - 1)]
        self.tpath = f"assets/{self.imdir}/{self.color}.png"
        self.turbimg = cv2.imread(self.tpath, cv2.IMREAD_UNCHANGED)
        self.offsets = offsets


class TurbanTryApp:
    def __init__(self, root):
        self.selected_turb = mh
        self.root = root
        self.root.title("TurbanTry")
        self.root.geometry("412x917")
        self.root.configure(bg="#CFB58A")
        self.filtered_frame = None
        self.init_images()
        self.home_page()

    def init_images(self):
        self.images = {}
        for i in range(1, 5):
            img = Image.open(f"assets/img{i}.png").resize((150, 150))
            self.images[f"img{i}"] = ImageTk.PhotoImage(img)
        self.user_icon = ImageTk.PhotoImage(Image.open("assets/account_circle.png").resize((32, 32)))
        self.navbar_bg = "#E5E5E5"

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def back_button(self, cleanup=None):
        def on_back():
            if cleanup:
                cleanup()
            self.home_page()

        back_btn = tk.Button(self.root, text="←", font=("Helvetica", 16), command=on_back, bg="#CFB58A", bd=0)
        back_btn.place(x=10, y=10)

    def home_page(self):
        self.clear_window()

        tk.Label(self.root, text="TurbanTry", font=("Helvetica", 32, "bold"), fg="#01416F", bg="#CFB58A").place(x=30, y=20)
        tk.Button(self.root, image=self.user_icon, background="#CFB58A", bd=0, command=self.user_page).place(x=360, y=20)

        tk.Label(self.root, text="Learn About", font=("Helvetica", 18), bg="#CFB58A").place(x=160, y=90)

        items = [
            ("Dastar/Dumalla\n(Punjab)", self.images["img1"], self.info_pj),
            ("Pagri\n(Rajasthan)", self.images["img2"], self.info_rj),
            ("Pheta\n(Maharashtra)", self.images["img3"], self.info_mh),
            ("Other Indian\nTurbans", self.images["img4"], self.info_misc),
        ]
        x_coords = [30, 220, 30, 220]
        y_coords = [150, 150, 350, 350]

        for i in range(4):
            btn = tk.Button(self.root, image=items[i][1], bg="#CFB58A", bd=0, command=items[i][2])
            btn.place(x=x_coords[i], y=y_coords[i])
            tk.Label(self.root, text=items[i][0], font=("Helvetica", 10, "bold"), bg="#CFB58A").place(
                x=x_coords[i] + 40, y=y_coords[i] + 160)

        tk.Frame(self.root, height=60, width=412, bg=self.navbar_bg).place(x=0, y=700)
        tk.Button(self.root, text="Try", font=("Helvetica", 10), command=self.try_page, bg=self.navbar_bg, bd=0).place(x=60, y=717)
        tk.Button(self.root, text="Home", font=("Helvetica", 10, "bold"), bg=self.navbar_bg, bd=0).place(x=180, y=717)
        tk.Button(self.root, text="Shop", font=("Helvetica", 10), command=self.shop_page, bg=self.navbar_bg, bd=0).place(x=300, y=717)

    def user_page(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Hello, user!", font=("Helvetica", 16), bg="#CFB58A").pack(pady=100)

    def pjbt(self):
        self.selected_turb = pj
        new_color = pj.options[random.randint(0, len(pj.options) - 1)]
        pj.color = new_color
        pj.tpath = f"assets/{pj.imdir}/{new_color}.png"
        pj.turbimg = cv2.imread(pj.tpath, cv2.IMREAD_UNCHANGED)

    def mhbt(self):
        self.selected_turb = mh
        new_color = mh.options[random.randint(0, len(mh.options) - 1)]
        mh.color = new_color
        mh.tpath = f"assets/{mh.imdir}/{new_color}.png"
        mh.turbimg = cv2.imread(mh.tpath, cv2.IMREAD_UNCHANGED)

    def rjbt(self):
        self.selected_turb = rj
        new_color = rj.options[random.randint(0, len(rj.options) - 1)]
        rj.color = new_color
        rj.tpath = f"assets/{rj.imdir}/{new_color}.png"
        rj.turbimg = cv2.imread(rj.tpath, cv2.IMREAD_UNCHANGED)

    def capture(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        if ret:
            filename = f"captured/capture_{datetime.datetime.now()}.jpg"
            cv2.imwrite(filename, self.filtered_frame)
            saved = tk.Label(self.root, text="file saved successfully!", bg="#CFB58A")
            saved.place(x=120,y=40)

    def try_page(self):
        self.clear_window()
        self.pjbtn = tk.Button(self.root,text="Punjab",command=self.pjbt)
        self.pjbtn.place(x=20,y=600)
        self.mhbtn = tk.Button(self.root,text="Maharashtra",command=self.mhbt)
        self.mhbtn.place(x=140,y=600)
        self.rjbtn = tk.Button(self.root,text="Rajasthan",command=self.rjbt)
        self.rjbtn.place(x=300,y=600)

        def cleanup_camera():
            self.cap.release()
            cv2.destroyAllWindows()

        self.back_button(cleanup=cleanup_camera)

        self.video_label = tk.Label(self.root)
        self.video_label.place(x=7, y=197, width=400, height=300)

        self.cap = cv2.VideoCapture(0)
        self.detect = dlib.get_frontal_face_detector()
        self.predict = dlib.shape_predictor("assets/shape_predictor_68_face_landmarks.dat")

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detect(gray)

        for face in faces:
            landmarks = self.predict(gray, face)
            left = (landmarks.part(1).x, landmarks.part(1).y)
            right = (landmarks.part(15).x, landmarks.part(15).y)

            width = int(hypot(right[0] - left[0], right[1] - left[1])) + self.selected_turb.offsets["width_offset"]
            height = int(width * 0.8999)
            turban = cv2.resize(
                self.selected_turb.turbimg,
                (width + self.selected_turb.offsets["turban_width_offset"],
                 height + self.selected_turb.offsets["turban_height_offset"])
            )

            center_x = ((left[0] + right[0]) // 2 - (width // 2)) + self.selected_turb.offsets["center_x_offset"]
            top_y = (landmarks.part(24).y - height) + self.selected_turb.offsets["top_y_offset"]

            if self.selected_turb.turbimg.shape[2] == 4:
                frame = overlay(frame, turban, center_x, top_y)

        self.filtered_frame = frame.copy()
        frame = cv2.resize(frame, (400, 300))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        self.root.after(30, self.update_frame)
        self.capture_btn = tk.Button(self.root, text="Capture", command=self.capture)
        self.capture_btn.place(x=150, y=520)

    def shop_page(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Shop Page", font=("Helvetica", 16), bg="#CFB58A").pack(pady=100)

    def info_pj(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Pagg Info Page", font=("Helvetica", 16), bg="#CFB58A").pack(pady=100)
        desc = (
            "Punjabi turbans, or \"Pagg,\" are a symbol of Sikh identity, spirituality, and cultural pride. "
            "Styles like Patiala Shahi, Amritsar Shahi, Nok Pagg, and Morni reflect regional and personal expression. "
            "Colors hold meaning—saffron for courage, blue for spirituality, and white for peace. Traditionally tied daily, "
            "turbans represent honor and dignity, with modern versions embracing both tradition and style."
        )
        tk.Label(self.root, text=desc, wraplength=380, justify="left", font=("Helvetica", 18), bg="#CFB58A").pack(padx=20, pady=10)

    def info_rj(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Pagri Info Page", font=("Helvetica", 16), bg="#CFB58A").pack(pady=100)

    def info_mh(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Pheta Info Page", font=("Helvetica", 16), bg="#CFB58A").pack(pady=100)

    def info_misc(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Other Indian Turbans Info Page", font=("Helvetica", 16), bg="#CFB58A").pack(pady=100)


# Define your turbans
pj = Turb("Punjab", "pj", ["black", "blue", "green", "orange", "red"],
          {"width_offset": 100, "turban_height_offset": 0, "turban_width_offset": 150, "center_x_offset": -50, "top_y_offset": 100})
mh = Turb("Maharashtra", "mh", ["blue", "green", "orange", "pink"],
          {"width_offset": 100, "turban_height_offset": 220, "turban_width_offset": 220, "center_x_offset": -50, "top_y_offset": -30})
rj = Turb("Rajasthan", "rj", ["type1", "type2", "type3"],
          {"width_offset": 110, "turban_height_offset":60, "turban_width_offset": 60, "center_x_offset": -30,
           "top_y_offset": 10})

if __name__ == '__main__':
    root = tk.Tk()
    app = TurbanTryApp(root)
    root.mainloop()
