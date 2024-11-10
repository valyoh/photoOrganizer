import os
from PIL import Image, ImageOps

def resize_images(root_folder, size=(800, 600)):
    # Get the total number of images to process
    total_files = sum([len([file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and '-resized' not in file]) for _, _, files in os.walk(root_folder)])
    processed_files = 0

    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and '-resized' not in file:
                file_path = os.path.join(subdir, file)
                try:
                    image = Image.open(file_path)
                    image = ImageOps.exif_transpose(image)  # Keep the orientation

                    original_width, original_height = image.size
                    aspect_ratio = original_width / original_height

                    # Calculate new dimensions to maintain aspect ratio
                    if original_width > original_height:
                        new_width = size[0]
                        new_height = int(new_width / aspect_ratio)
                    else:
                        new_height = size[1]
                        new_width = int(new_height * aspect_ratio)

                    image_resized = image.resize((new_width, new_height), Image.LANCZOS)

                    base, ext = os.path.splitext(file_path)
                    new_file_path = f"{base}-resized{ext}"

                    image_resized.save(new_file_path)

                    # Preserve original timestamps
                    original_stats = os.stat(file_path)
                    os.utime(new_file_path, (original_stats.st_atime, original_stats.st_mtime))

                    #print(f"Resized image saved as {new_file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

                # Update progress
                processed_files += 1
                progress = processed_files / total_files
                progress_bar = (u"\u2588" * int(progress * 40)).ljust(40)
                print(f"\r[{progress_bar}] {progress * 100:.2f}%", end='')

if __name__ == "__main__":
    root_folder = 'E:/takeout-20240926T082647Z-004' #input("Enter the root folder path: ")
    resize_images(root_folder)
