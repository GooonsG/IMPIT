import tkinter as tk
from login import show_login

root = tk.Tk()
root.title("Inventory Management System")
root.geometry("700x700")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

show_login(root, main_frame)

root.mainloop()
