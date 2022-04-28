import numpy as np
import pandas as pd
import rasterio as ras
import matplotlib as mpl
from matplotlib import pyplot as plt


def load_labels():
    # Getting detect df
    ground = pd.read_csv('/data/xview3/data/labels/validation.csv')
    dets = pd.concat((pd.DataFrame(), ground))
    dets.rename({'detect_scene_row': 'scene_rows', 'detect_scene_column': 'scene_cols'}, inplace=True, axis='columns')

    # Getting predictions from file
    preds = pd.read_csv('/data/xview3/data/inference_output.csv')
    preds.rename({'detect_scene_row': 'scene_rows', 'detect_scene_column': 'scene_cols'}, inplace=True, axis='columns')

    return dets, preds


def display_image_in_actual_size(im_data, rows, cols, scene, rows2=None, cols2=None):

    dpi = mpl.rcParams['figure.dpi']
    height, width= im_data.shape

    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    vmin, vmax = -35, -5
    #print('Plotting image...')
    ax.matshow(im_data, cmap="bone", vmin=vmin, vmax=vmax)

    #print('Plotting scatterplot...')
    ax.scatter(cols, rows, s=120, facecolors="none", edgecolors="r")
    if rows2 is not None:
        ax.scatter(cols2, rows2, s=120, facecolors="none", edgecolors="g")

    plt.margins(0, 0)
    dest = '/data/xview3/data/big/visuals/' + scene + '.png'
    plt.savefig(dest)
    plt.close()


def visualizer():
    
    i = 1
    df_original, df_preds_original = load_labels()
    
    scene_ids = list(dict.fromkeys(df_original['scene_id']))
                     
    for scene_id in scene_ids:
                     
        df = df_original[df_original['scene_id'] == scene_id]
        df_preds= df_preds_original[df_preds_original['scene_id'] == scene_id]
        # progress bar
        print(f"Processing Scene {i}/50:", end="\r")
        i += 1

        # Loading image in UTM coordinates
        grdfile = '/data/xview3/data/big/validation/' + str(scene_id) + '/VH_dB.tif'
        src = ras.open(grdfile)
        image_orig = src.read(1)

        # Identifying a specific detection on which to center plot
        row = df[df['detect_id'].str.contains('6.4')].iloc[0]

        # Defining size of image patch for plot (generally suggest keeping ~ 1000)
        patch_half_width = 1000

        # Getting predictions and detections in image patch
        df_small = df[np.abs(df.scene_rows - row.scene_rows) < patch_half_width]
        df_small = df_small[np.abs(df_small.scene_cols - row.scene_cols) < patch_half_width]

        df_preds_small = df_preds[np.abs(df_preds.scene_rows - row.scene_rows) < patch_half_width]
        df_preds_small = df_preds_small[np.abs(df_preds_small.scene_cols - row.scene_cols) < patch_half_width]

        dt = image_orig[row.scene_rows - patch_half_width:row.scene_rows + patch_half_width,
                        row.scene_cols - patch_half_width:row.scene_cols + patch_half_width]

        # Plotting detections (red) and predictions (green)
        try:
            display_image_in_actual_size(dt,
                                         df_small.scene_rows - row.scene_rows + patch_half_width,
                                         df_small.scene_cols - row.scene_cols + patch_half_width,
                                         scene_id, rows2=df_preds_small.scene_rows - row.scene_rows + patch_half_width,
                                         cols2=df_preds_small.scene_cols - row.scene_cols + patch_half_width)
        except RuntimeError:
            print(f"Processing Scene {i}/50:", end="\r")
            # move along

if __name__ == '__main__':
    # Visualize detections/predictions
    visualizer()
