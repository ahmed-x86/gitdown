#!/usr/bin/env python3

import argparse
import urllib.request
import json
import sys

def parse_github_url(url):
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
        
    parts = url.split('/')
    try:
        github_index = parts.index("github.com")
        owner = parts[github_index + 1]
        repo = parts[github_index + 2]
        
        branch = None
        target_path = None
        
        if len(parts) > github_index + 3 and parts[github_index + 3] == "tree":
            branch = parts[github_index + 4]
            target_path = "/".join(parts[github_index + 5:])
            
        return owner, repo, branch, target_path
    except (ValueError, IndexError):
        return None, None, None, None

def fetch_repo_files(url, output_file=None, items=None):
    owner, repo, branch, target_path = parse_github_url(url)
    
    if not owner or not repo:
        print(f"Error: Invalid GitHub URL '{url}'")
        return

    if not branch:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'gh-fetcher-script'})
        try:
            with urllib.request.urlopen(req) as response:
                repo_data = json.loads(response.read().decode())
                branch = repo_data.get('default_branch', 'main')
        except Exception as e:
            print(f"Error accessing repository metadata: {e}")
            return


    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    req = urllib.request.Request(tree_url, headers={'User-Agent': 'gh-fetcher-script'})
    
    try:
        with urllib.request.urlopen(req) as response:
            tree_data = json.loads(response.read().decode())
            
            output_lines = []
            output_lines.append(f"\nRepository : {owner}/{repo}")
            output_lines.append(f"Branch     : {branch}")
            if target_path:
                output_lines.append(f"Directory  : {target_path}")
            output_lines.append("=" * 70)

            if items:
                for user_item in items:
                    clean_item = user_item.strip('/')
                    found = False
                    for item in tree_data.get('tree', []):
                        if item['path'] == clean_item:
                            found = True
                            file_path = item['path']
                            if item['type'] == 'blob':
                                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/refs/heads/{branch}/{file_path}"
                                output_lines.append(f"File Path : {file_path}")
                                output_lines.append(f"Raw Link  : {raw_url}")
                                output_lines.append("-" * 70)
                            elif item['type'] == 'tree':
                                dir_url = f"https://github.com/{owner}/{repo}/tree/{branch}/{file_path}/"
                                output_lines.append(f"Directory : {file_path}/")
                                output_lines.append(f"Link      : {dir_url}")
                                output_lines.append("-" * 70)
                            break
                    if not found:
                        output_lines.append(f"Not Found : {user_item}")
                        output_lines.append("-" * 70)
            
            else:
                for item in tree_data.get('tree', []):
                    if item['type'] == 'blob': 
                        file_path = item['path']
                        if target_path and not file_path.startswith(target_path + '/'):
                            continue
                        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/refs/heads/{branch}/{file_path}"
                        output_lines.append(f"File Path : {file_path}")
                        output_lines.append(f"Raw Link  : {raw_url}")
                        output_lines.append("-" * 70)
                        
            output_text = "\n".join(output_lines)
            
            if output_file:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(output_text + "\n")
                print(f"✓ Saved results to {output_file}")
            else:
                print(output_text)
                    
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Error fetching repository data: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch file paths and links from a GitHub repository.")
    parser.add_argument("-link", type=str, required=True, help="The GitHub repository URL")
    parser.add_argument("-out", type=str, help="Output txt file to save the results")
    parser.add_argument("items", nargs='*', help="Specific files or directories to target")
    
    args = parser.parse_args()
    
    if args.out:
        open(args.out, 'w', encoding='utf-8').close()
        
    fetch_repo_files(args.link, args.out, args.items if args.items else None)

if __name__ == "__main__":
    main()غ