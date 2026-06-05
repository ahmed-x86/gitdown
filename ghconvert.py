#!/usr/bin/env python3

import argparse
import sys

def convert_url(url):
    url = url.strip()
    
    if url.startswith("https://raw.githubusercontent.com/"):
        return url
        
    if "github.com" in url:
        if "/blob/" in url:
            raw_url = url.replace("https://github.com", "https://raw.githubusercontent.com")
            raw_url = raw_url.replace("/blob/", "/refs/heads/")
            return raw_url
            
        return url
        
    return url

def process_links(urls, output_file=None):
    results = []
    
    for url in urls:
        converted = convert_url(url)
        results.append(converted)
        print(converted)
        
    if output_file:
        with open(output_file, 'a', encoding='utf-8') as f:
            for res in results:
                f.write(res + "\n")

def main():
    parser = argparse.ArgumentParser(description="Smart GitHub URL converter: Converts file links to raw, ignores directories and already raw links.")
    parser.add_argument("-link", nargs='+', help="One or more GitHub URLs to convert")
    parser.add_argument("-out", type=str, help="Output txt file to save the results")
    
    args = parser.parse_args()
    
    if args.out:
        open(args.out, 'w', encoding='utf-8').close()
        
    if args.link:
        process_links(args.link, args.out)
        if args.out:
            print("-" * 50)
            print(f"✓ Saved results to {args.out}")
    else:
 
        print("Interactive Mode. Enter GitHub URLs one by one.")
        print("Type 'exit' to stop.")
        if args.out:
            print(f"Results will be appended to: {args.out}")
        print("-" * 50)
        
        while True:
            try:
                url = input("URL: ").strip()
                if url.lower() in ['exit', 'quit']:
                    break
                if url:
                    process_links([url], args.out)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                sys.exit(0)

if __name__ == "__main__":
    main()