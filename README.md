# ⚡ gitdown

A simple, fast, and smart tool designed to solve a common developer headache: **downloading specific files or directories from a massive GitHub repository without cloning the entire thing.** Following the KISS principle, if you have a 2GB repository but only need 10 files (totaling 1MB), `gitdown` lets you fetch exactly what you need instantly. It preserves the original directory structure, saving your bandwidth and time by bypassing the entire Git history download.

## ✨ Features

* **Selective Download:** Browse the repository tree and precisely pick only the files or folders you need.
* **No Git Required:** The tool operates entirely via the GitHub API, fetching raw files directly. No `git` installation or complex dependencies are needed on your system.
* **Interactive TUI:** A sleek, terminal-based User Interface built with `curses`. It features a comfortable Catppuccin color scheme, allowing you to easily navigate and select items using just your keyboard.
* **CLI & Interactive Mode:** Run operations via direct commands, or drop into the interactive mode to convert URLs and download items step-by-step.
* **Preserves Directory Structure:** When downloading subdirectories or specific files, the tool automatically creates the necessary local folders to keep everything organized exactly as it was in the original repository.

## 🛠️ How it Works

1. **Fetch the Tree:** Connects to the GitHub API to recursively read the repository's file structure.
2. **View & Select:** Displays the repository tree in the TUI, allowing you to check/uncheck the files you want using the `SPACE` bar.
3. **Direct Download:** Converts the selected paths into raw links and downloads them instantly using standard Python libraries.

## 📂 Project Structure

For those looking to explore the code or contribute:
* `gitdown.py`: The main entry point and terminal user interface (TUI).
* `ghls.py`: Responsible for fetching and parsing the repository tree.
* `ghdown.py`: Handles the downloading process and builds local directories.
* `ghconvert.py` / `ghget.py`: Utility scripts for parsing and converting standard GitHub URLs to raw links.