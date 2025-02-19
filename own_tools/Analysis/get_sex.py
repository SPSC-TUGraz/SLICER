import os

path = r"C:\Users\Lucas Eckert\Nextcloud2\Shared\TRaehX_Stimuli\experiment\trAEHx\soundSamples\AlleTypen_3.0"
female = 0
male = 0
for file in os.listdir(path):
    firstpart = file.split("_")[0]
    if firstpart.endswith("F"):
        female += 1
    else:
        male += 1
print(f"female: {female/8}; male: {male/8}")