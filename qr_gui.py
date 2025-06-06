#!/usr/bin/env python3
import os
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
import qrcode
from PIL import Image, ImageTk
from qrcode.image.svg import SvgPathImage

# Determine correct resampling filter
from PIL import Image as _PilImage
RESAMPLE = getattr(_PilImage, "LANCZOS", _PilImage.BICUBIC)

# Fixed canvas size
MAX_PREVIEW = 512

def choose_color(var, default):
    _, hexcol = colorchooser.askcolor(color=var.get() or default)
    if hexcol:
        var.set(hexcol)
        if var is custom_fill_var:
            fill_choice.set("custom")
        elif var is custom_bg_var:
            bg_choice.set("custom")

def select_file():
    fmt = fmt_var.get()
    types = [("PNG Image","*.png"),("JPEG Image","*.jpg"),("SVG Image","*.svg")]
    p = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=types)
    if p: path_var.set(p)

def on_format_change(*_):
    p = path_var.get()
    if p:
        base, _ = os.path.splitext(p)
        path_var.set(base + "." + fmt_var.get())

def build_qr_image():
    data = data_entry.get().strip()
    if not data:
        raise ValueError("Please enter text or URL.")

    try:
        box_px = int(box_var.get())
    except ValueError:
        raise ValueError("Module size must be an integer.")
    if box_px < 1:
        raise ValueError("Module size must be at least 1 px.")

    try:
        border_px = int(border_var.get())
    except ValueError:
        raise ValueError("Border must be an integer.")
    if border_px < 0:
        raise ValueError("Border cannot be negative.")

    border_modules = int(round(border_px / box_px))

    fm = fill_choice.get()
    fill = fm if fm in ("black","white") else custom_fill_var.get() or "black"

    bm = bg_choice.get()
    if bm == "transparent":
        transparent, back = True, "white"
    elif bm in ("white","black"):
        transparent, back = False, bm
    else:
        transparent, back = False, custom_bg_var.get() or "white"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_px,
        border=border_modules,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill, back_color=back).convert("RGBA")

    if transparent:
        img.putdata([
            (r, g, b, 0) if (r, g, b) == (255,255,255) else (r, g, b, a)
            for (r, g, b, a) in img.getdata()
        ])
    return img

def preview():
    try:
        img = build_qr_image()
    except Exception as e:
        return messagebox.showerror("Preview Error", str(e))

    w, h = img.size
    dim_label.config(text=f"{w}×{h} px")

    scale = min(1, MAX_PREVIEW / w, MAX_PREVIEW / h)
    dw, dh = int(w * scale), int(h * scale)
    thumb = img.resize((dw, dh), RESAMPLE)

    preview_canvas.delete("all")
    tkimg = ImageTk.PhotoImage(thumb)
    preview_canvas.create_image(
        MAX_PREVIEW // 2,
        MAX_PREVIEW // 2,
        image=tkimg,
        anchor="center"
    )
    preview_canvas.image = tkimg

def generate():
    try:
        img = build_qr_image()
    except Exception as e:
        return messagebox.showerror("Error", str(e))

    p = path_var.get().strip()
    if not p:
        return messagebox.showerror("Error", "Select an output file.")

    fmt = fmt_var.get()
    try:
        if fmt in ("png","jpg"):
            out = img if fmt=="png" else img.convert("RGB")
            out.save(p)
        else:
            svg = qrcode.make(
                data_entry.get().strip(),
                image_factory=SvgPathImage,
                fill_color=fill_choice.get()
            )
            with open(p,"wb") as f:
                f.write(svg.to_string())
        messagebox.showinfo("Saved", f"QR saved:\n{p}")
    except Exception as e:
        messagebox.showerror("Save Error", str(e))


root = tk.Tk()
root.title("MacQRGenerator")

# Use the system window background color
default_bg = root.cget("bg")

