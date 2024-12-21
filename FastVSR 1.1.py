import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Path to the FFmpeg executable
FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg.exe")

# Function to process the video
def process_video(video_path, start_time, end_time, encoder):
    try:
        # Generate output filename by replacing colons with hyphens
        removed_section = f"{start_time}-{end_time}"
        
        # Replace colons with hyphens to avoid invalid characters in the filename
        removed_section_safe = removed_section.replace(":", "-")
        
        # Output filename
        output_name = f"{os.path.splitext(video_path)[0]}_removed_section_{removed_section_safe}.mp4"
        
        # Temporary files for the two parts of the video
        temp_file1 = "temp_part1.mp4"
        temp_file2 = "temp_part2.mp4"
        
        # FFmpeg command to cut the first part (before the start time)
        ffmpeg_command1 = [
            FFMPEG_PATH,
            "-i", video_path,  # Input file
            "-ss", "00:00",    # Start from the beginning
            "-to", start_time,  # Cut until the start time
            "-c:v", encoder,    # Encoder
            "-c:a", "aac",      # Audio codec
            "-strict", "experimental",
            temp_file1           # Save to temp file
        ]
        
        subprocess.run(ffmpeg_command1, check=True)
        
        # FFmpeg command to cut the second part (after the end time)
        ffmpeg_command2 = [
            FFMPEG_PATH,
            "-i", video_path,  # Input file
            "-ss", end_time,    # Start from the end time
            "-c:v", encoder,    # Encoder
            "-c:a", "aac",      # Audio codec
            "-strict", "experimental",
            temp_file2           # Save to second temp file
        ]
        
        subprocess.run(ffmpeg_command2, check=True)

        # Create a file list for concatenation
        concat_file = "filelist.txt"
        with open(concat_file, "w") as f:
            f.write(f"file '{temp_file1}'\n")
            f.write(f"file '{temp_file2}'\n")
        
        # Concatenate the two parts using the concat demuxer
        ffmpeg_command_concat = [
            FFMPEG_PATH,
            "-f", "concat",    # Use concat demuxer
            "-safe", "0",      # Allow unsafe file paths
            "-i", concat_file,  # Use file list
            "-c:v", encoder,   # Encoder
            "-c:a", "aac",     # Audio codec
            "-strict", "experimental",
            output_name        # Output file name
        ]
        
        subprocess.run(ffmpeg_command_concat, check=True)
        
        # Clean up temporary files
        os.remove(temp_file1)
        os.remove(temp_file2)
        os.remove(concat_file)  # Remove file list

        return output_name
    
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {e}")
        messagebox.showerror("Error", "An error occurred while processing the video. Please try again.")
        return None

# GUI setup
def create_gui():
    root = tk.Tk()
    root.title("Video Editor")

    # Add widgets
    tk.Label(root, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10)

    video_path_var = tk.StringVar()

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
        if file_path:
            video_path_var.set(file_path)

    tk.Entry(root, textvariable=video_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="Start Time (MM:SS):").grid(row=1, column=0, padx=10, pady=10)
    start_time_var = tk.StringVar(value="00:00")

    tk.Entry(root, textvariable=start_time_var).grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="End Time (MM:SS):").grid(row=2, column=0, padx=10, pady=10)
    end_time_var = tk.StringVar(value="00:00")

    tk.Entry(root, textvariable=end_time_var).grid(row=2, column=1, padx=10, pady=10)

    tk.Label(root, text="Select Encoder:").grid(row=3, column=0, padx=10, pady=10)
    encoder_var = tk.StringVar(value="libx264")

    encoder_choices = ["libx264", "h264_nvenc", "h264_amf"]
    encoder_menu = ttk.Combobox(root, textvariable=encoder_var, values=encoder_choices)
    encoder_menu.grid(row=3, column=1, padx=10, pady=10)

    def process():
        video_path = video_path_var.get()
        start_time = start_time_var.get()
        end_time = end_time_var.get()
        encoder = encoder_var.get()

        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("Error", "Please select a valid video file.")
            return

        if not start_time or not end_time:
            messagebox.showerror("Error", "Please provide both start and end times.")
            return

        output_file = process_video(video_path, start_time, end_time, encoder)
        if output_file:
            messagebox.showinfo("Success", f"Video processed successfully! Output: {output_file}")

    tk.Button(root, text="Process Video", command=process).grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    # Run the GUI
    root.mainloop()

# Start the GUI
if __name__ == "__main__":
    create_gui()
