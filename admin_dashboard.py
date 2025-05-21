import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection
from utils import clear_frame

PRIMARY_BLUE = "#1F1B4F"
LIGHT_BLUE = "#20141c"
ACCENT_YELLOW = "#F9BF3B"
WHITE = "#ffffff"
FF = "#f4eee2"
FONT = ("Segoe UI", 12)
HEADER_FONT = ("Segoe UI", 16, "bold")
ALT_ROW = "#edecec"
ROUNDED_RADIUS = 15


def style_widgets(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview",
                    background=FF,
                    foreground=PRIMARY_BLUE,
                    rowheight=28,
                    fieldbackground=FF,
                    font=FONT,

                    )


    style.configure("Treeview.Heading",
                    font=FONT,
                    background=PRIMARY_BLUE,
                    foreground=WHITE,

                    )
    style.map("Treeview", background=[('selected', PRIMARY_BLUE)])
    style.configure("Accent.TButton",
                    background=ACCENT_YELLOW,
                    foreground=WHITE,
                    font=FONT,

                    )
    style.configure("Primary.TButton",
                    background=PRIMARY_BLUE,
                    foreground=WHITE,
                    font=FONT,

                    )
    style.map("Accent.TButton",
              background=[('active', "#facc15"), ('!active', ACCENT_YELLOW)])
    style.map("Primary.TButton",
              background=[('active', "#1d4ed8"), ('!active', PRIMARY_BLUE)])

def open_admin_dashboard(root, frame):
    clear_frame(frame)
    root.geometry("830x650")
    style_widgets(root)
    frame.configure(bg=LIGHT_BLUE)

    tk.Label(frame, text="Admin Dashboard",
             font=HEADER_FONT, bg=LIGHT_BLUE, fg=ACCENT_YELLOW).pack(pady=10)

    tree_frame = tk.Frame(frame, bg=ACCENT_YELLOW,highlightbackground=ACCENT_YELLOW,highlightthickness=2, bd=2, relief="solid")
    tree_frame.pack(padx=5, pady=5)
    inner_frame = tk.Frame(tree_frame, bg=FF)
    inner_frame.pack(padx=6, pady=6)

    # Treeview (table)
    columns = ("ID", "Name", "Description", "Quantity")
    tree = ttk.Treeview(inner_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    tree.pack(padx=8, pady=10)

    def refresh_tree():
        for row in tree.get_children():
            tree.delete(row)
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT product_id, name, description, quantity_available FROM Products")
        for idx, row in enumerate(cursor.fetchall()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tree.insert("", "end", values=row, tags=(tag,))
        tree.tag_configure('evenrow', background=FF)
        tree.tag_configure('oddrow', background=ALT_ROW)
        db.close()

    def add_product():
        name = name_entry.get()
        desc = desc_entry.get()
        qty = qty_entry.get()
        if not name or not qty.isdigit():
            messagebox.showerror("Error", "Invalid input")
            return
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM Products WHERE name = %s", (name,))
        exists = cursor.fetchone()[0]
        if exists:
            db.close()
            messagebox.showerror("Error", "Product name already exists!")
            return

        cursor.execute(
            "INSERT INTO Products (name, description, quantity_available) VALUES (%s, %s, %s)",
            (name, desc, int(qty))
        )
        db.commit()
        db.close()
        refresh_tree()
        clear_entries()

    def update_product():
        selected = tree.focus()
        if not selected:
            return
        item = tree.item(selected)['values']
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE Products SET name=%s, description=%s, quantity_available=%s WHERE product_id=%s",
            (name_entry.get(), desc_entry.get(), qty_entry.get(), item[0])
        )
        db.commit()
        db.close()
        refresh_tree()
        clear_entries()

    def delete_product():
        selected = tree.focus()
        if not selected:
            return
        item = tree.item(selected)['values']

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            return

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM Products WHERE product_id=%s", (item[0],))
            db.commit()
            db.close()
            refresh_tree()
            clear_entries()
        except Exception as e:
            db.rollback()
            db.close()
            messagebox.showerror("Error", "Cannot delete product. It is used in existing orders.")

    def on_select(event):
        selected = tree.focus()
        if not selected:
            clear_entries()
            return

        values = tree.item(selected)["values"]
        name_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])
        desc_entry.delete(0, tk.END)
        desc_entry.insert(0, values[2])
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, values[3])

    def clear_entries():
        name_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)

    tree.bind("<<TreeviewSelect>>", on_select)

    # Entry form inside a colored frame



    form_frame = tk.Frame(frame, bg=FF, bd=2, relief=tk.GROOVE)
    form_frame.pack(pady=12, padx=16, fill="x", ipadx=6, ipady=8)

    tk.Label(form_frame, text="Name:", font=FONT, bg=FF, fg=PRIMARY_BLUE).grid(row=0, column=0, sticky="e", padx=4, pady=4)
    name_entry = tk.Entry(form_frame, font=FONT, width=20)
    name_entry.grid(row=0, column=1, padx=4, pady=4)

    tk.Label(form_frame, text="Description:", font=FONT, bg=FF, fg=PRIMARY_BLUE).grid(row=1, column=0, sticky="e", padx=4, pady=4)
    desc_entry = tk.Entry(form_frame, font=FONT, width=20)
    desc_entry.grid(row=1, column=1, padx=4, pady=4)

    tk.Label(form_frame, text="Quantity:", font=FONT, bg=FF, fg=PRIMARY_BLUE).grid(row=2, column=0, sticky="e", padx=4, pady=4)
    qty_entry = tk.Entry(form_frame, font=FONT, width=20)
    qty_entry.grid(row=2, column=1, padx=4, pady=4)

    # --- Edit Dropdown Button ---
    edit_frame = tk.Frame(frame, bg=LIGHT_BLUE)
    edit_frame.pack(pady=12)

    def show_edit_menu(event):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        edit_menu.tk_popup(x, y)

    def edit_action(action):
        if action == "Add":
            add_product()
        elif action == "Update":
            update_product()
        elif action == "Delete":
            delete_product()

    # Creating the popup menu
    edit_menu = tk.Menu(root, tearoff=0)
    edit_menu.add_command(label="Add", command=lambda: edit_action("Add"))
    edit_menu.add_command(label="Edit", command=lambda: edit_action("Update"))
    edit_menu.add_command(label="Delete", command=lambda: edit_action("Delete"))

    # Edit button
    edit_btn = ttk.Button(
        edit_frame, text="Update", style="Accent.TButton", width=10)
    edit_btn.grid(row=0, column=0, padx=8)
    # Bind left mouse click to show the menu
    edit_btn.bind("<Button-1>", show_edit_menu)

    # Logout button
    ttk.Button(
        edit_frame,
        text="Logout",
        style="Primary.TButton",
        width=10,
        command=lambda: __import__('login').show_login(root, frame)
    ).grid(row=0, column=1, padx=12)

    refresh_tree()