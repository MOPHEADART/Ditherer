import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from Ditherer import apply_bayer_dithering

# Create window
window = tk.Tk()
window.title("Ditherer")
window.geometry("500x800")
window.minsize(width=500, height=800)

# Store variables to use globally
loaded_image = None
image_tk = None
resize_after_id = None
preview_window = None
preview_label = None
zoom_level = 1.0
zoom_step = 0.1

###############
#Layout Frames#
###############
# Load image button frame
load_button_frame = tk.Frame(window)
load_button_frame.place(relx=0.5, rely=0.1, anchor="center")

# Export buttons frame
export_frame = tk.Frame(window)
export_frame.place(relx=0.5, rely=0.92, relwidth=0.6, anchor="center")

# Image frame
image_frame = tk.Frame(window)
image_frame.place(relx=0.5, rely=0.35, relwidth=0.8, relheight=0.4, anchor="center")
image_frame.pack_propagate(False)

# Downscale slider frame
downscale_factor = tk.IntVar(value=2)
slider_frame = tk.Frame(window)
slider_frame.place(relx=0.5, rely=0.65, relwidth=0.7, anchor='center')

# Preview image button frame
preview_button_frame = tk.Frame(window)
preview_button_frame.place(relx=0.5, rely=0.77, anchor="center")
###############

# Label to image frame
image_label = tk.Label(image_frame, bg="gray")
image_label.pack(fill=tk.BOTH, expand=True)

# Label to slider
slider_label = tk.Label(slider_frame, text= "Downscale Factor:", anchor="w", justify="left")
slider_label.pack(anchor="w")

#Label to dropdown
matrix_dropdown_label = tk.Label(window, text="Dither type:")
matrix_dropdown_label.place(relx=0.5, rely=0.57, anchor="center")

# When 'Load Image' is clicked
def load_image():
    global loaded_image, image_tk
    path = filedialog.askopenfilename(filetypes=[("Image Files","*.png; *.jpg; *.jpeg")])
    
    # If image is selected
    if path:
        loaded_image = Image.open(path)
        update_image()
        update_preview()

# Scale Image with window size
def update_image():
    global loaded_image, image_label

    if loaded_image:
        frame_width = image_frame.winfo_width()
        frame_height = image_frame.winfo_height()
        frame_aspect = frame_width / frame_height

        # Original image size and aspect ratio
        image_width, image_height = loaded_image.size
        image_aspect = image_width / image_height

        # Fit image into window with maintained aspect ratio
        if image_aspect > frame_aspect:
            new_width = frame_width
            new_height = int(frame_width / image_aspect)
        else:
            new_height = frame_height
            new_width = int(frame_height * image_aspect)

        resized_image = loaded_image.resize((new_width, new_height), Image.Resampling.BILINEAR)

        # Convert to use with Tkinter
        image_tk = ImageTk.PhotoImage(resized_image)
        image_label.config(image = image_tk)
        image_label.image = image_tk

# Debounce resize event
def on_resize(event):
    global resize_after_id

    if not loaded_image:
        return
    current_size = (image_frame.winfo_width(), image_frame.winfo_height())

    if resize_after_id:
        window.after_cancel(resize_after_id)
    resize_after_id = window.after(100, update_image)

# Generate dithered image
def generate_dithered_image():
    global preview_label

    if not loaded_image:
        return None
    
    downscale = downscale_factor.get()

    selected_matrix = matrix_size.get()
    if "Bayer 2x2" in selected_matrix:
        matrix_value = 2
    elif "Bayer 4x4" in selected_matrix:
        matrix_value = 4
    elif "Bayer 8x8" in selected_matrix:
        matrix_value = 8

    return apply_bayer_dithering(loaded_image, downscale, matrix_value, color=color_checkbox_state.get() == 1)

