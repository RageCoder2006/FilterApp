import os
from dotenv import load_dotenv
import mysql.connector
import tkinter as tk
import datetime
from PIL import Image, ImageTk
import random
import cv2
import dlib
from math import hypot

# ------ DATABASE SETUP ------
load_dotenv("secret.env")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

db = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd=password,
    database="turbantry"
)
crsr = db.cursor()
userprofile = []

# ------ RANDOMSS ------
charlist = list("abcdefghijklmnopqrstuvwxyz0123456789")
splchar = ['!', "@", "#", "$", "%", "&", "*", "-", "_", "+", "?"]


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

    rgb, alpha = overlay_img[:, :, :3], overlay_img[:, :, 3:] / 255.0
    background[y:y + h, x:x + w] = (1 - alpha) * background[y:y + h, x:x + w] + alpha * rgb
    return background


assets_path = 'assets/'


# for prototype's sake only
def generate_shop_items():
    mh_styles = os.listdir(os.path.join(assets_path, 'mh'))
    pj_styles = os.listdir(os.path.join(assets_path, 'pj'))
    rj_styles = os.listdir(os.path.join(assets_path, 'rj'))

    mh_item = random.choice(mh_styles)
    pj_item = random.choice(pj_styles)
    rj_item = random.choice(rj_styles)

    mh_price = random.randint(200, 700)
    pj_price = random.randint(200, 700)
    rj_price = random.randint(200, 700)

    shop_items = [
        {'style': 'mh', 'item': mh_item, 'price': mh_price},
        {'style': 'pj', 'item': pj_item, 'price': pj_price},
        {'style': 'rj', 'item': rj_item, 'price': rj_price}
    ]

    for item in shop_items:
        style_dir = os.path.join(assets_path, item['style'])
        item['image'] = ImageTk.PhotoImage(file=os.path.join(style_dir, item['item']))

    return shop_items


class Turb:
    def __init__(self, state, imdir, options, offsets):
        self.state = state
        self.imdir = imdir
        self.options = options
        self.color = random.choice(self.options)
        self.tpath = os.path.join("assets", self.imdir, f"{self.color}.png")
        self.turbimg = cv2.imread(self.tpath, cv2.IMREAD_UNCHANGED)
        self.offsets = offsets


# --------------- TURBAN OBJECTS ---------------
pj = Turb("Punjab", "pj", ["black", "blue", "green", "orange", "red"],
          {"width_offset": 100, "turban_height_offset": 0,
           "turban_width_offset": 150, "center_x_offset": -50, "top_y_offset": 100})
mh = Turb("Maharashtra", "mh", ["blue", "green", "orange", "pink"],
          {"width_offset": 100, "turban_height_offset": 220,
           "turban_width_offset": 220, "center_x_offset": -50, "top_y_offset": -30})
rj = Turb("Rajasthan", "rj", ["type1", "type2", "type3"],
          {"width_offset": 110, "turban_height_offset": 60,
           "turban_width_offset": 60, "center_x_offset": -30, "top_y_offset": 10})


