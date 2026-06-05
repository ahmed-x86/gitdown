#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import subprocess
import curses

LOGO = [
    " ██████╗ ██╗ ████████╗ ██████╗   ██████╗  ██╗    ██╗ ██╗   ██╗ ",
    "██╔════╝ ██║ ╚══██╔══╝ ██╔══██╗ ██╔═══██╗ ██║    ██║ ████╗  ██║",
    "██║  ███╗██║    ██║    ██║  ██║ ██║   ██║ ██║ █╗ ██║ ██╔██╗ ██║",
    "██║   ██║██║    ██║    ██║  ██║ ██║   ██║ ██║███╗██║ ██║╚██╗██║",
    "╚██████╔╝██║    ██║    ██████╔╝ ╚██████╔╝ ╚███╔███╔╝ ██║ ╚████║",
    " ╚═════╝ ╚═╝    ╚═╝    ╚═════╝   ╚═════╝   ╚══╝╚══╝  ╚═╝  ╚═══╝"
]

def setup_catppuccin_colors():
    curses.use_default_colors()
    try:
        if curses.can_change_color():
            def set_hex(col_id, hex_code):
                h = hex_code.lstrip('#')
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                curses.init_color(col_id, int(r*1000/255), int(g*1000/255), int(b*1000/255))

            BLUE = 200; set_hex(BLUE, "#89b4fa")
            MAUVE = 201; set_hex(MAUVE, "#cba6f7")
            GREEN = 202; set_hex(GREEN, "#a6e3a1")
            PEACH = 203; set_hex(PEACH, "#fab387")
            RED = 204; set_hex(RED, "#f38ba8")
            SURFACE1 = 205; set_hex(SURFACE1, "#45475a")
            OVERLAY0 = 206; set_hex(OVERLAY0, "#6c7086")
            BASE = 207; set_hex(BASE, "#1e1e2e")

            curses.init_pair(1, MAUVE, -1)
            curses.init_pair(2, GREEN, -1)
            curses.init_pair(3, PEACH, -1)
            curses.init_pair(4, BLUE, -1)
            curses.init_pair(5, OVERLAY0, -1)
            curses.init_pair(6, BASE, BLUE)
            curses.init_pair(7, RED, SURFACE1)
            curses.init_pair(8, BLUE, -1)
            curses.init_pair(9, PEACH, SURFACE1)
        else:
            raise Exception()
    except:
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_BLUE, -1)
        curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_WHITE)

def draw_logo(stdscr, start_y, max_x):
    for i, line in enumerate(LOGO):
        x = (max_x - len(line)) // 2
        stdscr.addstr(start_y + i, x, line, curses.color_pair(8) | curses.A_BOLD)
    return start_y + len(LOGO) + 2

def parse_github_url(url):
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    parts = url.split('/')
    try:
        idx = parts.index("github.com")
        return parts[idx + 1], parts[idx + 2]
    except (ValueError, IndexError):
        return None, None

def fetch_tree_data(owner, repo):
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'gitdown-script'})
    try:
        with urllib.request.urlopen(req) as response:
            repo_data = json.loads(response.read().decode())
            branch = repo_data.get('default_branch', 'main')
    except Exception as e:
        return None, str(e)

    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    req = urllib.request.Request(tree_url, headers={'User-Agent': 'gitdown-script'})
    try:
        with urllib.request.urlopen(req) as response:
            tree_data = json.loads(response.read().decode())
            return branch, tree_data.get('tree', [])
    except Exception as e:
        return None, str(e)

def get_selection_state(item_path, item_type, selected_paths):
    for sel in selected_paths:
        if item_path == sel or item_path.startswith(sel + '/'):
            return 2
    if item_type == 'tree':
        for sel in selected_paths:
            if sel.startswith(item_path + '/'):
                return 1
    return 0

