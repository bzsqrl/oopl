import argparse
import os
import glob
from backend.processor import process_video_crossfade

def main():
    parser = argparse.ArgumentParser(description="VJ Loop Crossfader - Convert clips to seamless loops.")
    parser.add_argument("input", help="Input file path or directory path.")
    parser.add_argument("-d", "--duration", type=float, default=1.0, help="Crossfade duration in seconds (default: 1.0)")
    parser.add_argument("-f", "--format", choices=["mp4", "hap"], default="mp4", help="Output format: 'mp4' (H.264) or 'hap' (HAP Codec). Default: mp4")
    parser.add_argument("-o", "--output", help="Output directory (optional). Defaults to 'processed' folder in current directory.")
    
    args = parser.parse_args()
    
    # Determine output directory
    output_dir = args.output
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "processed")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Output directory: {output_dir}")
    
    files_to_process = []
    
    # Check if input is directory or file
    if os.path.isdir(args.input):
        # Gather all video files
        types = ('*.mov', '*.mp4', '*.avi', '*.mkv')
        for t in types:
            files_to_process.extend(glob.glob(os.path.join(args.input, t)))
    elif os.path.isfile(args.input):
        files_to_process.append(args.input)
    else:
        print(f"Error: Input '{args.input}' not found.")
        return

    if not files_to_process:
        print("No video files found.")
        return

    print(f"Found {len(files_to_process)} file(s) to process.")
    
    for file_path in files_to_process:
        print(f"Processing: {os.path.basename(file_path)}...")
        try:
            # We need to slightly update processor logic to accept a specific output path if we want strictly controlling destination
            # But currently processor.py writes to 'outputs/' hardcoded or relative.
            # We should probably modify processor.py to accept an output directory or full path.
            # For now, let's look at processor.py content again. 
            pass 
            
            # Since I haven't modified processor.py yet, I'll do it in the next step to accept output_dir.
            # But I can pass the logic here if I import it.
            
            # Let's assume process_video_crossfade(input_file, crossfade_duration, output_format, output_dir)
            process_video_crossfade(file_path, args.duration, args.format, output_dir)
            
            print(f"Done: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()
