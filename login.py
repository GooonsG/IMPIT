import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection
from utils import clear_frame
from admin_dashboard import open_admin_dashboard
from user_dashboard import open_user_dashboard

PRIMARY_BLUE = "#2563eb"
LIGHT_BLUE = "#dbeafe"
ACCENT_YELLOW = "#fde047"
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
    root.geometry("300x400")
    frame.configure(bg=LIGHT_BLUE)

    tk.Label(frame, text="Login", font=HEADER_FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE).pack(pady=16)

    tk.Label(frame, text="Username:", font=FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE).pack(pady=(0, 2))
    username_entry = tk.Entry(frame, font=FONT)
    username_entry.pack(pady=4)

    tk.Label(frame, text="Password:", font=FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE).pack(pady=(12, 2))
    password_entry = tk.Entry(frame, show="*", font=FONT)
    password_entry.pack(pady=4)

    def login():
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

    def show_register():
        clear_frame(frame)
        tk.Label(frame, text="Register New User").pack()
        reg_user = tk.Entry(frame)
        reg_user.pack()
        tk.Label(frame, text="Password").pack()
        reg_pass = tk.Entry(frame, show="*")
        reg_pass.pack()

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

        tk.Button(frame, text="Register", command=register).pack()
        tk.Button(frame, text="Back to Login", command=lambda: show_login(root, frame)).pack()

    btn_frame = tk.Frame(frame, bg=LIGHT_BLUE)
    btn_frame.pack(pady=18)
    ttk.Button(
        btn_frame, text="Login", style="Primary.TButton", width=10, command=login).pack(side=tk.LEFT, padx=12)

