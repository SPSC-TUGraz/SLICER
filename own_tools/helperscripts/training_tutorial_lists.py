import os
import random
import pandas as pd

def list_files(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append(file)
    return file_list

traininglist = []
trainingchunkID = []
directory = 'soundSamples'
# types = 'training_ecki'
types = 'tutorial_ecki'
dir_path = os.path.join(directory, types)
print(dir_path)

file_list = list_files(dir_path)
for filename in file_list:
    if filename.endswith('.wav'):
        traininglist.append(os.path.join(dir_path, filename))
for filename in traininglist:
    filename = filename.split('\\')[-1]
    parts = filename.split('_')
    list_name = f"{parts[0]}_{parts[1]}_{parts[2]}"
    trainingchunkID.append(list_name)

df1 = pd.DataFrame({'chunk_id': trainingchunkID, 'path_incomplete_structure': traininglist})

excel_path = ''
# df1.to_excel(os.path.join(excel_path,'ConditionsFileTraining_ecki.xlsx'), index=False)
df1.to_excel(os.path.join(excel_path,'ConditionsFileTutorial_ecki.xlsx'), index=False)
