import os

# Replace this with the path to your folder
folder_path = r"/dataset/DETRAC-Images"

# List of image extensions to check
image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")

# Count image files
image_count = sum(
    1 for file in os.listdir(folder_path) if file.lower().endswith(image_extensions)
)

print(f"Number of image files in the folder: {image_count}")
