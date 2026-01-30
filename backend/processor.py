import ffmpeg
import os
import subprocess
import json

def get_video_duration(input_file):
    try:
        probe = ffmpeg.probe(input_file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        return float(video_stream['duration'])
    except Exception as e:
        print(f"Error probing file {input_file}: {e}")
        return None

def process_video_crossfade(input_file, crossfade_duration, output_format="mp4", output_dir="outputs"):
    """
    Takes a video file, finds its duration, and creates a crossfaded loop.
    """
    
    output_filename = f"processed_{os.path.basename(input_file)}"
    if output_format == "hap":
        # Ensure extension is .mov for HAP
        output_filename = output_filename.rsplit('.', 1)[0] + ".mov"
    else:
        # Ensure extension is .mp4 for H264
        output_filename = output_filename.rsplit('.', 1)[0] + ".mp4"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, output_filename)
    
    duration = get_video_duration(input_file)
    if duration is None:
        raise Exception("Could not determine video duration")
        
    if duration < 2 * crossfade_duration:
        raise Exception("Video is too short for this crossfade duration (must be > 2x fade)")

    D = duration
    
    F = crossfade_duration
    
    # Safety margin: reduce effective duration to ensure we don't hit EOF quirks
    # which can cause xfade segments to be shorter than requested
    D_safe = D - 0.25
    
    D_buffer = 0.5
    
    # Effective crossfade length for trimming (includes buffer)
    F_eff = F + D_buffer
    
    if D_safe < 2 * F_eff:
         raise Exception("Video is too short for this crossfade duration (after safety margin and buffer adjustment)")

    # Body: F_eff to D_safe - F_eff
    # Tail: D_safe - F_eff to D_safe
    # Head: 0 to F_eff
    
    body_start = F_eff
    body_end = D_safe - F_eff
    tail_start = D_safe - F_eff
    tail_end = D_safe
    head_end = F_eff
    
    filter_complex = (
        f"[0:v]split=3[v_body][v_tail][v_head];"
        f"[v_body]trim=start={body_start}:end={body_end},setpts=PTS-STARTPTS[body];"
        f"[v_tail]trim=start={tail_start}:end={tail_end},setpts=PTS-STARTPTS[tail];"
        f"[v_head]trim=start=0:end={head_end},setpts=PTS-STARTPTS[head];"
        f"[tail][head]xfade=transition=fade:duration={F}:offset=0[turn];"
        f"[body][turn]concat=n=2:v=1:a=0[outv]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-filter_complex", filter_complex,
        "-map", "[outv]"
    ]
    
    if output_format == "hap":
        cmd.extend(["-c:v", "hap", "-format", "hap"])
    else:
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p"])
        
    cmd.append(output_path)
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    return output_path
