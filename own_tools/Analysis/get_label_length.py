import textgrid
import numpy as np
import os
import pandas as pd

def load_textgrids_from_folder(path, tiername):
    textgrid_dict = {}
    counter = 0
    
    for file in os.listdir(path):
        if file.endswith("ganz_mit.TextGrid"):
            tg = textgrid.TextGrid.fromFile(os.path.join(path, file))
            for tier in tg:
                if tiername in tier.name:
                    textgrid_dict[counter] = {tier.name: tier}
                    counter += 1

    return textgrid_dict

def get_lengths_of_labels(textgrid_dict, labels):
    label_lengths = {label: {'direct': [], 'between': []} for label in labels}
    
    for counter, textgrids in textgrid_dict.items():
        for tier_name, tier in textgrids.items():
            for i, interval in enumerate(tier):
                if interval.mark in labels:
                    label = interval.mark
                    
                    # Direct length
                    direct_length = interval.maxTime - interval.minTime
                    label_lengths[label]['direct'].append(direct_length)
                    
                    # Between-label length
                    prev_end = interval.minTime if i == 0 else tier[i-1].maxTime
                    next_start = interval.maxTime if i == len(tier)-1 else tier[i+1].minTime
                    between_length = next_start - prev_end
                    label_lengths[label]['between'].append(between_length)

    return label_lengths

def write_lengths_to_excel(label_lengths, filename):
    # Initialisiere eine leere Liste, um die Daten in Tabellenform zu speichern
    data = []
    
    # Durchlaufe das Dictionary und extrahiere die Daten
    for label, lengths in label_lengths.items():
        for direct_length, between_length in zip(lengths['direct'], lengths['between']):
            data.append({'Label': label, 'Direct Length': direct_length, 'Between Length': between_length})
    
    # Erstelle ein DataFrame aus den Daten
    df = pd.DataFrame(data)
    
    # Berechne Mittelwert und Standardabweichung für jedes Label
    stats = df.groupby('Label').agg(Count=('Direct Length', 'size'),
                                    Mean=('Direct Length', 'mean'),
                                    Std=('Direct Length', 'std')).reset_index()
    
    # Füge eine Zeile für die Gesamtsumme hinzu
    total_stats = pd.DataFrame({
        'Label': ['all'],
        'Count': [df['Direct Length'].count()],
        'Mean': [df['Direct Length'].mean()],
        'Std': [df['Direct Length'].std()]
    })
    stats = pd.concat([stats, total_stats], ignore_index=True)

    # Schreibe das DataFrame und die Statistiken in separate Blätter der Excel-Datei
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='Lengths', index=False)
        stats.to_excel(writer, sheet_name='Statistics', index=False)

def main():
    path = r"C:\Users\Lucas Eckert\Nextcloud2\Shared\TRaehX_Stimuli\experiment\trAEHx\soundSamples\AlleTypen_3.0"
    tiername = "word-FA"
    labels = ['äh', 'ähm', 'ahm']
    
    # Lade die TextGrid-Daten und berechne die Label-Längen
    textgrid_dict = load_textgrids_from_folder(path, tiername)
    label_lengths = get_lengths_of_labels(textgrid_dict, labels)
    
    # Schreibe die Längen in eine Excel-Datei
    output_filename = "All_label_lengths.xlsx"
    write_lengths_to_excel(label_lengths, output_filename)
    
    print(f"Label lengths successfully written to {output_filename}")

if __name__ == "__main__":
    main()