#!/usr/bin/env python3

import argparse
import os
import urllib.request
import sys

def download_files(txt_file):
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

                    req = urllib.request.Request(raw_url, headers={'User-Agent': 'gh-downloader'})
                    with urllib.request.urlopen(req) as response, open(local_file_path, 'wb') as out_file:
                        out_file.write(response.read())
                    print("Done ✓")
                except Exception as e:
                    print(f"Failed ✗ ({e})")
                
                current_path = None

def main():
    parser = argparse.ArgumentParser(description="Download files matching the tree structure from the links txt file.")
    parser.add_argument("-in", dest="input_file", type=str, required=True, help="The txt file containing paths and raw links")
    
    args = parser.parse_args()
    download_files(args.input_file)

if __name__ == "__main__":
    main()