import tgt
from getConfig import get_config
import os
from pydub import AudioSegment
import pandas as pd
import re
        
def filename_from_dir(dir_path, starts_with=None, ends_with=None):
    dir = os.fsencode(dir_path + '/')
    for file in os.listdir(dir):
        file_dec = os.fsdecode(file)
        filename = os.path.join(dir_path, file_dec)

        if (starts_with is None or file_dec.startswith(starts_with)) and \
           (ends_with is None or file_dec.endswith(ends_with)):
            return filename
        
def get_folder_names(directory):
    folder_names = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    return folder_names

def get_unique_name(speaker, label, start_time):
    start_time_formatted = f"{start_time}.2f"
    start_time_formatted = start_time_formatted.replace('.','_')
    return f"{speaker}_{label}_{start_time_formatted}"

class LabelMetadata:
    def __init__(self):
        self.metadata = {'total_count': {}}

    def add_speaker_label_count(self, speaker, label, count):
        if speaker not in self.metadata:
            self.metadata[speaker] = {}

        if label not in self.metadata[speaker]:
            self.metadata[speaker][label] = {'count': count}
        else:
            self.metadata[speaker][label]['count'] += count

        if label not in self.metadata['total_count']:
            self.metadata['total_count'][label] = count
        else:
            self.metadata['total_count'][label] += count

    def add_tier(self, speaker, label, phrase):
        count = self.get_count(speaker,label)
        count_name = f"{count:03}"
        if speaker not in self.metadata:
            self.metadata[speaker] = {}
        if label not in self.metadata[speaker]:
            self.metadata[speaker][label] = {}
        if count_name not in self.metadata[speaker][label]:
            self.metadata[speaker][label][count_name] = {'phrase': phrase}
        else:
            self.metadata[speaker][label][count_name]['phrase'] = phrase

    def add_secondtier(self, speaker, label, secondtier):
        count = self.get_count(speaker,label)
        count_name = f"{count:03}"
        if speaker not in self.metadata:
            self.metadata[speaker] = {}
        if label not in self.metadata[speaker]:
            self.metadata[speaker][label] = {}
        if count_name not in self.metadata[speaker][label]:
            self.metadata[speaker][label][count_name] = {'secondtier': secondtier}
        else:
            self.metadata[speaker][label][count_name]['secondtier'] = secondtier

    def add_start_time(self, speaker, label, start_time):
        count = self.get_count(speaker,label)
        count_name = f"{count:03}"
        if speaker not in self.metadata:
            self.metadata[speaker] = {}
        if label not in self.metadata[speaker]:
            self.metadata[speaker][label] = {}
        if count_name not in self.metadata[speaker][label]:
            self.metadata[speaker][label][count_name] = {'start_time': start_time}
        else:
            self.metadata[speaker][label][count_name]['start_time'] = start_time

    def add_end_time(self, speaker, label, end_time):
        count = self.get_count(speaker,label)
        count_name = f"{count:03}"
        if speaker not in self.metadata:
            self.metadata[speaker] = {}
        if label not in self.metadata[speaker]:
            self.metadata[speaker][label] = {}
        if count_name not in self.metadata[speaker][label]:
            self.metadata[speaker][label][count_name] = {'end_time': end_time}
        else:
            self.metadata[speaker][label][count_name]['end_time'] = end_time

    def get_count(self, speaker, label):
        return self.metadata.get(speaker, {}).get(label, {}).get('count', 0)

    def get_total_count(self, label):
        return self.metadata['total_count'].get(label, 0)
    
def cut_and_save_audio(config, start_time, end_time, speaker, label, talk, count):
    # get times in ms
    start_time_ms = start_time * 1000
    end_time_ms = end_time * 1000
    # define input file and output folder
    output_folder = config['AudioOutputPath']
    input_file_path = os.path.join(config['SoundFilePath'],talk)
    starts_with = talk + '_' + speaker
    input_file = filename_from_dir(input_file_path,starts_with=starts_with,ends_with='.wav')
    # cut audio segment
    audio = AudioSegment.from_wav(input_file)
    sliced_audio = audio[start_time_ms:end_time_ms]
    os.makedirs(output_folder, exist_ok=True)
    count_formatted = f"{count:03}"
    name = get_unique_name(speaker, label, start_time)
    output_file = os.path.join(output_folder, f"{name}.wav")
    sliced_audio.export(output_file, format="wav")

