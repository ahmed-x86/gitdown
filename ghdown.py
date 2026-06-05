#!/usr/bin/env python3

import argparse
import os
import urllib.request
import sys
import subprocess
import multiprocessing

def download_files(txt_file, downloader, aria_threads=None):
    if not os.path.isfile(txt_file):
        print(f"Error: File '{txt_file}' not found.")
        sys.exit(1)

    repo_name = "github_downloads"
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("Repository :"):
            full_repo = line.split(":", 1)[1].strip()
            repo_name = full_repo.split('/')[-1]
            break
    
    print(f"Target Directory: {repo_name}/")
    print(f"Downloader Tool : {downloader}")
    
    if downloader == 'aria2':
        if aria_threads is None:
            aria_threads = multiprocessing.cpu_count()
        safe_threads = min(aria_threads, 16)
        print(f"Aria2 Threads   : {safe_threads} (Requested: {aria_threads})")

    print("=" * 50)
    
    current_path = None

    for line in lines:
        line = line.strip()
        
        if line.startswith("File Path :"):
            current_path = line.split(":", 1)[1].strip()
            
        elif line.startswith("Raw Link  :"):
            raw_url = line.split(":", 1)[1].strip()
            
            if current_path and raw_url:
                local_file_path = os.path.join(repo_name, current_path)
                local_dir = os.path.dirname(local_file_path)
                
                if local_dir:
                    os.makedirs(local_dir, exist_ok=True)
                
                print(f"Downloading: {current_path} ...", end=" ", flush=True)
                
                try:
                    if downloader == 'curl':
                        subprocess.run(['curl', '-sL', '-o', local_file_path, raw_url], check=True)
                        print("Done ✓")
                        
                    elif downloader == 'wget':
                        subprocess.run(['wget', '-q', '-O', local_file_path, raw_url], check=True)
                        print("Done ✓")
                        
                    elif downloader == 'aria2':
                        filename = os.path.basename(local_file_path)
                        subprocess.run([
                            'aria2c', '-q', '--allow-overwrite=true',
                            f'-x{safe_threads}', f'-s{safe_threads}',
                            '-d', local_dir, '-o', filename, raw_url
                        ], check=True)
                        print("Done ✓")
                        
                    else:
                        req = urllib.request.Request(raw_url, headers={'User-Agent': 'gh-downloader'})
                        with urllib.request.urlopen(req) as response, open(local_file_path, 'wb') as out_file:
                            out_file.write(response.read())
                        print("Done ✓")
                        
                except subprocess.CalledProcessError:
                    print("Failed ✗ (Command Error)")
                except Exception as e:
                    print(f"Failed ✗ ({e})")
                
                current_path = None

def main():
    parser = argparse.ArgumentParser(description="Download files matching the tree structure from the links txt file.")
    parser.add_argument("-in", dest="input_file", type=str, required=True, help="The txt file containing paths and raw links")
    parser.add_argument("-d", "--downloader", dest="downloader", type=str, choices=['urllib', 'curl', 'wget', 'aria2'], default='curl', help="Download tool to use (urllib, curl, wget, aria2). Defaults to curl.")
    parser.add_argument("-t", "--threads", dest="threads", type=int, help="Number of threads for aria2. Defaults to CPU core count if omitted.")
    
    args = parser.parse_args()
    
    download_files(args.input_file, args.downloader, args.threads)

if __name__ == "__main__":
    main()