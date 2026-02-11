import matplotlib.pyplot as plt
import matplotlib.animation as Animate
import numpy as np
import glob
import sys

fdir = "/Users/jacksontobin/Local_Documents/NightTime_Research/ANGSTROM/Angstrom_data/10272025/Angstrom_Overnight_2025-10-27_Band450nm/*tiff"

# Open all the tiff images in fdir from time 05:00 to 06:00
file_list = sorted(glob.glob(fdir))  # Assuming images are named in a way that sorting works
print('file_list created: ', len(file_list))

# Keep images from 5:00 to 6:00 MST only
# Using UTC conversion (UTC = MST + 7 hours)
# 
images = [plt.imread(file) for file in file_list]
images = np.array(images)
print("Images loaded: ", images.shape)

# Take the images from hour 5 to 6

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
print("Creating animation...")
# Now create an animation of these images
fig, ax = plt.subplots(figsize=(8, 8))
# initialize the first image
im = ax.imshow(images[0], cmap='gray', vmin=0, vmax=255)
ax.axis('off')

# Function for updating the animation
def update(frame):
    im.set_array(images[frame])
    ax.set_title(f"Frame {frame + 1} / {len(images)}")
    return [im]

# Create the animation
ani = Animate.FuncAnimation(fig, update, frames=len(images), interval=100, blit=True)
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Save the animation as a gif
outname = './test1.gif'
ani.save(outname, writer='pillow')
print(f"Animation saved as {outname}")