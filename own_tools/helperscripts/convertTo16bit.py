import os
import soundfile as sf

directory = r'C:\Users\Lucas Eckert\Desktop\Documenti\Graz\TI-Projekt\experiment\trAEHx\soundSamples\Typ4_3.0'

for filename in os.listdir(directory):
    if filename.endswith(".wav"):
        filepath = os.path.join(directory, filename)
        
        data, samplerate = sf.read(filepath)
        
        sf.write(filepath, data, samplerate, subtype='PCM_16')