# %%
# Imports #

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import imageio
import shutil
from matplotlib.animation import FuncAnimation

from config import (
    file_dir,
    parent_dir,
    grandparent_dir,
    great_grandparent_dir,
    data_dir,
)


# %%
# Functions #


def create_animated_line_graph(
    dataset,
    time_col,
    value_col,
    rows_per_frame=5,
    output_video_file_name="animated_line_graph.mp4",
):
    # Create Frames dir and frames
    frames_dir = os.path.join(data_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    num_frames = (len(dataset) + rows_per_frame - 1) // rows_per_frame

    for i in range(1, num_frames + 1):
        start_idx = (i - 1) * rows_per_frame
        end_idx = min(i * rows_per_frame, len(dataset))
        data_slice = dataset.iloc[:end_idx]

        fig, ax = plt.subplots()
        ax.plot(data_slice[time_col], data_slice[value_col], marker="o")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.set_title("Animated Line Graph")
        frame_path = os.path.join(frames_dir, f"frame{i:04d}.png")
        plt.savefig(frame_path)
        plt.close(fig)

    # Create a video from the frames
    with imageio.get_writer(
        os.path.join(data_dir, output_video_file_name), mode="I", fps=60
    ) as writer:
        for i in range(1, num_frames + 1):
            frame_path = os.path.join(frames_dir, f"frame{i:04d}.png")
            frame = imageio.imread(frame_path)
            writer.append_data(frame)

    # Remove the frames directory
    shutil.rmtree(frames_dir)


# %%
# Main #

if __name__ == "__main__":
    # Data File Import Or Generation
    data_file_path = os.path.join(data_dir, "test_data.csv")

    time_col = "time"
    value_col = "value"

    if not os.path.exists(data_file_path):
        num_samples = 1000
        np.random.seed(42)
        time_data = np.arange(1, num_samples + 1)
        value_data = np.random.randint(1, 100, size=num_samples)
        test_data = pd.DataFrame({time_col: time_data, value_col: value_data})
        test_data.to_csv(data_file_path, index=False)

    # Read data
    data = pd.read_csv(data_file_path)

    # Call the function to create the animated line graph video
    create_animated_line_graph(
        data,
        time_col,
        value_col,
        rows_per_frame=10,
        output_video_file_name=os.path.join(data_dir, "animated_line_graph.mp4"),
    )


# %%
