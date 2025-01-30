import os
import math

# from moviepy.editor import VideoFileClip
from moviepy import VideoFileClip


def split_video_to_chunks(video_path: str, output_dir: str, chunk_duration: int = 10):
    """
    Splits a video into fixed-size chunks, extracts audio from each chunk,
    and saves frames (1 frame per second) for each chunk.

    :param video_path: Path to the input video file.
    :param output_dir: Directory to store output chunks, audio, and frames.
    :param chunk_duration: Duration (in seconds) of each chunk.
    """
    # Load the full video
    clip = VideoFileClip(video_path)

    # Total duration of the video in seconds
    total_duration = clip.duration

    # Make sure output directories exist
    os.makedirs(output_dir, exist_ok=True)
    audio_dir = os.path.join(output_dir, "audio")
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    # Calculate number of chunks needed (rounding up)
    num_chunks = math.ceil(total_duration / chunk_duration)

    print(f"Total video duration: {total_duration:.2f} seconds")
    print(f"Splitting into {num_chunks} chunk(s) of {chunk_duration} second(s) each.")

    for i in range(num_chunks):
        clip = VideoFileClip(video_path)
        sub_dir = os.path.join(frames_dir, f"chunk_{i:03d}")
        os.makedirs(sub_dir, exist_ok=True)
        # Start and end times for this chunk
        start_time = i * chunk_duration
        end_time = min((i + 1) * chunk_duration, total_duration)

        print(f"\nProcessing chunk {i}: from {start_time}s to {end_time}s")

        # Create subclip
        subclip = clip.subclipped(start_time, end_time)

        # Extract and save the audio for this chunk
        audio_path = os.path.join(audio_dir, f"chunk_{i:03d}.wav")
        subclip.audio.write_audiofile(audio_path)

        # Duration of this subclip (might be less than chunk_duration if it's the last chunk)
        chunk_length = end_time - start_time

        # Save one frame per second (10 frames for a 10-second chunk)
        for sec in range(math.ceil(chunk_length)):
            frame_time = sec  # second offset inside the subclip
            # Construct the frame output path
            frame_path = os.path.join(sub_dir, f"{sec:02d}.jpg")
            # Ensure we don't go past the subclip duration
            if frame_time < chunk_length:
                subclip.save_frame(frame_path, t=frame_time)
                print(f" - Saved frame at {frame_time}s -> {frame_path}")

        # Close subclip to free resources
        subclip.close()

    # Close the main clip
    clip.close()
    print("\nProcessing complete!")


if __name__ == "__main__":
    # Example usage:
    video_input = "data/videos/prince.mp4"  # Replace with your actual video path
    output_folder = "output_chunks"

    split_video_to_chunks(video_input, output_folder, chunk_duration=10)
