import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection
from utils import clear_frame
from admin_dashboard import open_admin_dashboard
from user_dashboard import open_user_dashboard
from PIL import Image, ImageTk

# Color and font constants
PRIMARY_BLUE = "#1F1B4F"
LIGHT_BLUE = "#888096"
ACCENT_YELLOW = "#F9BF3B"
WHITE = "#ffffff"
FONT = ("Segoe UI", 12)
HEADER_FONT = ("Segoe UI", 16, "bold")


def style_widgets(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview",
                    background=WHITE,
                    foreground="#222",
                    rowheight=28,
                    fieldbackground=WHITE,
                    font=FONT)
    style.configure("Treeview.Heading",
                    font=FONT,
                    background=PRIMARY_BLUE,
                    foreground=WHITE)
    style.map("Treeview", background=[('selected', PRIMARY_BLUE)])
    style.configure("Accent.TButton",
                    background=ACCENT_YELLOW,
                    foreground="#1e293b",
                    font=FONT)
    style.configure("Primary.TButton",
                    background=PRIMARY_BLUE,
                    foreground=WHITE,
                    font=FONT)
    style.map("Accent.TButton",
              background=[('active', "#facc15"), ('!active', ACCENT_YELLOW)])
    style.map("Primary.TButton",
              background=[('active', "#1d4ed8"), ('!active', PRIMARY_BLUE)])


def show_login(root, frame):
    clear_frame(frame)
    style_widgets(root)
    root.geometry("430x500")
    root.resizable(False, False)

    # Background image
    image = Image.open("asset/dogdog.jpg")
    image = image.resize((430, 500), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(image)

    canvas = tk.Canvas(frame, width=430, height=500, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_image)
    canvas.bg_image = bg_image  # prevent garbage collection

    # Input widgets
    title_label = tk.Label(frame, text="Login", font=HEADER_FONT, bg="#20141c", fg=ACCENT_YELLOW)
    user_label = tk.Label(frame, text="Username:", font=FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE)
    username_entry = tk.Entry(frame, font=FONT)

    pass_label = tk.Label(frame, text="Password:", font=FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE)
    password_entry = tk.Entry(frame, show="*", font=FONT)

    login_btn = ttk.Button(frame, text="Login", style="Accent.TButton", width=12)
    register_btn = ttk.Button(frame, text="Register", style="Primary.TButton", width=12)

    # Place widgets
    canvas.create_window(215, 60, window=title_label)
    canvas.create_window(215, 120, window=user_label)
    canvas.create_window(215, 150, window=username_entry)
    canvas.create_window(215, 200, window=pass_label)
    canvas.create_window(215, 230, window=password_entry)
    canvas.create_window(160, 300, window=login_btn)
    canvas.create_window(270, 300, window=register_btn)

    # Login logic
    def login():

        username = username_entry.get().strip()
        password = password_entry.get().strip()

        # Prevent login if either field is blank
        if not username or not password:
            messagebox.showwarning("Login Failed", "Username and password cannot be blank.")
            return

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, role FROM Users WHERE username=%s AND password_hash=%s",
                       (username_entry.get(), password_entry.get()))
        result = cursor.fetchone()
        db.close()


        if result:
            user_id, role = result
            username = username_entry.get()
            if role == "admin":
                open_admin_dashboard(root, frame)
            else:
                open_user_dashboard(root, frame, user_id, username)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")


    # Register logic
    def show_register():
        clear_frame(frame)
        root.geometry("350x400")
        root.resizable(False, False)

        image = Image.open("asset/dogdog.jpg")
        image = image.resize((350, 400), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(image)

        canvas = tk.Canvas(frame, width=350, height=400, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, anchor="nw", image=bg_image)
        canvas.bg_image = bg_image

        # Input widgets
        title_label = tk.Label(frame, text="Register New User", bg="#20141c", font=HEADER_FONT, fg=ACCENT_YELLOW)
        user_label = tk.Label(frame, text="Username", font=FONT, bg=WHITE, fg=PRIMARY_BLUE)
        reg_user = tk.Entry(frame, font=FONT)

        pass_label = tk.Label(frame, text="Password", font=FONT, bg=WHITE, fg=PRIMARY_BLUE)
        reg_pass = tk.Entry(frame, font=FONT, show="*")

        register_btn = ttk.Button(frame, text="Register", style="Accent.TButton", width=12, command=lambda: register())
        back_btn = ttk.Button(frame, text="Back to Login", style="Primary.TButton", width=12,
                              command=lambda: show_login(root, frame))

        canvas.create_window(175, 50, window=title_label)
        canvas.create_window(175, 100, window=user_label)
        canvas.create_window(175, 130, window=reg_user)
        canvas.create_window(175, 180, window=pass_label)
        canvas.create_window(175, 210, window=reg_pass)
        canvas.create_window(120, 270, window=register_btn)
        canvas.create_window(230, 270, window=back_btn)

        def register():
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users WHERE username=%s", (reg_user.get(),))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                db.close()
                return
            cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, 'user')",
                           (reg_user.get(), reg_pass.get()))
            db.commit()
            db.close()
            messagebox.showinfo("Success", "Registered successfully")
            show_login(root, frame)

    login_btn.config(command=login)
    register_btn.config(command=show_register)
