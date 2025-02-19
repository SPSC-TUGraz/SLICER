import os
import random
import pandas as pd

def list_files(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append(file)
    return file_list

group1list = []
group2list = []
group3list = []
group1chunkID = []
group2chunkID = []
group3chunkID = []
typenames = ['Typ1_3.0','Typ2_3.0','Typ4_3.0']
gmc = 0
directory = 'soundSamples'
i = 0
flag = 0
for ii, types in enumerate(typenames):
    dir_path = os.path.join(directory, types)
    print(dir_path)
    file_list = list_files(dir_path)
    for filename in file_list:
        # if (filename.endswith('ganz_mit.wav') and i == 0) or (filename.endswith('ganz_ohne.wav') and i == 1) or ((filename.endswith('vorn_mit.wav') or filename.endswith('hinten_mit.wav') or filename.endswith('hinten_ohne.wav') or filename.endswith('vorn_ohne.wav')) and i == 2):
        #     group1list.append(os.path.join(dir_path, filename))
        # elif (filename.endswith('ganz_mit.wav') and i == 2) or (filename.endswith('ganz_ohne.wav') and i == 0) or ((filename.endswith('vorn_mit.wav') or filename.endswith('hinten_mit.wav') or filename.endswith('hinten_ohne.wav') or filename.endswith('vorn_ohne.wav')) and i == 1):
        #     group2list.append(os.path.join(dir_path, filename))
        # elif (filename.endswith('ganz_mit.wav') and i == 1) or (filename.endswith('ganz_ohne.wav') and i == 2) or ((filename.endswith('vorn_mit.wav') or filename.endswith('hinten_mit.wav') or filename.endswith('hinten_ohne.wav') or filename.endswith('vorn_ohne.wav')) and i == 0):
        #     group3list.append(os.path.join(dir_path, filename))
        if filename.endswith('.wav'):
            # print(i%3)
            if i%3 == 0:
                group1list.append(os.path.join(dir_path, filename))
            elif i%3 == 1:
                group2list.append(os.path.join(dir_path, filename))
            elif i%3 == 2:
                group3list.append(os.path.join(dir_path, filename))
            if ('hinten' in filename) or ('vorn' in filename):
                if flag == 0:
                    flag = 1
                else:
                    i -= 1
                    flag = 0
            else:
                i += 1

random.seed(45)
random.shuffle(group1list)
random.shuffle(group2list)
random.shuffle(group3list)

for filename in group1list:
    filename = filename.split('\\')[-1]
    parts = filename.split('_')
    list_name = f"{parts[0]}_{parts[1]}_{parts[2]}"
    group1chunkID.append(list_name)
for filename in group2list:
    filename = filename.split('\\')[-1]
    parts = filename.split('_')
    list_name = f"{parts[0]}_{parts[1]}_{parts[2]}"
    group2chunkID.append(list_name)
for filename in group3list:
    filename = filename.split('\\')[-1]
    parts = filename.split('_')
    list_name = f"{parts[0]}_{parts[1]}_{parts[2]}"
    group3chunkID.append(list_name)

# group1list.insert(0, 'path_incomplete_structure')
# group2list.insert(0, 'path_incomplete_structure')
# group3list.insert(0, 'path_incomplete_structure')
# group1chunkID.insert(0, 'chunk_id')
# group2chunkID.insert(0, 'chunk_id')
# group3chunkID.insert(0, 'chunk_id')

print(len(group1list))
print(len(group2list))
print(len(group3list))
print(gmc)

df1 = pd.DataFrame({'chunk_id': group1chunkID, 'path_incomplete_structure': group1list})
df2 = pd.DataFrame({'chunk_id': group2chunkID, 'path_incomplete_structure': group2list})
df3 = pd.DataFrame({'chunk_id': group3chunkID, 'path_incomplete_structure': group3list})

# excel_path = os.path.join('experiment','trAEHx')
excel_path = ''
df1.to_excel(os.path.join(excel_path,'ConditionsFile0_ecki.xlsx'), index=False)
df2.to_excel(os.path.join(excel_path,'ConditionsFile1_ecki.xlsx'), index=False)
df3.to_excel(os.path.join(excel_path,'ConditionsFile2_ecki.xlsx'), index=False)