def write_to_markdown(label_metadata, config):
    audio_file_path = config['AudioOutputPath']
    markdown_file_path = os.path.join(config['ObsidianVaultPath'],config['MarkdownFileName'])
    if os.path.exists(markdown_file_path):
        user_input = input("Markdown-File exists. Do you want to overwrite? (y/n): ").strip().lower()
        if user_input == 'y':
            print("File will be overwritten.")
        else:
            copy_name_input = input("Enter name of copy: ").strip().lower()
            base_name, extension = os.path.splitext(markdown_file_path)
            markdown_file_path = f"{base_name}_{copy_name_input}{extension}"
    os.makedirs(config['ObsidianVaultPath'],exist_ok=True)
    with open(markdown_file_path, 'w', encoding=config['encoding']) as md_file:
        for speaker, label_data in label_metadata.metadata.items():
            if speaker == 'total_count':
                continue
            md_file.write(f"# {speaker}\n")
            for label, items in label_data.items():
                md_file.write(f"## {label}\n")
                for item_name, item_info in items.items():
                    if item_name == 'count':
                        md_file.write(f"{item_name} = {item_info}\n")
                    else:
                        md_file.write(f"**{item_name}**\n")
                        start_time = item_info.get('start_time')
                        md_file.write(f"- start time: {start_time}\n")
                        end_time = item_info.get('end_time')
                        md_file.write(f"- end time: {end_time}\n")
                        phrase = item_info.get('phrase')
                        md_file.write(f"- phrase:\n```\n{phrase}\n```\n")
                        abs_path = os.path.abspath(audio_file_path)
                        sound_file = "file:///" + abs_path.replace('\\', '/') + "/" + speaker + "_" + label + "_" + item_name + ".wav"
                        md_file.write(f"[{label}]({sound_file})\n")
                        md_file.write("- valid: \n")
                        md_file.write("- reason: \n")


def create_excel_table(label_metadata, config):
    speakers = []
    labels = []
    counts = []
    start_times = []
    end_times = []
    phrases = []
    wav_links = []
    valids = []
    reasons = []
    number = []
    closeto = []
    glued = []
    secondtiers = []
    checknumber = 0

    for speaker, label_data in label_metadata.metadata.items():
        if speaker == 'total_count':
            continue
        for label, items in label_data.items():
            
            for item_name, item_info in items.items():
                if item_name == 'count':
                    current_count = item_info
                else:
                    checknumber += 1
                    counts.append(item_name)
                    speakers.append(speaker)
                    labels.append(label)
                    abs_path = os.path.abspath(config['AudioOutputPath'])
                    sound_file = f"file:///{abs_path.replace(os.sep, '/')}/{speaker}_{label}_{item_name}.wav"
                    wav_links.append(sound_file)
                    start_time = item_info.get('start_time')
                    start_times.append(start_time)
                    end_time = item_info.get('end_time')
                    end_times.append(end_time)
                    phrase = item_info.get('phrase')
                    secondtier = item_info.get('secondtier')
                    secondtiers.append(secondtier)
                    phrases.append(phrase)
                    valids.append('')
                    reasons.append('')
                    closeto.append('')
                    glued.append('')
                    number.append(checknumber)

    df = pd.DataFrame({
        'Checknumber': number,
        'Speaker': speakers,
        'Label': labels,
        'Count': counts,
        'Start time': start_times,
        'End time': end_times,
        'WAV_Link': wav_links,
        'Valid': valids,
        'Reason': reasons,
        'Close to': closeto,
        'Glued': glued,
        'Other DF': glued,
        'Multi-FP': glued,
        'FP-length': glued,
        'Struct. cont.': glued,
        'Dis. type': glued,
        'Anneliese, HELP!': glued,
        'ManualCorrectionOrtho': glued,
        'Word2Word': glued,
        'Phrase': phrases,
        'PCOMP': secondtiers
    })

    excel_output_path = os.path.join(config['ExcelPath'], config['ExcelFileName'])
    if os.path.exists(excel_output_path):
        user_input = input("Excel-File exists. Do you want to overwrite? (y/n): ").strip().lower()
        if user_input == 'y':
            print(f"{excel_output_path} has been overwritten.")
        else:
            copy_name_input = input("Enter name-extension of copy: ").strip().lower()
            base_name, extension = os.path.splitext(excel_output_path)
            excel_output_path = f"{base_name}_{copy_name_input}{extension}"
    df.to_excel(excel_output_path, index=False)

