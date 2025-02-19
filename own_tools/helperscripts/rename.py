import os

def rename_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".wav") or filename.endswith(".TextGrid"):
            parts = filename.split('_')
            new_name = f"{parts[1]}_{parts[5]}_{parts[6]}_{parts[7]}_{parts[8]}"
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_name)
            os.rename(old_file, new_file)
            print(f"Renamed: {filename} to {new_name}")

directory = r'C:\Users\Lucas Eckert\Desktop\Documenti\Graz\TI-Projekt\experiment\trAEHx\soundSamples\tutorial_ecki'
rename_files(directory)