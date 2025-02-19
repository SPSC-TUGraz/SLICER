"""
created 240109 by Ecki. Get utterances found with grasstools-andre into a txt document for readability. A whole folder is looked through.
"""
import os

def go_through_dir(dir_path,includes):
    extract = ""
    dir = os.fsencode(dir_path)
    for file in os.listdir(dir):
        file_dec = os.fsdecode(file)
        filename = dir_path + file_dec
        if includes in filename:
            if filename.endswith(".TextGrid"):
                extracted_strings = extract_strings_from_file(filename)
                extract = extract + file_dec + ":" + extracted_strings + "\n\n"
    return extract

def extract_strings_from_file(file_path):
    extracted_strings = ""
    count = 0
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            count += 1
            if ('"' in line) & (count > 3):
                line = line.lstrip('"')
                line = line.rstrip('\n')
                line = line.rstrip('"')
                if line == "IntervalTier":
                    line = "\n\t" + line
                    tier_flag = 1
                else:
                    if tier_flag == 1:
                        line = line + ":" + "\n\t\t"
                        tier_flag = 0
                
                extracted_strings = extracted_strings + " " + line

    return extracted_strings

if __name__ == "__main__":
    dir_path = "C:/Users/Lucas Eckert/Desktop/Documenti/Graz/TI-Projekt/extract/"
    includes = "011M"
    extract = go_through_dir(dir_path,includes)
    with open(dir_path + "textract.txt", 'w', encoding="utf-8") as f:
        f.write(extract)