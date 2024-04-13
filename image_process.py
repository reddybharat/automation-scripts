#this script is good for image preprocessing
#e.g. when you need multiple images in a certain size, filetype etc

from PIL import Image
import os

# define path for the images to be read and where to be saved
old_path = "/images/"
new_path = "/images/"

for fh in os.listdir(old_path):
    img = Image.open(old_path + fh)
    img = img.rotate(-90)
    img = img.resize((128, 128))
    img = img.convert("RGB")
    img.save(new_path + fh, "JPEG")
