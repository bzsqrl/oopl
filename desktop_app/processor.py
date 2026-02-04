import ffmpeg
import os
import subprocess
import json

import sys

import platform

def get_ffmpeg_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        exe_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        ffmpeg_exe = os.path.join(base_path, exe_name)
        if os.path.exists(ffmpeg_exe):
            return ffmpeg_exe
    return "ffmpeg" # Fallback to system PATH

def get_ffprobe_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        exe_name = "ffprobe.exe" if platform.system() == "Windows" else "ffprobe"
        ffprobe_exe = os.path.join(base_path, exe_name)
        if os.path.exists(ffprobe_exe):
            return ffprobe_exe
    return "ffprobe" # Fallback to system PATH

def get_video_duration(input_file):
    ffprobe_cmd = get_ffprobe_path()
    try:
        probe = ffmpeg.probe(input_file, cmd=ffprobe_cmd)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        return float(video_stream['duration'])
    except Exception as e:
        print(f"Error probing file {input_file}: {e}")
        return None

def process_video_crossfade(input_file, crossfade_duration, output_format="mp4", target_output_duration=None, output_dir="outputs", enable_crossfade=True, start_offset=0.0, quality_val=None, output_filename=None, target_resolution=None):
    """
    Takes a video file, finds its duration, and creates a crossfaded loop.
    target_resolution: tuple (width, height) or None
    """
    
    # Old: output_filename = f"processed_{os.path.basename(input_file)}"
    # New: filename loop.ext (Default) OR custom output_filename
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Determine extension
    ext = "mp4"
    if output_format == "hap" or output_format == "prores" or output_format == "mjpeg":
        ext = "mov"
        
    if output_filename:
        # Use provided filename (ensure extension matches format if possible, or just append)
        # We assume the caller provides the full name including desirable extension, BUT
        # to be safe let's respect the format extension if the user didn't provide one.
        if not output_filename.lower().endswith(f".{ext}"):
             # Just replace whatever extension (if any) with correct one
             name_no_ext = os.path.splitext(output_filename)[0]
             output_filename = f"{name_no_ext}.{ext}"
    else:
        # Default Logic
        output_filename = f"{base_name} loop.{ext}"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, output_filename)
    
    duration = get_video_duration(input_file)
    if duration is None:
        raise Exception("Could not determine video duration")
        
    # Adjust available duration if seeking
    if start_offset > 0:
        if start_offset >= duration:
             raise Exception(f"Start offset ({start_offset}s) is beyond video duration ({duration}s)")
        duration -= start_offset
        print(f"Applying start offset {start_offset}s. Effective duration: {duration}s")
    
    if target_output_duration:
        # NOTE: Logic differs if crossfade is ON or OFF
        if enable_crossfade:
            # We need to account for the safety margin (0.25) and buffer (0.5) that are subtracted effectively
            # Final Duration = D - 0.25 - (F + 0.5) = D - F - 0.75
            # So D = Target + F + 0.75
            required_duration = target_output_duration + crossfade_duration + 0.75
            if duration > required_duration:
                 duration = required_duration # Trim input to exactly what's needed
                 print(f"Trimming input to {duration}s for target output {target_output_duration}s")
        else:
            # Plain trim
            pass 
        
    if enable_crossfade:
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

    if enable_crossfade:
        # Body: F_eff to D_safe - F_eff
        # Tail: D_safe - F_eff to D_safe
        # Head: 0 to F_eff
        
        body_start = F_eff
        body_end = D_safe - F_eff
        tail_start = D_safe - F_eff
        tail_end = D_safe
        head_end = F_eff
        
        # Determine Source Node
        # Chain filters: [0:v] -> [v_trim] -> [v_scaled] -> split
        
        current_node = "[0:v]"
        setup_filter = ""
        
        # 1. Trim/Seek
        if start_offset > 0:
             setup_filter += f"[0:v]trim=start={start_offset},setpts=PTS-STARTPTS[v_main];"
             current_node = "[v_main]"
             
        # 2. Scale
        if target_resolution:
            w, h = target_resolution
            # Chain from current_node
            # We implicitly stretch if aspect ratio differs (default behavior of scale=w:h)
            setup_filter += f"{current_node}scale={w}:{h}[v_scaled];"
            current_node = "[v_scaled]"
        
        filter_complex = (
            f"{setup_filter}"
            f"{current_node}split=3[v_body][v_tail][v_head];"
            f"[v_body]trim=start={body_start}:end={body_end},setpts=PTS-STARTPTS[body];"
            f"[v_tail]trim=start={tail_start}:end={tail_end},setpts=PTS-STARTPTS[tail];"
            f"[v_head]trim=start=0:end={head_end},setpts=PTS-STARTPTS[head];"
            f"[tail][head]xfade=transition=fade:duration={F}:offset=0[turn];"
            f"[body][turn]concat=n=2:v=1:a=0[outv]"
        )
    else:
        # No crossfade logic.
        pass

    cmd = [
        get_ffmpeg_path(), "-y"
    ]
    
    # If using simple path (no crossfade) and seeking, use fast seeking before input
    if not enable_crossfade and start_offset > 0:
         cmd.extend(["-ss", str(start_offset)])
         
    cmd.extend(["-i", input_file])
    
    if enable_crossfade:
        cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]"])
    else:
        # Simple processing
        
        # Apply scaling if needed via -vf
        video_filters = []
        if target_resolution:
            w, h = target_resolution
            video_filters.append(f"scale={w}:{h}")
            
        if video_filters:
            cmd.extend(["-vf", ",".join(video_filters)])
        
        if target_output_duration:
            cmd.extend(["-t", str(target_output_duration)])
    
    
    if output_format == "hap":
        # HAP: Expect "hap" or "hap_q"
        val = quality_val if quality_val else "hap"
        cmd.extend(["-c:v", "hap", "-format", val])
        
    elif output_format == "prores":
        # ProRes 422: Expect "0", "1", "2", "3"
        val = str(quality_val) if quality_val is not None else "2"
        cmd.extend(["-c:v", "prores_ks", "-profile:v", val])
        
    elif output_format == "mjpeg":
        # MJPEG: Expect qscale 2-31
        val = str(quality_val) if quality_val is not None else "5"
        cmd.extend(["-c:v", "mjpeg", "-q:v", val])
        
    else:
        # MP4 (H.264): Expect CRF 18-35
        val = str(quality_val) if quality_val is not None else "23"
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", val])
        
    cmd.append(output_path)
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    return output_path
