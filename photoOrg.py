import os
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog, messagebox

def get_exif_creation_date(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error extracting EXIF data from {file_path}: {e}")
    return None

def organize_photos(input_dirs, output_dir, operation):
    for input_dir in input_dirs:
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Use the last modified date instead of the creation date
                    creation_date = datetime.fromtimestamp(os.path.getmtime(file_path))

                    year_month_path = os.path.join(output_dir, str(creation_date.year), creation_date.strftime('%m-%B'))
                    Path(year_month_path).mkdir(parents=True, exist_ok=True)

                    destination_path = os.path.join(year_month_path, file)
                    if os.path.exists(destination_path):
                        base, extension = os.path.splitext(file)
                        counter = 1
                        new_file_name = f"{base}_{counter}{extension}"
                        new_destination_path = os.path.join(year_month_path, new_file_name)
                        while os.path.exists(new_destination_path):
                            counter += 1
                            new_file_name = f"{base}_{counter}{extension}"
                            new_destination_path = os.path.join(year_month_path, new_file_name)
                        destination_path = new_destination_path

                    if operation == 'move':
                        shutil.move(file_path, destination_path)
                    elif operation == 'copy':
                        shutil.copy2(file_path, destination_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

def select_input_folders():
    input_dirs = []
    while True:
        dir_path = filedialog.askdirectory()
        if not dir_path:
            break
        input_dirs.append(f'"{dir_path}"')  # Ensure the directory path is quoted
    if input_dirs:
        input_dirs_var.set(" ".join(input_dirs))

def select_output_folder():
    output_dir = filedialog.askdirectory()
    if output_dir:
        output_dir_var.set(f'"{output_dir}"')  # Ensure the directory path is quoted

def start_organizing():
    input_dirs = input_dirs_var.get().split('\" \"')  # Split based on quoted paths
    input_dirs = [dir.strip('"') for dir in input_dirs]  # Remove quotes from paths
    output_dir = output_dir_var.get().strip('"')  # Remove quotes from the output path
    operation = operation_var.get()
    if not input_dirs or not output_dir:
        messagebox.showerror("Error", "Please select both input and output folders.")
        return
    organize_photos(input_dirs, output_dir, operation)
    messagebox.showinfo("Success", "Photos organized successfully!")

# Create the main window
root = tk.Tk()
root.title("Photo Organizer")

# Input folders selection
input_dirs_var = tk.StringVar()
tk.Label(root, text="Input Folders:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_dirs_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Select Folders", command=select_input_folders).grid(row=0, column=2, padx=10, pady=10)

# Output folder selection
output_dir_var = tk.StringVar()
tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=output_dir_var, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Select Folder", command=select_output_folder).grid(row=1, column=2, padx=10, pady=10)

# Operation selection (copy or move)
operation_var = tk.StringVar(value='move')
tk.Label(root, text="Operation:").grid(row=2, column=0, padx=10, pady=10)
tk.Radiobutton(root, text="Move", variable=operation_var, value='move').grid(row=2, column=1, padx=10, pady=10)
tk.Radiobutton(root, text="Copy", variable=operation_var, value='copy').grid(row=2, column=2, padx=10, pady=10)

# Start button
tk.Button(root, text="Start", command=start_organizing).grid(row=3, column=1, padx=10, pady=10)

root.mainloop()
