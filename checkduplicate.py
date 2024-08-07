import os
from fuzzywuzzy import fuzz
import pickle
import hashlib
import re

def calculate_pair_id(file1, file2):
    """Calculates a unique ID for a file pair based on their filenames."""
    combined_name = file1 + file2
    return hashlib.md5(combined_name.encode()).hexdigest()

def find_similar_music_filenames(directory, similarity_threshold=80):
    """Interactively finds and handles similar music files,
    remembering decisions across runs using file pair IDs.
    Compares files across different parent folders only,
    removing artist name and leading track numbers from filename comparison.

    Args:
        directory: The directory to search.
        similarity_threshold: Minimum similarity ratio (0-100) for filename similarity.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    handled_pairs_file = os.path.join(script_dir, "handled_pairs.pickle")
    preferences_file = os.path.join(script_dir, "preferences.pickle")

    already_handled = set()
    if os.path.exists(handled_pairs_file):
        with open(handled_pairs_file, "rb") as f:
            already_handled = pickle.load(f)

    # Load preferences
    preferences = {"similarity_threshold": 80, "music_folder": directory}
    if os.path.exists(preferences_file):
        with open(preferences_file, "rb") as f:
            preferences = pickle.load(f)
    else:
        with open(preferences_file, "wb") as f:
            pickle.dump(preferences, f)

    similarity_threshold = preferences["similarity_threshold"]
    music_directory = preferences["music_folder"]

    # === Preferences and initial setup ===
    print(f"Current similarity threshold: {similarity_threshold}%")
    print(f"Current music folder to scan: {music_directory}")
    while True:
        choice = input("Enter: start scan / st: change similarity threshold / mf: change music folder: ").lower().strip()
        if choice in ("", "st", "mf"):
            break
        print("Invalid choice. Please press 'Enter', or enter 'st', or 'mf'.")

    if choice == "st":
        while True:
            try:
                new_threshold = int(input("Enter the new similarity threshold (0-100): "))
                if 0 <= new_threshold <= 100:
                    similarity_threshold = new_threshold
                    preferences["similarity_threshold"] = similarity_threshold
                    with open(preferences_file, "wb") as f:
                        pickle.dump(preferences, f)
                    print(f"Similarity threshold updated to {similarity_threshold}%.\nRestarting...\n")
                    find_similar_music_filenames(music_directory, similarity_threshold)
                    return
                else:
                    print("Invalid threshold. Please enter a value between 0 and 100 with anything else.")
            except ValueError:
                print("Invalid input. Please enter a number with anything else.")
    elif choice == "mf":
        new_music_folder = input("Enter the new music folder path: ")
        if os.path.isdir(new_music_folder):
            music_directory = new_music_folder
            preferences["music_folder"] = music_directory
            with open(preferences_file, "wb") as f:
                pickle.dump(preferences, f)
            print(f"Music folder updated to {music_directory}.\nYour preferences have been registered ! Restarting...\n")
            find_similar_music_filenames(music_directory, similarity_threshold)
            return
        else:
            print("Invalid folder path.")

    # === Duplicate detection and handling ===
    filenames = []
    for root, _, files in os.walk(music_directory):
        for filename in files:
            if not filename.lower().endswith(".jpg"):
                filenames.append(os.path.join(root, filename))

    duplicates = []
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            file1 = filenames[i]
            file2 = filenames[j]

            if os.path.dirname(file1) != os.path.dirname(file2):
                pair_id = calculate_pair_id(file1, file2)
                if pair_id in already_handled:
                    continue

                artist1 = os.path.basename(os.path.dirname(os.path.dirname(file1)))
                artist2 = os.path.basename(os.path.dirname(os.path.dirname(file2)))

                filename1_no_artist = re.sub(rf"\b{artist1}\b", "", os.path.basename(file1), flags=re.IGNORECASE).strip()
                filename2_no_artist = re.sub(rf"\b{artist2}\b", "", os.path.basename(file2), flags=re.IGNORECASE).strip()

                filename1_cleaned = re.sub(r"^\s*\d+\s*[-.]?\s*", "", filename1_no_artist, flags=re.IGNORECASE).strip()
                filename2_cleaned = re.sub(r"^\s*\d+\s*[-.]?\s*", "", filename2_no_artist, flags=re.IGNORECASE).strip()

                ratio = fuzz.ratio(
                    os.path.splitext(filename1_cleaned)[0],
                    os.path.splitext(filename2_cleaned)[0],
                )
                if ratio >= similarity_threshold:
                    duplicates.append((file1, file2, ratio, pair_id))

    if not duplicates:
        print("No new similar music filenames found (excluding cover .jpg files).")
    else:
        print(f"Found {len(duplicates)} potential duplicate track pairs (excluding covers .jpg files).\n")
        stop_processing = False
        for file1, file2, ratio, pair_id in duplicates:
            if stop_processing:
                break

            print("-" * 40)
            print(f"File 1: {file1}")
            print(f"File 2: {file2}")
            print(f"Similarity: {ratio}%")

            while True:
                choice = input("Choose action (1=delete file1, 2=delete file2, n/enter=keep both, s=stop): ").lower().strip()
                if choice in ("1", "2", "n", "s", ""):
                    break
                print("Invalid choice. Please enter '1', '2', 'n', directly 'Enter' or 's' .")

            if choice == "1":
                os.remove(file1)
                print(f"Deleted: {file1}")
                already_handled.add(pair_id)
            elif choice == "2":
                os.remove(file2)
                print(f"Deleted: {file2}")
                already_handled.add(pair_id)
            elif choice == "s":
                stop_processing = True
            else:  # choice == "n" or "" (empty input)
                already_handled.add(pair_id)

        with open(handled_pairs_file, "wb") as f:
            pickle.dump(already_handled, f)

    # === Empty folder removal ===
    empty_folders = []
    for root, dirs, files in os.walk(music_directory, topdown=False):
        for dir in dirs:
            full_dir_path = os.path.join(root, dir)
            if not os.listdir(full_dir_path):
                empty_folders.append(full_dir_path)

    if empty_folders:
        print("\nScan is done ! \nThe following empty folders were found:")
        for folder in empty_folders:
            print(folder)

        while True:
            confirm = input("Do you want to remove these folders? (y/n): ").lower().strip()
            if confirm in ("y", "n"):
                break
            print("Invalid choice. Please enter 'y' or 'n'.")

        if confirm == "y":
            for folder in empty_folders:
                os.rmdir(folder)
                print("These folders have been removed.")
    else:
        print("\nNo empty folders found.")

if __name__ == "__main__":
    music_directory = os.path.abspath(os.path.dirname(__file__))  # Use script's directory as default
    find_similar_music_filenames(music_directory)
