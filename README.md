# Music Duplicate Manager

This Python script helps you find and manage potential duplicate music files in your music library. It's designed to be interactive and remember your decisions across multiple runs.

## Features

- **Fuzzy filename matching:** Uses the `fuzzywuzzy` library to identify similar filenames, even with slight variations in spelling, track numbers, etc. It lets you define your own similarity threshold.
- **Cross-folder comparison:** Compares files across different parent folders, assuming that duplicates won't exist within the same folder (e.g., the same album folder).
- **Artist name removal:** Ignores the artist name during filename comparison to prevent false positives from similar track titles with the artist name inside (if you use a storage path like /artist/album/tracks)
- **Interactive prompts:** Presents you with pairs of potentially duplicate files and lets you choose whether to:
    - Delete one of the files. (press "1" or "2" to select which)
    - Keep both files. (press "n" or "enter" directly)
    - Stop processing further pairs and store the value for the already compared pairs (press "s")
- **Persistent decision and preference storage:** Remembers your choices (delete, keep, stop) and your preferences (the similarity threshold and file path) across multiple runs using a pickle file, so you can interrupt and resume the process later.
- **Empty folders cleaning:** Show you empty folders in your library at the end of the process and let you the choice of removing them to keep your library clean.

## Requirements

- Python 3.6 or later
- `fuzzywuzzy` library: Install using `pip install fuzzywuzzy`
- `python-Levenshtein` library (optional but recommended for speed): Install using `pip install python-Levenshtein`

## Usage

1. **Save the code:** Save the provided Python code as a file (e.g., `music_duplicates_manager.py`), preferably in your music directory (you can also custom your music path when you run this script)
2. **Make it executable :**
   ```bash
   chmod +x music_duplicates_manager.py
   ```
3. **Run the script:**
   ```bash
   python music_duplicates_manager.py
   ```
   - You can set your preferences at each launch such as your music path (the path you installed the script by default) or similarity threshold (default 80) to control how similar filenames need to be to be considered duplicates.
   - You'll be prompted to make a decision for each pair of potential duplicates.
   - Press '1' to delete the first file, '2' to delete the second file, 'n' or 'enter' directly to keep both, or 's' to stop the process and keep your progress.

## Notes

- The script creates two files called `handled_pairs.pickle` (to store your decisions) and `preferences.pickle` (to store your preferences). You can safely delete these files if you want to reset the script's memory.
- Make sure you have backups of your music library before running the script, as **file deletions are permanent**.
- The script currently assumes a folder structure where artists are in top-level folders, albums are in subfolders within artist folders, and tracks are directly within album folders. If your structure is different, you might need to modify the code accordingly.