# Open preview window
def open_preview():
    global preview_window, preview_label
    if preview_window is not None and tk.Toplevel.winfo_exists(preview_window):
        preview_window.lift()
        return
    
    preview_window = tk.Toplevel(window)
    preview_window.title("Preview Image")
    preview_window.geometry("420x420")

    preview_label = tk.Label(preview_window, bg="black")
    preview_label.pack(fill=tk.BOTH, expand=True)

    preview_window.bind("<MouseWheel>", on_mouse_wheel)

    update_preview()

def on_settings_change(*args):
    update_preview()

# Update preview window
def update_preview():
    global preview_label

    dithered = generate_dithered_image()
    if dithered is None or preview_label is None:
        return
    
    width, height = dithered.size
    zoomed = dithered.resize(
        (int(width * zoom_level), int(height * zoom_level)),
        resample=Image.NEAREST
    )
    
    preview_tk = ImageTk.PhotoImage(zoomed)
    preview_label.config(image=preview_tk)
    preview_label.image = preview_tk

# Zoom function
def on_mouse_wheel(event):
    global zoom_level

    if event.delta > 0:
        zoom_level += zoom_step
    else:
        zoom_level = max(zoom_step, zoom_level - zoom_step)
    
    update_preview()

# Bind the resize of window to image update
window.bind("<Configure>", on_resize)

###########
# Widgets #
###########
# Load button
load_image_button = tk.Button(load_button_frame, text="Load Image", command=load_image)
load_image_button.pack()

# Export buttons
export_png_button = tk.Button(export_frame, text="Export PNG", command=lambda: export_image("PNG"))
export_png_button.pack(side=tk.RIGHT, expand=True)

export_jpg_button = tk.Button(export_frame, text="Export JPG", command=lambda: export_image("JPEG"))
export_jpg_button.pack(side=tk.LEFT, expand=True)

# Downscale Slider
downscale_slider = tk.Scale(
    slider_frame, from_=1, to=12, orient=tk.HORIZONTAL,
    variable=downscale_factor
)
downscale_slider.pack (fill=tk.X, expand=True)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100)
progress_bar.place(relx=0.5, rely=0.97, relwidth=0.95, anchor="center")

# Dither selection dropdown
matrix_size = tk.StringVar(value="Bayer 2x2")
matrix_dropdown = ttk.Combobox(window, textvariable=matrix_size, state="readonly")
matrix_dropdown['values'] = ("Bayer 2x2", "Bayer 4x4", "Bayer 8x8")
matrix_dropdown.current(0)
matrix_dropdown.place(relx=0.5, rely=0.6, relwidth=0.3, anchor="center")

# Upscale checkbox
upscale_checkbox_state = tk.IntVar()
upscale_checkbox = tk.Checkbutton(window, text="Upscale on export?", variable=upscale_checkbox_state,
                                  onvalue=1, offvalue=0)
upscale_checkbox.place(relx=0.25, rely=0.85, anchor="center")

# Color checkbox
color_checkbox_state = tk.IntVar()
color_checkbox = tk.Checkbutton(window, text="Color image?", variable=color_checkbox_state,
                                onvalue=1, offvalue=0)
color_checkbox.place(relx=0.75, rely=0.85, anchor="center")

# Preview button
preview_button = tk.Button(preview_button_frame, text="Live Preview", command=open_preview)
preview_button.pack()
###########

downscale_factor.trace_add("write", on_settings_change)
color_checkbox_state.trace_add("write", on_settings_change)
matrix_size.trace_add("write", on_settings_change)

# Exporter
def export_image(format):
    if loaded_image is None:
        return
    
    progress_var.set(10)

    dithered = generate_dithered_image()

    if upscale_checkbox_state.get() == 1:
        dithered = dithered.resize(loaded_image.size, resample=Image.NEAREST)

    progress_var.set(50)

    ext = format.lower()
    file_path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"{format} files", f"*.{ext}")])
    if file_path:
        dithered.save(file_path, format=format)

    progress_var.set(100)
    window.update_idletasks
    window.after(500, lambda: progress_var.set(0))

# Tinker Event loop
window.mainloop()