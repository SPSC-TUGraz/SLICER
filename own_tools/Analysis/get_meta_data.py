import os
import csv
import pandas as pd

def list_categories(file, meta_dict):
    index = 0
    indexes = []
    names = {}
    with open(file, 'r', newline='\n', encoding='utf-8') as open_file:
        csvfile = csv.reader(open_file, delimiter=',')
        first_flag = 0
        for row in csvfile:
            index = 0
            for word in row:    
                if first_flag == 0:
                    # print(f"{index}: {word}")
                    if (word.endswith('.response') or word.endswith('.text')) and ('Exposure' not in word) and ('Terms' not in word) and ('Rating' not in word):
                        indexes.append(index)
                        names[index] = word
                        if word not in meta_dict:
                            meta_dict[word] = []
                else:
                    if (word != '') and (index in indexes):
                        meta_dict[names[index]].append(word)
                index += 1
            first_flag = 1
        return meta_dict

def main():
    path = r"C:\Users\Lucas Eckert\Nextcloud2\Shared\TRaehX_Stimuli\experiment\results\all"
    meta_dict = {}
    
    # Process each CSV file
    for file in os.listdir(path):
        if file.endswith(".csv"):
            meta_dict = list_categories(os.path.join(path, file), meta_dict)

    # Convert the meta_dict to a DataFrame
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in meta_dict.items()]))

    # Save DataFrame to an Excel file
    output_path = r"meta_dict_output.xlsx"
    df.to_excel(output_path, index=False, engine='openpyxl')

if __name__ == "__main__":
    main()