class TurbanTryApp:
    def __init__(self, root):
        self.selected_turb = mh
        self.root = root
        self.root.title("TurbanTry")
        self.root.geometry("412x917")
        self.root.configure(bg="#2d3651")
        self.bgcolor = "#2d3651"
        self.filtered_frame = None
        self.em = tk.StringVar()
        self.phno = tk.IntVar()
        self.pwd = tk.StringVar()
        self.email = ""
        self.name = ""
        self.loggedin = False
        self.init_images()
        self.home_page()

    def init_images(self):
        self.images = {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for i in range(1, 5):
            path = os.path.join(script_dir, "assets", f"img{i}.png")
            img = Image.open(path).resize((150, 150))
            self.images[f"img{i}"] = ImageTk.PhotoImage(img)
        icon_path = os.path.join(script_dir, "assets", "account_circle.png")
        self.user_icon = ImageTk.PhotoImage(Image.open(icon_path).resize((32, 32)))
        self.navbar_bg = "#ccd6ed"

    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()

    def back_button(self, cleanup=None):
        def on_back():
            if cleanup:
                cleanup()
            self.home_page()

        tk.Button(self.root, text="←", font=("Aptos", 16),
                  command=on_back, bg=self.bgcolor, bd=0).place(x=10, y=10)

    def home_page(self):
        self.clear_window()
        tk.Label(self.root, text="TurbanTry", font=("Aptos", 32, "bold"),
                 fg="#c6b6ad", bg=self.bgcolor).place(x=30, y=20)
        if self.loggedin:
            tk.Button(self.root, image=self.user_icon, bg=self.bgcolor, bd=0, command=self.loggedin_window).place(x=360,
                                                                                                                  y=20)
        else:
            tk.Button(self.root, image=self.user_icon, bg=self.bgcolor, bd=0, command=self.user_page).place(x=360, y=20)

        tk.Label(self.root, text="Learn About", font=("Aptos", 18),
                 bg=self.bgcolor).place(x=160, y=90)

        items = [
            ("Dastar/Dumalla\n(Punjab)", self.images["img1"], self.info_pj),
            ("Pagri\n(Rajasthan)", self.images["img2"], self.info_rj),
            ("Pheta\n(Maharashtra)", self.images["img3"], self.info_mh),
            ("Other Indian\nTurbans", self.images["img4"], self.info_misc),
        ]
        xs = [30, 220, 30, 220];
        ys = [150, 150, 350, 350]
        for i, (text, img, cmd) in enumerate(items):
            tk.Button(self.root, image=img, bg=self.bgcolor,
                      bd=0, command=cmd).place(x=xs[i], y=ys[i])
            tk.Label(self.root, text=text, font=("Aptos", 10, "bold"),
                     bg=self.bgcolor).place(x=xs[i] + 40, y=ys[i] + 160)

        tk.Frame(self.root, height=60, width=412, bg=self.navbar_bg).place(x=0, y=700)
        tk.Button(self.root, text="Try", font=("Aptos", 10),
                  command=self.try_page, bg=self.navbar_bg, bd=0, highlightbackground=self.navbar_bg).place(x=60, y=717)
        tk.Button(self.root, text="Home", font=("Aptos", 10, "bold"),
                  bg=self.navbar_bg, bd=0, highlightbackground=self.navbar_bg).place(x=180, y=717)
        tk.Button(self.root, text="Shop", font=("Aptos", 10),
                  command=self.shop_page, bg=self.navbar_bg, bd=0, highlightbackground=self.navbar_bg).place(x=300,
                                                                                                             y=717)

    def generate_uid(self):
        return ''.join(random.choices(charlist, k=5))

    def signup_window(self):
        self.clear_window()
        self.back_button()

        tk.Label(self.root, text="Name", font=("Aptos", 15, "bold"), background=self.bgcolor).place(x=80, y=100)
        name_entry = tk.Entry(self.root, bg="#ccd6ed", fg="black")
        name_entry.place(x=80, y=130)

        tk.Label(self.root, text="Email", font=("Aptos", 15, "bold"), background=self.bgcolor).place(x=80, y=160)
        email_entry = tk.Entry(self.root, bg="#ccd6ed", fg="black")
        email_entry.place(x=80, y=180)

        tk.Label(self.root, text="Password", font=("Aptos", 15, "bold"), background=self.bgcolor).place(x=80, y=210)
        pwd_entry = tk.Entry(self.root, show="*", bg="#ccd6ed", fg="black")
        pwd_entry.place(x=80, y=240)

        tk.Label(self.root, text="Phone Number (Optional)", font=("Aptos", 15, "bold"), background=self.bgcolor).place(
            x=80, y=270)
        phno_entry = tk.Entry(self.root, bg="#ccd6ed", fg="black")
        phno_entry.place(x=80, y=300)

        def register_user():
            name = name_entry.get()
            self.name = name
            email = email_entry.get()
            self.email = email
            pwd = pwd_entry.get()
            phno = phno_entry.get()
            self.phno = phno

            if not name or not email or not pwd:
                tk.Label(self.root, text="Please fill all required fields").pack()
                return

            uid = self.generate_uid()

            try:
                if phno.strip() == "":
                    query = "INSERT INTO users (uid, name, email, pwd, purchase_count) VALUES (%s, %s, %s, %s, %s)"
                    crsr.execute(query, (uid, name, email, pwd, 0))
                else:
                    query = "INSERT INTO users (uid, name, email, pwd, phno, purchase_count) VALUES (%s, %s, %s, %s, %s, %s)"
                    crsr.execute(query, (uid, name, email, pwd, int(phno), 0))
                db.commit()
                self.loggedin = True
                tk.Label(self.root, text="Registered successfully!").place(x=80, y=380)
            except mysql.connector.Error as err:
                tk.Label(self.root, text=f"Error: {err}").place(x=80, y=400)

        tk.Button(self.root, text="Register", command=register_user, bd=0, highlightbackground=self.bgcolor).place(
            x=145, y=340)

    def login(self):
        email = self.em.get()
        pwd = self.pwd.get()
        crsr.execute("SELECT * FROM users WHERE email=%s AND pwd=%s", (email, pwd))
        entry = crsr.fetchone()
        if entry:
            self.name = entry[1]
            self.email = self.em.get()
            self.phno = entry[4]
            self.loggedin_window()
            self.loggedin = True
        else:
            tk.Label(self.root, text="Incorrect Credentials!", font=("Aptos", 15, "bold"),
                     background=self.bgcolor).place(x=80, y=290)

    def loginpage(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Email:", font=("Aptos", 15, "bold"), background=self.bgcolor).place(x=80, y=130)
        tk.Entry(self.root, textvariable=self.em, bg="#ccd6ed", fg="black").place(x=80, y=160)
        tk.Label(self.root, text="Password:", font=("Aptos", 15, "bold"), background=self.bgcolor).place(x=80, y=190)
        tk.Entry(self.root, textvariable=self.pwd, show="*", bg="#ccd6ed", fg="black").place(x=80, y=220)
        tk.Button(self.root, text="Login", command=self.login, highlightbackground=self.bgcolor).place(x=150, y=260)

    def loggedin_window(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Welcome " + self.name, font=("Aptos", 15), background=self.bgcolor).place(x=20, y=120)
        tk.Label(self.root, text=f"Email: {self.em}", font=("Aptos", 15), background=self.bgcolor).place(x=20, y=160)
        tk.Label(self.root, text=f"Phone No.: {self.phno}", font=("Aptos", 15), background=self.bgcolor).place(x=20,
                                                                                                               y=190)
        tk.Button(self.root, text="Logout", command=self.logout_user, highlightbackground=self.bgcolor).place(x=150,
                                                                                                              y=260)

    def logout_user(self):
        self.loggedin = False
        self.clear_window()
        self.home_page()

    def user_page(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Hello, user!",
                 font=("Aptos", 16), bg=self.bgcolor).pack(pady=100)
        tk.Button(self.root, text="Login", command=self.loginpage, highlightbackground=self.bgcolor).place(x=170, y=200)
        tk.Button(self.root, text="Sign Up", command=self.signup_window, highlightbackground=self.bgcolor).place(
            x=162.5,
            y=300)

    def pjbt(self):
        self.selected_turb = pj
        new = random.choice(pj.options)
        pj.color = new
        pj.tpath = f"assets/{pj.imdir}/{new}.png"
        pj.turbimg = cv2.imread(pj.tpath, cv2.IMREAD_UNCHANGED)

    def mhbt(self):
        self.selected_turb = mh
        new = random.choice(mh.options)
        mh.color = new
        mh.tpath = f"assets/{mh.imdir}/{new}.png"
        mh.turbimg = cv2.imread(mh.tpath, cv2.IMREAD_UNCHANGED)

    def rjbt(self):
        self.selected_turb = rj
        new = random.choice(rj.options)
        rj.color = new
        rj.tpath = f"assets/{rj.imdir}/{new}.png"
        rj.turbimg = cv2.imread(rj.tpath, cv2.IMREAD_UNCHANGED)

    def capture(self):
        ret, _ = self.cap.read()
        if ret and self.filtered_frame is not None:
            fn = f"captured/capture_{datetime.datetime.now():%Y%m%d_%H%M%S}.jpg"
            cv2.imwrite(fn, self.filtered_frame)
            tk.Label(self.root, text="File saved successfully!", bg=self.bgcolor).place(x=120, y=40)

    def try_page(self):
        self.clear_window()
        tk.Button(self.root, text="Punjab", command=self.pjbt, highlightbackground=self.bgcolor).place(x=20, y=600)
        tk.Button(self.root, text="Maharashtra", command=self.mhbt, highlightbackground=self.bgcolor).place(x=145,
                                                                                                            y=600)
        tk.Button(self.root, text="Rajasthan", command=self.rjbt, highlightbackground=self.bgcolor).place(x=300, y=600)

        def cleanup_camera():
            self.cap.release();
            cv2.destroyAllWindows()

        self.back_button(cleanup=cleanup_camera)
        self.video_label = tk.Label(self.root)
        self.video_label.place(x=7, y=197, width=400, height=300)

        self.cap = cv2.VideoCapture(0)
        self.detect = dlib.get_frontal_face_detector()
        spath = os.path.join("assets", "shape_predictor_68_face_landmarks.dat")
        self.predict = dlib.shape_predictor(spath)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(30, self.update_frame)
            return

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detect(gray)

        for f in faces:
            l = self.predict(gray, f)
            left = (l.part(1).x, l.part(1).y)
            right = (l.part(15).x, l.part(15).y)

            w = int(hypot(right[0] - left[0], right[1] - left[1])) + self.selected_turb.offsets["width_offset"]
            h = int(w * 0.8999)
            turban = cv2.resize(
                self.selected_turb.turbimg,
                (w + self.selected_turb.offsets["turban_width_offset"],
                 h + self.selected_turb.offsets["turban_height_offset"])
            )
            cx = ((left[0] + right[0]) // 2 - (w // 2)) + self.selected_turb.offsets["center_x_offset"]
            ty = (l.part(24).y - h) + self.selected_turb.offsets["top_y_offset"]

            if turban.shape[2] == 4:
                frame = overlay(frame, turban, cx, ty)

        self.filtered_frame = frame.copy()
        disp = cv2.resize(frame, (400, 300))
        rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        if not hasattr(self, 'capture_btn'):
            tk.Button(self.root, text="Capture", command=self.capture, highlightbackground=self.bgcolor).place(x=155,
                                                                                                               y=520)
            self.capture_btn = True

        self.root.after(30, self.update_frame)

    def shop_page(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Shop Page", font=("Aptos", 16), bg=self.bgcolor).pack()
        if self.loggedin:
            shop_items = generate_shop_items()
            y_position = 100

            for item in shop_items:
                label = tk.Label(self.root, text=f"Turban Style: {item['style']} | Price: ₹{item['price']}",
                                 bg=self.bgcolor)
                label.place(x=10, y=y_position)

                image_label = tk.Label(self.root, image=item['image'], bg=self.bgcolor)
                image_label.place(x=150, y=y_position)

                purchase_button = tk.Button(self.root, text="Buy", command=self.purchase, bg=self.bgcolor)
                purchase_button.place(x=300, y=y_position)

                y_position += 100
        else:
            tk.Label(self.root, text="Login or Signup First", font=("Aptos", 16), bg=self.bgcolor).pack()

    def purchase(self):
        label = tk.Label(self.root, text="Purchased Successfully", font=("Aptos", 15), bg=self.bgcolor)
        label.pack()
        self.root.after(500, label.destroy)

    def info_pj(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Pagg Info Page", font=("Aptos", 16), bg=self.bgcolor).pack(pady=100)
        desc_punjab = (
            "Punjabi turbans, or \"Pagg,\" are emblematic of Sikh identity and cultural pride. "
            "Styles like Patiala Shahi, Amritsar Shahi, Nok Pagg, and Morni reflect regional and personal expression. "
            "Colors hold significance—saffron for courage, blue for spirituality, and white for peace. "
            "Traditionally tied daily, turbans represent honor and dignity, with modern versions embracing both tradition and style."
        )
        tk.Label(self.root, text=desc_punjab, wraplength=380, justify="left",
                 font=("Aptos", 18), bg=self.bgcolor).pack(padx=20, pady=10)

    def info_rj(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Pagri Info Page", font=("Aptos", 16), bg=self.bgcolor).pack(pady=100)
        desc_rajasthan = (
            "In Rajasthan, the Pagri or Safa is more than just headgear; it's a symbol of identity, status, and regional pride. "
            "These turbans vary in style, color, and size, often indicating the wearer's community, occasion, or region. "
            "The Jodhpuri Safa is known for its elegance. "
            "Turban lengths range from 8 to 20 meters, and they serve practical purposes—from sun protection to drawing water."
        )
        tk.Label(self.root, text=desc_rajasthan, wraplength=380, justify="left",
                 font=("Aptos", 18), bg=self.bgcolor).pack(padx=20, pady=10)

    def info_mh(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Pheta Info Page", font=("Aptos", 16), bg=self.bgcolor).pack(pady=100)
        desc_maharashtra = (
            "The Pheta is a traditional turban from Maharashtra, symbolizing pride and honor. "
            "Typically made of cotton, it measures about 3.5 to 6 meters in length and 1 meter in width. "
            "Commonly worn during weddings, festivals, and religious ceremonies, the Pheta comes in various styles like the Kolhapuri and Puneri. "
            "Colors such as saffron signify valor, while white represents peace."
        )
        tk.Label(self.root, text=desc_maharashtra, wraplength=380, justify="left",
                 font=("Aptos", 18), bg=self.bgcolor).pack(padx=20, pady=10)

    def info_misc(self):
        self.clear_window()
        self.back_button()
        tk.Label(self.root, text="Other Indian Turbans Info Page",
                 font=("Aptos", 16), bg=self.bgcolor).pack(pady=100)
        desc_others = (
            "Across India, turbans are part of daily life for many communities. "
            "Farmers wear large, loose turbans for sun and dust protection. "
            "In Rajasthan, shepherds wear pink turbans, while farmers use different colors for community identity. "
            "Railway porters, or coolies, traditionally wear white turbans with red shirts to stand out in crowded stations."
        )
        tk.Label(self.root, text=desc_others, wraplength=380, justify="left",
                 font=("Aptos", 18), bg=self.bgcolor).pack(padx=20, pady=10)


if __name__ == '__main__':
    root = tk.Tk()
    app = TurbanTryApp(root)
    root.mainloop()