# Text / URL
tk.Label(root, text="Text / URL:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
data_entry = tk.Entry(root, width=40)
data_entry.grid(row=0, column=1, columnspan=4, sticky="w")

# Fill Color
tk.Label(root, text="Fill Color:").grid(row=1, column=0, sticky="e")
fill_choice = tk.StringVar(value="black")
tk.Radiobutton(root, text="Black",  variable=fill_choice, value="black").grid(row=1, column=1)
tk.Radiobutton(root, text="White",  variable=fill_choice, value="white").grid(row=1, column=2)
tk.Radiobutton(root, text="Custom", variable=fill_choice, value="custom").grid(row=1, column=3)
custom_fill_var = tk.StringVar(value="#000000")
tk.Entry(root, textvariable=custom_fill_var, width=10).grid(row=2, column=3, sticky="w")
tk.Button(root, text="Choose…", command=lambda: choose_color(custom_fill_var, "#000000")).grid(row=2, column=4)

# Background Color
tk.Label(root, text="Background Color:").grid(row=3, column=0, sticky="e")
bg_choice = tk.StringVar(value="white")
tk.Radiobutton(root, text="White",       variable=bg_choice, value="white").grid(row=3, column=1)
tk.Radiobutton(root, text="Black",       variable=bg_choice, value="black").grid(row=3, column=2)
tk.Radiobutton(root, text="Custom",      variable=bg_choice, value="custom").grid(row=3, column=3)
tk.Radiobutton(root, text="Transparent", variable=bg_choice, value="transparent").grid(row=4, column=1)
custom_bg_var = tk.StringVar(value="#ffffff")
tk.Entry(root, textvariable=custom_bg_var, width=10).grid(row=4, column=3, sticky="w")
tk.Button(root, text="Choose…", command=lambda: choose_color(custom_bg_var, "#ffffff")).grid(row=4, column=4)

# Format
tk.Label(root, text="Format:").grid(row=5, column=0, sticky="e", padx=4, pady=4)
fmt_var = tk.StringVar(value="png")
ttk.OptionMenu(root, fmt_var, fmt_var.get(), "png","jpg","svg").grid(row=5, column=1, sticky="w")
fmt_var.trace("w", on_format_change)

# Module size & Border
tk.Label(root, text="Module size (px):").grid(row=6, column=0, sticky="e", padx=4)
box_var = tk.StringVar(value="10")
tk.Entry(root, textvariable=box_var, width=5).grid(row=6, column=1, sticky="w")
tk.Label(root, text="Border (px):").grid(row=6, column=2, sticky="e")
border_var = tk.StringVar(value="10")
tk.Entry(root, textvariable=border_var, width=5).grid(row=6, column=3, sticky="w")

# Output file
ttk.Button(root, text="Select…", command=select_file).grid(row=7, column=0, columnspan=2, pady=6)
path_var = tk.StringVar(value="")
tk.Entry(root, textvariable=path_var, width=40).grid(row=7, column=2, columnspan=3, sticky="w")

# Preview & Generate
ttk.Button(root, text="Preview", command=preview).grid(row=8, column=1, pady=6)
ttk.Button(root, text="Generate", command=generate).grid(row=8, column=3, pady=6)

# Preview panel
dim_label = tk.Label(root, text="– × – px")
dim_label.grid(row=9, column=0, columnspan=5)
preview_canvas = tk.Canvas(
    root,
    width=MAX_PREVIEW,
    height=MAX_PREVIEW,
    bg=default_bg,      # system window background
    bd=1, relief="sunken"
)
preview_canvas.grid(row=10, column=0, columnspan=5, pady=8)

# Force layout to read the actual window size
root.update_idletasks()

# Get window size
win_w = root.winfo_width()
win_h = root.winfo_height()

# Get screen size
scr_w = root.winfo_screenwidth()
scr_h = root.winfo_screenheight()

# Calculate position x, y
pos_x = (scr_w - win_w) // 2
pos_y = (scr_h - win_h) // 2

# Set geometry so the window is centered
root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

# Start the event loop
root.mainloop()