def extract_text(config_name):
    # get contents of config text-file
    config = get_config(config_name)
    # check if necessary key-words are contained within config
    expected_keys = ['TextGridPath','SoundFilePath','encoding','tier','SpeakerID','labels','deltatime']
    for key in expected_keys:
        if key not in config:
            raise KeyError(f'Expected keyword {key} not in config.')
    # get labels into list
    labels = config['labels'].split()
    # extract the tiername for both speakers involved
    if config['SpeakerID'] == 'all':
        talks = get_folder_names(config['TextGridPath'])
        # print(talks)
    else:
        talks = config['SpeakerID'].split()
    
    # initialize label info
    label_metadata = LabelMetadata()

    for talk in talks:
        # safety check; directory name must match this pattern
        if not re.match(r"(\d{3}[MF]){2}", talk):
            continue;
        # get filename from config keys
        dir_path = os.path.join(config['TextGridPath'],talk)
        filename = filename_from_dir(dir_path,'','.TextGrid')
        # read textgrid using tgt
        textgrid = tgt.io.read_textgrid(filename,encoding=config['encoding'])
        # get all tiernames of the TextGrid object
        tiernames = textgrid.get_tier_names()
        speakers = []
        speakers.append(talk[:4])
        speakers.append(talk[-4:])
        # do for both speakers
        for speaker in speakers:
            print(speaker)
            # if tier name is ortho, get the randomass name given by a system
            if config['tier'] == 'ortho':
                tiername = [name for name in tiernames if name.startswith(speaker)]
                tiername = tiername[0]
                # print(tiername)
            else:
                tiername = speaker + '-' + config['tier']
            # get index for Intervaltier PCOMP
            secondtier_found = 0
            if config['secondtier']:
                for idx, tier in enumerate(textgrid.tiers):
                    if tier.name == speaker + '-' + config['secondtier']:
                        secondtier_idx = idx
                        secondtier_found = 1
                    
            if secondtier_found == 1:
                secondtier_annotations = textgrid.tiers[secondtier_idx].annotations
            else:
                print(f"Speaker {speaker} has no PCOMP tier.")
            # get tier according to name
            for IntervalTier in textgrid.tiers:
                if tiername == IntervalTier.name:
                    for label in labels:
                        for index, annotation in enumerate(IntervalTier.annotations):
                            phrase = ''
                            secondtier = ''
                            annotationflag = 0
                            for word in annotation.text.split():
                                if word == label and annotationflag == 0:
                                    annotationflag = 1 # if in the same annotation a label is found more than once
                                    phrase += ' ' + annotation.text
                                    
                                    # get start time for extraction
                                    start_string = annotation.start_time - config['deltatime']
                                    if start_string < 0:
                                        start_string = 0 
                                    end_string = annotation.end_time + config['deltatime']
                                    label_metadata.add_speaker_label_count(speaker, word, 1)
                                    
                                    # get all annotations within the defined time interval
                                    # backwards:
                                    backflag = 1
                                    backcount = 0
                                    while backflag == 1:
                                        backcount += 1
                                        if IntervalTier.annotations[index - backcount].end_time >= start_string:
                                            phrase = IntervalTier.annotations[index - backcount].text + ' ' + phrase
                                        else:
                                            backflag = 0
                                    
                                    # forwards:
                                    forwardflag = 1
                                    forwardcount = 0
                                    while forwardflag == 1:
                                        forwardcount += 1
                                        if IntervalTier.annotations[index + forwardcount].start_time <= end_string:
                                            phrase += ' ' + IntervalTier.annotations[index + forwardcount].text
                                        else:
                                            forwardflag = 0
                                    # get pcomp annotations
                                    if secondtier_found == 1:
                                        i = 0
                                        start_pcomp = 0
                                        while start_pcomp <= end_string:
                                            if len(secondtier_annotations[i:]) == 0:
                                                break
                                            end_comp = secondtier_annotations[i].end_time
                                            start_pcomp = secondtier_annotations[i].start_time
                                            if end_comp >= start_string:
                                                secondtier += ' ' + secondtier_annotations[i].text
                                            i += 1
                                    # add phrase to struct
                                    label_metadata.add_tier(speaker,label,phrase)
                                    # add pcomp to struct
                                    label_metadata.add_secondtier(speaker,label,secondtier)
                                    # add start time and end time
                                    label_metadata.add_start_time(speaker,label,start_string)
                                    label_metadata.add_end_time(speaker,label,end_string)
                                    # cut audio
                                    if config['ExtractAudio'] == 'yes':
                                        cut_and_save_audio(config, start_string, end_string, speaker, label, talk, label_metadata.get_count(speaker,label))
                                    
                                    

                    break # break once the right level has been found
            
    # TODO: extract Obsidian File
    if config['ExtractObsidian'] == 'yes':
        write_to_markdown(label_metadata,config)
    # TODO: extract Excel file
    if config['ExtractExcel'] == 'yes':
        create_excel_table(label_metadata, config)
    # TODO: extract single text files
    # if config['ExtractText'] == 'yes':
    #     create_txt_file(label_metadata, config)
    return label_metadata

def main():
    config_name = 'own_tools/config.txt'
    # config_name = 'own_tools/config_saskia.txt'
    label_metadata = extract_text(config_name)
    config = get_config(config_name)
    for label in config['labels'].split():
        print(f'{label}: {label_metadata.get_total_count(label)}')
    print(f'{label_metadata.get_count("038F","ähm")}')

if __name__ == '__main__':
    main()