def prompt_input(stdscr):
    curses.curs_set(1)
    input_str = ""
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        logo_bottom = draw_logo(stdscr, max_y // 4 - 2, max_x)
        
        box_w = min(80, max_x - 4)
        start_x = (max_x - box_w) // 2
        input_y = logo_bottom + 3
        
        stdscr.addstr(input_y, start_x, "   Enter GitHub Repository URL ", curses.color_pair(4) | curses.A_BOLD)
        
        stdscr.addstr(input_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
        stdscr.addstr(input_y + 2, start_x, "│ ", curses.color_pair(5))
        
        stdscr.addstr(input_y + 2, start_x + 2, input_str.ljust(box_w-4), curses.color_pair(1))
        
        stdscr.addstr(input_y + 2, start_x + box_w - 2, " │", curses.color_pair(5))
        stdscr.addstr(input_y + 3, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
        
        stdscr.move(input_y + 2, start_x + 2 + len(input_str))
        stdscr.refresh()
        
        c = stdscr.getch()
        if c in (curses.KEY_ENTER, 10, 13):
            break
        elif c in (curses.KEY_BACKSPACE, 8, 127) and len(input_str) > 0:
            input_str = input_str[:-1]
        elif 32 <= c <= 126 and len(input_str) < box_w - 5:
            input_str += chr(c)
            
    curses.curs_set(0)
    return input_str.strip()

def prompt_choice(stdscr, options):
    current_idx = 0
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        logo_bottom = draw_logo(stdscr, max_y // 4 - 2, max_x)
        
        box_w = 46
        start_x = (max_x - box_w) // 2
        start_y = logo_bottom + 3
        
        stdscr.addstr(start_y, start_x, " 󰧚  Select Download Mode ", curses.color_pair(4) | curses.A_BOLD)
        
        stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
        stdscr.addstr(start_y + 2, start_x, f"│{' ' * (box_w-2)}│", curses.color_pair(5))
        
        for i, opt in enumerate(options):
            icon_label = f"  {opt['icon']}  {opt['label']} ".ljust(box_w - 6)
            key_str = f"{opt['key']} "
            y_pos = start_y + 3 + i
            
            if i == current_idx:
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                stdscr.addstr(y_pos, start_x + 2, icon_label, curses.color_pair(7) | curses.A_BOLD)
                stdscr.addstr(y_pos, start_x + 2 + len(icon_label), key_str, curses.color_pair(9) | curses.A_BOLD)
                stdscr.addstr(y_pos, start_x + 2 + len(icon_label) + len(key_str), " │", curses.color_pair(5))
            else:
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                stdscr.addstr(y_pos, start_x + 2, icon_label, curses.color_pair(1))
                stdscr.addstr(y_pos, start_x + 2 + len(icon_label), key_str, curses.color_pair(3))
                stdscr.addstr(y_pos, start_x + 2 + len(icon_label) + len(key_str), " │", curses.color_pair(5))
                
        stdscr.addstr(start_y + 3 + len(options), start_x, f"│{' ' * (box_w-2)}│", curses.color_pair(5))
        stdscr.addstr(start_y + 4 + len(options), start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
                
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(options) - 1:
            current_idx += 1
        elif c in (curses.KEY_ENTER, 10, 13):
            return current_idx

def tui_loop(stdscr, owner, repo, branch, tree_items):
    current_dir = ""
    selected_paths = set()
    cursor_idx = 0
    scroll_offset = 0

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        display_items = []
        if current_dir != "":
            display_items.append({"path": "..", "type": "up", "name": ".."})
            
        for item in tree_items:
            item_dir = os.path.dirname(item['path'])
            if item_dir == current_dir:
                display_items.append({
                    "path": item['path'],
                    "type": item['type'],
                    "name": os.path.basename(item['path'])
                })
        
        display_items.sort(key=lambda x: (x['type'] != 'tree', x['name']))

        max_display = max_y - 4
        if cursor_idx < scroll_offset:
            scroll_offset = cursor_idx
        elif cursor_idx >= scroll_offset + max_display:
            scroll_offset = cursor_idx - max_display + 1

        try:
            header = f"  {owner}/{repo}  |   {branch}  |   /{current_dir} "
            stdscr.addstr(0, 0, header.ljust(max_x - 1), curses.color_pair(6) | curses.A_BOLD)
            
            for i in range(max_display):
                item_idx = i + scroll_offset
                if item_idx >= len(display_items):
                    break
                    
                item = display_items[item_idx]
                y_pos = i + 2
                
                state = get_selection_state(item['path'], item['type'], selected_paths)
                
                if item['type'] == 'up':
                    checkbox = "   "
                    icon = "󰜣"
                elif item['type'] == 'tree':
                    checkbox = "[x]" if state == 2 else "[-]" if state == 1 else "[ ]"
                    icon = ""
                else:
                    checkbox = "[x]" if state == 2 else "[ ]"
                    icon = ""
                    
                display_name = f"{icon} {item['name']}/" if item['type'] == 'tree' else f"{icon} {item['name']}"
                
                stdscr.addstr(y_pos, 0, " " * (max_x - 1))

                if item_idx == cursor_idx:
                    line_text = f" {checkbox}  {display_name}"
                    if len(line_text) > max_x - 2:
                        line_text = line_text[:max_x - 5] + "..."
                    stdscr.addstr(y_pos, 0, line_text.ljust(max_x - 1), curses.color_pair(7) | curses.A_BOLD)
                else:
                    cb_str = f" {checkbox}  "
                    if state == 2:
                        cb_attr = curses.color_pair(2) | curses.A_BOLD
                    elif state == 1:
                        cb_attr = curses.color_pair(3) | curses.A_BOLD
                    else:
                        cb_attr = curses.color_pair(5)
                        
                    stdscr.addstr(y_pos, 0, cb_str, cb_attr)
                    
                    name_str = display_name
                    if item['type'] == 'tree' or item['type'] == 'up':
                        name_attr = curses.color_pair(4) | curses.A_BOLD
                    else:
                        name_attr = curses.color_pair(1)
                        
                    max_name_len = (max_x - 1) - len(cb_str)
                    if len(name_str) > max_name_len:
                        name_str = name_str[:max_name_len-3] + "..."
                        
                    stdscr.addstr(y_pos, len(cb_str), name_str, name_attr)

            footer = " [SPACE] Select  |  [ENTER] Open Dir  |  [q] Go Back / Finish "
            stdscr.addstr(max_y - 1, 0, footer.ljust(max_x - 1), curses.color_pair(6) | curses.A_BOLD)
            
        except curses.error:
            pass 

        stdscr.refresh()
        key = stdscr.getch()
        
        if key == curses.KEY_UP and cursor_idx > 0:
            cursor_idx -= 1
        elif key == curses.KEY_DOWN and cursor_idx < len(display_items) - 1:
            cursor_idx += 1
        elif key == ord(' '):
            item = display_items[cursor_idx]
            if item['type'] != 'up':
                if item['path'] in selected_paths:
                    selected_paths.remove(item['path'])
                else:
                    selected_paths.add(item['path'])
        elif key in [curses.KEY_ENTER, 10, 13]:
            item = display_items[cursor_idx]
            if item['type'] == 'tree':
                current_dir = item['path']
                cursor_idx = 0
                scroll_offset = 0
            elif item['type'] == 'up':
                current_dir = os.path.dirname(current_dir)
                cursor_idx = 0
                scroll_offset = 0
        elif key == ord('q'):
            if current_dir == "":
                break 
            else:
                current_dir = os.path.dirname(current_dir)
                cursor_idx = 0
                scroll_offset = 0

    return selected_paths

def generate_links_file(owner, repo, branch, tree_items, selected_paths, out_file="links.txt"):
    files_to_download = []
    for item in tree_items:
        if item['type'] == 'blob':
            if get_selection_state(item['path'], 'blob', selected_paths) == 2:
                files_to_download.append(item)
                        
    if not files_to_download:
        return False
        
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"\nRepository : {owner}/{repo}\n")
        f.write(f"Branch     : {branch}\n")
        f.write("=" * 70 + "\n")
        
        for item in files_to_download:
            file_path = item['path']
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/refs/heads/{branch}/{file_path}"
            f.write(f"File Path : {file_path}\n")
            f.write(f"Raw Link  : {raw_url}\n")
            f.write("-" * 70 + "\n")
    return True

def run_download_ui(stdscr):
    max_y, max_x = stdscr.getmaxyx()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    p = subprocess.Popen(["./ghdown.py", "-in", "links.txt"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    
    box_w = min(80, max_x - 4)
    box_y = max_y - 6
    start_x = (max_x - box_w) // 2

    while True:
        line = p.stdout.readline()
        if not line and p.poll() is not None:
            break
            
        line = line.strip()
        if line:
            stdscr.clear()
            draw_logo(stdscr, 2, max_x)
            
            stdscr.addstr(box_y - 1, start_x, "   Downloading Files... ", curses.color_pair(4) | curses.A_BOLD)
            
            display_line = line
            if len(display_line) > box_w - 4:
                display_line = display_line[:box_w-7] + "..."
                
            stdscr.addstr(box_y, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            stdscr.addstr(box_y + 1, start_x, "│ ", curses.color_pair(5))
            stdscr.addstr(box_y + 1, start_x + 2, display_line.ljust(box_w-4), curses.color_pair(1))
            stdscr.addstr(box_y + 1, start_x + box_w - 2, " │", curses.color_pair(5))
            stdscr.addstr(box_y + 2, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            
            stdscr.refresh()
            
    stdscr.clear()
    draw_logo(stdscr, max_y // 4 - 2, max_x)
    stdscr.addstr(max_y // 2 + 2, (max_x - 23) // 2, "   Download Complete! ", curses.color_pair(2) | curses.A_BOLD)
    stdscr.refresh()
    curses.napms(1500)

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    url = prompt_input(stdscr)
    if not url: return
    
    owner, repo = parse_github_url(url)
    if not owner:
        stdscr.addstr(0, 0, " Invalid URL. Press any key to exit. ", curses.color_pair(3))
        stdscr.getch()
        return

    menu_options = [
        {"icon": "", "label": "Full Repository Download", "key": "f"},
        {"icon": "󰒉", "label": "Manual Selection (TUI)", "key": "m"}
    ]
    
    mode = prompt_choice(stdscr, menu_options)
    
    stdscr.clear()
    draw_logo(stdscr, stdscr.getmaxyx()[0] // 4 - 2, stdscr.getmaxyx()[1])
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 2, (stdscr.getmaxyx()[1] - 18) // 2, "   Fetching tree... ", curses.color_pair(4) | curses.A_BOLD)
    stdscr.refresh()

    if mode == 0:
        subprocess.run(["./ghls.py", "-link", url, "-out", "links.txt"])
        run_download_ui(stdscr)
    else:
        branch, tree_items = fetch_tree_data(owner, repo)
        if not branch:
            return
            
        selected = tui_loop(stdscr, owner, repo, branch, tree_items)
        if selected:
            if generate_links_file(owner, repo, branch, tree_items, selected, "links.txt"):
                run_download_ui(stdscr)

if __name__ == "__main__":
    curses.wrapper(main_tui)