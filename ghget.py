#!/usr/bin/env python3

import argparse
import sys

def get_raw_url(url):

    if "github.com" not in url or "/blob/" not in url:
        return f"Error: Invalid URL '{url}'. Make sure it is a GitHub repository file link."
    

    raw_url = url.replace("https://github.com", "https://raw.githubusercontent.com")
    raw_url = raw_url.replace("/blob/", "/refs/heads/")
    
    return raw_url

def main():

    parser = argparse.ArgumentParser(description="A simple tool to convert GitHub file URLs to raw direct links.")
    parser.add_argument("-link", nargs='+', help="One or more GitHub file URLs separated by space")
    
    args = parser.parse_args()
    

    if args.link:
        for url in args.link:
            print(get_raw_url(url))
    else:

        print("Interactive Mode. Enter GitHub URLs one by one.")
        print("Type 'exit' or 'quit' to stop, or press Ctrl+C.")
        print("-" * 50)
        
        while True:
            try:
                url = input("GitHub URL: ").strip()
                

                if url.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break
                

                if url:
                    print(get_raw_url(url))
                    
            except KeyboardInterrupt:
                print("\nProcess interrupted. Exiting...")
                sys.exit(0)
            except EOFError:
                print("\nExiting...")
                sys.exit(0)

if __name__ == "__main__":
    main()