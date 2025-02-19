import os
import sys
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.transforms
import textgrid
from scipy.io import wavfile
from scipy.signal import resample
import numpy as np
import sounddevice as sd
import matplotlib
import textwrap
import idlelib.tooltip as tt
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
import pickle
import re
import webbrowser

class Slicer:
    def __init__(self, root):    
        # init window and title
        self.root = root
        self.root.title("Slicer TNT - untitled project")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # init menu bar
        self.create_menubar()

        # init frame in window
        self.create_mainframe()

    def create_mainframe(self):
        self.mainframe = Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky="nsew")
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_rowconfigure(0, weight=1)
        
        # init button frame
        self.button_frame = Frame(self.mainframe)
        self.button_frame.grid(column=1,row=5,columnspan=2,rowspan=2,sticky="nw")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(0, weight=1)

        # init checkboxframe text
        Label(self.mainframe,text="Textgrids to show:").grid(column=4,row=0)

        # # init export button frame
        # self.exp_button_frame = Frame(self.mainframe)
        # self.exp_button_frame.grid(column=3,row=8)

        # add start time and end time entry
        self.startendtime_frame = Frame(self.mainframe,relief="groove")
        self.startendtime_frame.grid(column=0,row=3,rowspan=2,columnspan=2,sticky="nsew")
        self.starttime = StringVar()
        self.start_entry = Entry(self.startendtime_frame, width=10, textvariable=self.starttime)
        self.start_entry.grid(column=1, row=3, sticky='w')
        Label(self.startendtime_frame, text="Start: ").grid(column=0,row=3)

        self.endtime = StringVar()
        self.end_entry = Entry(self.startendtime_frame, width=10, textvariable=self.endtime)
        self.end_entry.grid(column=1, row=4, sticky='w')
        Label(self.startendtime_frame, text="End: ").grid(column=0,row=4)

        # add button to refresh wav and tg slice
        refresh_button = Button(self.startendtime_frame, text="Refresh Figure", command=self.refresh_fig)
        refresh_button.grid(column=0,row=5)
        tt.Hovertip(refresh_button, text='Refresh the figure plot.\nManipulation changes will only be\napplied upon pressing the other button')

        # add button to save times
        Button(self.startendtime_frame,text="Save times",command=self.savetimes).grid(column=1,row=5)
        self.timesave_frame = Frame(self.mainframe,relief="groove")
        self.timesave_frame.grid(column=2,row=3,rowspan=2, sticky="nsew")
        self.timesave_frame.grid_rowconfigure(0, weight=1)
        self.timesave_frame.grid_columnconfigure(0, weight=1)
        Label(self.timesave_frame,text="Selected time frames").grid(column=0,row=0)
        self.timesave_canvas = Canvas(self.timesave_frame,width=150,height=150)
        self.timesave_canvas.grid(column=0,row=1, sticky="nsew")
        self.timesave_canvas.grid_rowconfigure(0, weight=1)
        self.timesave_canvas.grid_columnconfigure(0, weight=1)
        self.timesave_inner_frame = Frame(self.timesave_canvas)
        self.timesave_inner_frame.grid(column=0,row=0,sticky="nsew")
        self.timesave_inner_frame.grid_rowconfigure(0, weight=1)
        self.timesave_inner_frame.grid_columnconfigure(0, weight=1)
        # self.timesave_frame.grid_columnconfigure(0, weight=1)
        self.timesave_scrollbar = Scrollbar(self.timesave_frame, orient=VERTICAL, command=self.timesave_canvas.yview)
        self.timesave_scrollbar.grid(column=1,row=1,sticky='nsew')
        # self.timesave_inner_frame.bind("<Configure>", lambda e: self.timesave_canvas.configure(scrollregion=self.timesave_canvas.bbox("all")))
        self.timesave_inner_frame.update_idletasks()
        self.timesave_canvas.configure(scrollregion=self.timesave_canvas.bbox("all"))

        self.timesave_canvas.create_window((0,0), window=self.timesave_inner_frame, anchor='nw')
        self.timesave_canvas.configure(yscrollcommand=self.timesave_scrollbar.set)
        self.time_count = 0
        self.saved_starttime = {}
        self.saved_endtime = {}
        self.saved_name = {}
        self.saved_export = {}
        self.time_index_count = {}
        self.savetimes_frames = {}

        # show min and max of wav and tg
        self.mintimelabel = Label(self.startendtime_frame,text='min: 0')
        self.mintimelabel.grid(column=2,row=3, sticky='e')
        self.maxtimelabel = Label(self.startendtime_frame,text='max:')
        self.maxtimelabel.grid(column=2,row=4, sticky='e')

        # init frame for time manipulation buttons
        self.starttimeframe = Frame(self.mainframe,relief="groove")
        self.starttimeframe.grid(column=0,row=8)
        self.starttimeframe.grid_columnconfigure(0, weight=1)
        self.starttimeframe.grid_rowconfigure(0, weight=1)

        self.endtimeframe = Frame(self.mainframe,relief="groove") 
        self.endtimeframe.grid(column=5,row=8)
        self.endtimeframe.grid_columnconfigure(0, weight=1)
        self.endtimeframe.grid_rowconfigure(0, weight=1)

        
        self.endplusplus = Button(self.endtimeframe,text='e++',command=lambda: self.timebuttons('e++'), width=5)
        self.endplusplus.grid(column=0,row=0,sticky=E)
        tt.Hovertip(self.endplusplus,'Add 1 sec to end')
        self.endplus = Button(self.endtimeframe,text='e+',command=lambda: self.timebuttons('e+'), width=5)
        self.endplus.grid(column=0,row=1,sticky=E)
        tt.Hovertip(self.endplus,'Add 0.05 sec to end')
        self.endminus = Button(self.endtimeframe,text='e-',command=lambda: self.timebuttons('e-'), width=5)
        self.endminus.grid(column=0,row=2,sticky=E)
        tt.Hovertip(self.endminus,'Remove 0.05 sec from end')
        self.endminusminus = Button(self.endtimeframe,text='e--',command=lambda: self.timebuttons('e--'), width=5)
        self.endminusminus.grid(column=0,row=3,sticky=E)
        tt.Hovertip(self.endminusminus,'Remove 1 sec from end')

        self.startplusplus = Button(self.starttimeframe,text='s++',command=lambda: self.timebuttons('s++'), width=5)
        self.startplusplus.grid(column=0,row=0,sticky=W)
        tt.Hovertip(self.startplusplus,'Add 1 sec to start')
        self.startplus = Button(self.starttimeframe,text='s+',command=lambda: self.timebuttons('s+'), width=5)
        self.startplus.grid(column=0,row=1,sticky=W)
        tt.Hovertip(self.startplus,'Add 0.05 sec to start')
        self.startminus = Button(self.starttimeframe,text='s-',command=lambda: self.timebuttons('s-'), width=5)
        self.startminus.grid(column=0,row=2,sticky=W)
        tt.Hovertip(self.startminus,'Remove 0.05 sec from start')
        self.startminusminus = Button(self.starttimeframe,text='s--',command=lambda: self.timebuttons('s--'), width=5)
        self.startminusminus.grid(column=0,row=3,sticky=W)
        tt.Hovertip(self.startminusminus,'Remove 1 sec from start')

        # add button to load wav and tg
        Label(self.mainframe, text="sound:").grid(column=0,row=1)
        self.wavlabel = Label(self.mainframe, text="No file.")
        self.wavlabel.grid(column=1,row=1)
        Label(self.mainframe, text="textgrid:").grid(column=0,row=2)
        self.tglabel = Label(self.mainframe, text="No file.")
        self.tglabel.grid(column=1,row=2)

        # init paths
        self.tg_file_path = None
        self.file_path = None
        # loadwav_button = Button(self.mainframe, text="Load wav", command=self.choose_wav_file)
        # loadwav_button.grid(column=1, row=1, sticky=W)
        # tt.Hovertip(loadwav_button, text='Load the wav file \nyou want to process \nalongside your textgrid file')
        # loadtg_button = Button(self.mainframe, text="Load textgrid", command=self.choose_textgrid_file)
        # loadtg_button.grid(column=1, row=2, sticky=W)
        # tt.Hovertip(loadtg_button, text='Load the textgrid file \nyou want to process \nalongside your wav file')

        
        # add button to play wav and checkbox for normalizing before playback
        Button(self.button_frame, text="Play Slice", command=self.play_wav, width=10).grid(column=1,row=0)
        Button(self.button_frame, text="Stop", command=self.stop_wav, width=5).grid(column=2,row=0)
        self.normalize_playback = BooleanVar()
        Checkbutton(self.button_frame, text="Normalize Playback", variable=self.normalize_playback).grid(column=3,row=0)

        # add checkbox for spectrogram
        self.spec_check = BooleanVar()
        Checkbutton(self.button_frame, text="Show Spectrogram", variable=self.spec_check).grid(column=1,row=1)

        # # add button for export
        # Button(self.exp_button_frame, text="Export...", command=self.export_window).grid(column=1,row=0)

        # init Figure Window
        self.fig_height = StringVar(value='4')
        self.fig_width = StringVar(value='12')
        self.figsize_frame = Frame(self.mainframe,relief="groove")
        self.figsize_frame.grid(column=4,row=5,sticky="nsew")
        self.figsize_frame.grid_columnconfigure(0, weight=1)
        self.figsize_frame.grid_rowconfigure(0, weight=1)
        Label(self.figsize_frame,text='figsize:').grid(column=6,row=0)
        Label(self.figsize_frame,text='height:').grid(column=9,row=0, sticky='w')
        Entry(self.figsize_frame,textvariable=self.fig_height,width=3).grid(column = 10, row = 0, sticky='e')
        Label(self.figsize_frame,text='width:').grid(column=7,row=0, sticky='w')
        Entry(self.figsize_frame,textvariable=self.fig_width,width=3).grid(column = 8, row = 0, sticky='e')
        
        self.figure = Figure(figsize=(float(self.fig_width.get()), float(self.fig_height.get())), dpi=100)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, master=self.mainframe)
        self.figure_canvas.get_tk_widget().grid(column=1,row=8,columnspan=4, sticky="nsew")
        self.toolbar_frame = Frame(self.mainframe,relief="groove")
        self.toolbar_frame.grid(column=1, row=9, sticky="nsew", columnspan=2)
        self.toolbar_frame.grid_columnconfigure(0, weight=1)
        self.toolbar_frame.grid_rowconfigure(0, weight=1)
        NavigationToolbar2Tk(self.figure_canvas, self.toolbar_frame)

        # add cutout canvas
        self.cutout_canvas_frame = Frame(self.mainframe,relief="groove")
        self.cutout_canvas_frame.grid(column=3,row=1,rowspan=4, sticky="nsew")
        self.cutout_canvas_frame.grid_columnconfigure(0, weight=1)
        self.cutout_canvas_frame.grid_rowconfigure(0, weight=1)
        self.cutout_canvas = Canvas(self.cutout_canvas_frame)
        self.cutout_canvas.grid(column=0,row=0, sticky="nsew")
        self.cutout_canvas.grid_columnconfigure(0, weight=1)
        self.cutout_canvas.grid_rowconfigure(0, weight=1)
        self.cutout_frame = Frame(self.cutout_canvas)
        self.cutout_frame.grid_columnconfigure(0, weight=1)
        self.cutout_frame.grid_rowconfigure(0, weight=1)
        self.cutout_scrollbar = Scrollbar(self.cutout_canvas_frame, orient=VERTICAL, command=self.cutout_canvas.yview)
        self.cutout_scrollbar.grid(column=1,row=0,sticky='nsew')
        # self.cutout_frame.bind("<Configure>", lambda e: self.cutout_canvas.configure(scrollregion=self.cutout_canvas.bbox("all")))
        self.cutout_frame.update_idletasks()
        self.cutout_canvas.configure(scrollregion=self.cutout_canvas.bbox("all"))

        self.cutout_canvas.create_window((0,0), window=self.cutout_frame, anchor='nw')
        self.cutout_canvas.configure(yscrollcommand=self.cutout_scrollbar.set)
        
        # button for adding cutout-frames
        self.add_new_cutout_button = Button(self.mainframe, text='Add new manipulation',command= lambda: self.add_cutout(index=None))
        self.add_new_cutout_button.grid(column=3,row=0,sticky='w')
        tt.Hovertip(self.add_new_cutout_button,'Add and configure \nnew frames you want \nto cut out from the \n textgrid and wav file.')
        
        # button to apply changes
        self.apply_cutout_button = Button(self.mainframe, text='Apply changes',command=self.apply_cutout)
        self.apply_cutout_button.grid(column=3,row=0,sticky='e')
        self.cutout_count = 0 # initialize the count, how many cutouts are active
        
        # lists to save the state of the cut outs
        self.cut_index_count = {}
        self.cutout_frames = {}
        self.noise_check_list = {}
        self.apply_check_list = {}
        self.cutout_starttime = {}
        self.cutout_endtime = {}
        self.pause_length = {}
        self.SNR = {}
        self.front_gain_check_list = {}
        self.back_gain_check_list = {}
        self.front_gain_samples = {}
        self.back_gain_samples = {}
        # self.current_tier = {}

        # tier selection
        self.tier_check_list = {}
        self.selected_text = {}
        self.text_start = {}
        self.text_end = {}

        # min and max freq for spec
        self.min_freq = StringVar(value="0")
        self.max_freq = StringVar(value="5000")
        self.min_freq_entry = Entry(self.button_frame, textvariable=self.min_freq, state='disabled',width=6)
        self.min_freq_entry.grid(column=2, row=1)
        tt.Hovertip(self.min_freq_entry, text='Minimum Frequency')
        self.max_freq_entry = Entry(self.button_frame, textvariable=self.max_freq, state='disabled',width=6)
        self.max_freq_entry.grid(column=3, row=1)
        tt.Hovertip(self.max_freq_entry, text='Maximum Frequency')
        self.spec_check.trace_add('write', self.toggle_freq_entry)

        # buttons to save and load workspace
        # Button(self.mainframe,text='Save Project',command=self.save_workspace).grid(column=1,row=0)
        # Button(self.mainframe,text='Load Project',command=self.load_workspace).grid(column=2,row=0)
        self.loadflag = 0

        # label search thingy
        self.labelinfo = Frame(self.mainframe)
        self.labelinfo.grid(column=2,row=0,sticky="w")
        Label(self.labelinfo,text="Search for label:").grid(column=0,row=0,sticky="w")
        self.label_frame = Frame(self.mainframe,relief="groove")
        self.label_frame.grid(column=2, row=1, rowspan=2,sticky="nw")
        self.current_label = StringVar(value=str(0))
        self.labelcount = StringVar(value=str(0))
        self.label = StringVar(value="Label")
        self.timedelta = StringVar(value=str(2))
        Button(self.labelinfo,text="?",command=self.help_label,width=3).grid(column=1,row=0,sticky="e")
        Label(self.label_frame,text="+-time:").grid(column=0,row=1)
        Entry(self.label_frame,textvariable=self.timedelta,width=4).grid(column=1,row=1)
        Label(self.label_frame,text="Found:").grid(column=1,row=0,sticky="w")
        Label(self.label_frame,textvariable=self.labelcount).grid(column=2,row=0,sticky="e")
        Entry(self.label_frame,textvariable=self.label).grid(column=0,row=0)
        Button(self.label_frame,text="Find",command=self.search_for_label).grid(column=0,row=2)
        self.prevnext_frame = Frame(self.label_frame)
        self.prevnext_frame.grid(column=1,row=2)
        Button(self.prevnext_frame,text="<<",command=self.prev_label,width=3).grid(column=1,row=2)
        Entry(self.prevnext_frame,textvariable=self.current_label,width=3).grid(column=2,row=2)
        Button(self.prevnext_frame,text=">>",command=self.next_label,width=3).grid(column=3,row=2)

        # change intervals
        # Button(self.button_frame,text="Edit intervals",command=self.edit_intervals).grid(column=6,row=0)

    def create_menubar(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = Menu(menubar)
        # add wav load
        file_menu.add_command(
            label='Load wav',
            command = self.choose_wav_file
        )
        # add tgt load
        file_menu.add_command(
            label='Load textgrid',
            command = self.choose_textgrid_file
        )
        # add export
        file_menu.add_command(
            label='Export files',
            command = self.export_window
        )
        # add save and load
        file_menu.add_command(
            label='Save project',
            command = self.save_workspace
        )
        file_menu.add_command(
            label='Load project',
            command = self.load_workspace
        )
        file_menu.add_command(
            label='Clear window',
            command = self.clear_window
        )
        menubar.add_cascade(
            label="File",
            menu=file_menu
        )

    def configure_grid(widget):
        widget.grid_rowconfigure(0, weight=1)
        widget.grid_columnconfigure(0, weight=1)
    
    def edit_intervals(self):
        edit_int_window = Toplevel(self.mainframe)
        edit_int_window.title("Edit Intervals")
        edit_int_window.geometry("800x600")
        
        main_frame = Frame(edit_int_window, width=800, height=600)
        main_frame.grid(row=0, column=0, sticky="nsew")

        h_scrollbar = Scrollbar(main_frame, orient=HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky="nsew")

        edit_int_canvas = Canvas(main_frame, xscrollcommand=h_scrollbar.set, width=800, height=600)
        edit_int_canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.config(command=edit_int_canvas.xview)

        edit_int_frame = Frame(edit_int_canvas)
        edit_int_frame.grid(column=0,row=0)
        column = 0
        for name, var in self.tier_check_list.items():
            if var.get():
                # tier = next(t for t in self.tg.tiers if t.name == name)
                tier = self.tg.getFirst(name)

                tier_frame = Frame(edit_int_frame)
                tier_frame.grid(column=column,row=0,rowspan=1)

                Label(tier_frame,text=name).grid(column=0,row=0)

                tier_sb = Scrollbar(tier_frame, orient=VERTICAL)
                tier_sb.grid(row=1, column=1, sticky="nsew")

                tier_canvas = Canvas(tier_frame,yscrollcommand=tier_sb)
                tier_canvas.grid(row=1, column=0, sticky="nsew")
                tier_sb.config(command=tier_canvas.yview)

                intervals_frame = Frame(tier_canvas)
                tier_canvas.create_window((0, 0), window=intervals_frame, anchor="nw")

                # save or undo
                Button(tier_frame,command=self.save_intervals).grid(column=0,row=2)

                int_row = 0
                for i, mark in enumerate(self.selected_text[name]):
                    if (float(self.text_end[name][i]) > float(self.starttime.get())) and (float(self.text_start[name][i]) < float(self.endtime.get())):
                        interval = tier.intervals[i]

                        interval_frame = Frame(tier_canvas)
                        interval_frame.grid(column=0,row=int_row)

                        tb_frame = Frame(interval_frame)
                        tb_frame.grid(column=0,row=0,columnspan=2)

                        text_box = Text(interval_frame,height=2,width=20,wrap='word')
                        text_box.insert('end',interval.mark)
                        text_box.grid(column=0,row=0)

                        int_sb = Scrollbar(tb_frame, orient=VERTICAL)
                        int_sb.grid(row=0, column=2, sticky="nsew")

                        text_box.config(yscrollcommand=int_sb.set)
                        int_sb.config(command=text_box.yview)

                        int_row += 1

                interval_frame.update_idletasks()
                tier_canvas.config(scrollregion=tier_canvas.bbox("all"))  

                column += 1

        main_frame.update_idletasks()
        edit_int_canvas.config(scrollregion=edit_int_canvas.bbox("all"))
    
    def save_intervals(self):
        pass

    def savetimes(self,index=None):
        if index is None:
            if self.starttime.get() != '' and self.endtime.get() != '':
                self.time_count += 1
                index = f"frame_{self.time_count}"
                self.saved_starttime[index] = StringVar(value=str(self.starttime.get()))
                self.saved_endtime[index] = StringVar(value=str(self.endtime.get()))
                self.saved_name[index] = StringVar(value='')
                self.saved_export[index] = BooleanVar(value=True)
                self.time_index_count[index] = self.time_count
        frame = Frame(self.timesave_inner_frame,relief="groove")
        frame.grid(column=0,row=1+self.time_index_count[index],columnspan=2)
        Label(frame,text="Start:").grid(column=0,row=0)
        Entry(frame,textvariable=self.saved_starttime[index]).grid(column=1,row=0)
        Label(frame,text="End:").grid(column=0,row=1)
        Entry(frame,textvariable=self.saved_endtime[index]).grid(column=1,row=1)
        Label(frame,text="Name:").grid(column=0,row=2)
        Entry(frame,textvariable=self.saved_name[index]).grid(column=1,row=2)
        Checkbutton(frame,variable=self.saved_export[index],text="Export").grid(column=2,row=2)
        Button(frame,text="Remove",command=lambda ind=index: self.remove_savetimes(index=ind),width=7).grid(column=2,row=0)
        Button(frame,text="Go to",command=lambda ind=index: self.set_savetimes(index=ind),width=7).grid(column=2,row=1)
        self.savetimes_frames[index] = frame
        frame.update()
        frame_width = frame.winfo_width()
        self.timesave_canvas.config(width=frame_width+20)
        self.timesave_frame.update_idletasks()
        self.timesave_canvas.config(scrollregion=self.timesave_canvas.bbox("all"))

    def set_savetimes(self,index):
        self.starttime.set(self.saved_starttime[index].get())
        self.endtime.set(self.saved_endtime[index].get())
        self.refresh_fig()

    def remove_savetimes(self,index):
        frame = self.savetimes_frames[index]
        frame.destroy()
        del self.saved_starttime[index]
        del self.saved_endtime[index]
        del self.saved_name[index]
        del self.saved_export[index]
        del self.time_index_count[index]
        self.timesave_canvas.update_idletasks()
        self.timesave_canvas.config(scrollregion=self.timesave_canvas.bbox("all"))

    def search_for_label(self):  
        # labels = self.label.get().split("|")
        # labels = [label.strip().lower() for label in labels]
        self.label_dict = {}
        self.labelcount.set(str(0))
        self.current_label.set(str(0))
        # for label in labels:
        for tiername, tiertext in self.selected_text.items():
            for i, mark in enumerate(tiertext):
                x = re.search(self.label.get(), mark)
                if x:
                    self.write_label(tiername,i)
                # all_in = True
                # if "&" in label:
                #     multi_label = [l.strip() for l in label.split("&")]
                # else:
                #     multi_label = [label]
                # for l in multi_label:
                #     if ("{" in l) and ("}" in l):
                #         label_comp = l.strip("{").strip("}")
                #         if label_comp.lower() != mark.lower():
                #             all_in = False
                #     else:
                #         if l not in mark.lower():
                #             all_in = False
                # if all_in:
                #     self.write_label(tiername,i)

    def write_label(self,tiername,i):
        self.labelcount.set(str(int(self.labelcount.get())+1))
        # self.label_dict['labelcount'].append(self.labelcount)
        self.label_dict[self.labelcount.get()] = {'start': [], 'end': []}
        self.label_dict[self.labelcount.get()]['start'] = self.text_start[tiername][i]
        self.label_dict[self.labelcount.get()]['end'] = self.text_end[tiername][i]

    def prev_label(self):
        if int(self.current_label.get()) == 1 or int(self.current_label.get()) == 0:
            self.current_label.set(self.labelcount.get())
        else:
            self.current_label.set(str(int(int(self.current_label.get())-1)))
        self.refresh_label()

    def next_label(self):
        if int(self.current_label.get()) == int(self.labelcount.get()):
            self.current_label.set(str(1))
        else:
            self.current_label.set(str(int(int(self.current_label.get())+1)))
        self.refresh_label()
        
    def refresh_label(self):
        self.starttime.set(str(max(float(self.label_dict[self.current_label.get()]['start'])-float(self.timedelta.get()),0)))
        self.endtime.set(str(min(float(self.label_dict[self.current_label.get()]['end'])+float(self.timedelta.get()),int(self.tg.maxTime))))
        self.refresh_fig()

    def open_link(self, url):
        webbrowser.open_new(url)
    
    def help_label(self):
        help_window = Toplevel(self.mainframe)
        help_window.title("Help for label search")
        Label(help_window, text="The label search follows the rules of regex.").grid(column=0, row=0, sticky="w")

        link = tk.Label(help_window, text="Regex Documentation", fg="blue", cursor="hand2")
        link.grid(column=0, row=1, sticky="w")
        link.bind("<Button-1>", lambda e: self.open_link("https://docs.python.org/3/library/re.html"))

    def save_workspace(self):
        workspace_path = filedialog.asksaveasfilename(defaultextension='.pkl')
        if workspace_path:
            savedict = {
                        'cutout_count': self.cutout_count,
                        'tg_file_path': self.tg_file_path,
                        'file_path': self.file_path,
                        'starttime': self.starttime.get(),
                        'endtime': self.endtime.get(),
                        'cut_index_count': {},
                        'cutout_starttime': {},
                        'cutout_endtime': {},
                        'apply_check_list': {},
                        'noise_check_list': {},
                        'pause_length': {},
                        'SNR': {},
                        'tier_check_list': {},
                        'front_gain_check_list': {},
                        'back_gain_check_list': {},
                        'front_gain_samples': {},
                        'back_gain_samples': {},
                        'saved_starttime': {},
                        'saved_endtime': {},
                        'saved_name': {},
                        'saved_export': {},
                        'time_index_count': {}
                        }
            for index in self.cutout_starttime:
                savedict['cut_index_count'][index] = self.cut_index_count[index]
                savedict['cutout_starttime'][index] = self.cutout_starttime[index].get()
                savedict['cutout_endtime'][index] = self.cutout_endtime[index].get()
                savedict['apply_check_list'][index] = self.apply_check_list[index].get()
                savedict['noise_check_list'][index] = self.noise_check_list[index].get()
                savedict['pause_length'][index] = self.pause_length[index].get()
                savedict['SNR'][index] = self.SNR[index].get()
                savedict['front_gain_check_list'][index] = self.front_gain_check_list[index].get()
                savedict['back_gain_check_list'][index] = self.back_gain_check_list[index].get()
                savedict['front_gain_samples'][index] = self.front_gain_samples[index].get()
                savedict['back_gain_samples'][index] = self.back_gain_samples[index].get()
            for tier in self.tier_check_list:
                savedict['tier_check_list'][tier] = self.tier_check_list[tier].get()
            for index in self.saved_starttime:
                savedict['saved_starttime'][index] = self.saved_starttime[index].get()
                savedict['saved_endtime'][index] = self.saved_endtime[index].get()
                savedict['saved_name'][index] = self.saved_name[index].get()
                savedict['saved_export'][index] = self.saved_export[index].get()
                savedict['time_index_count'][index] = self.time_index_count[index]
            if not workspace_path:
                return
            with open(workspace_path, 'wb') as f:
                pickle.dump(savedict, f)
            self.root.title(f"Slicer TNT - {os.path.basename(workspace_path)}")

    def load_workspace(self):
        workspace_path = filedialog.askopenfilename()
        if workspace_path:
            self.loadflag = 1
            indexdummy= []
            for index in self.cutout_starttime:
                indexdummy.append(index)
            for index in indexdummy:
                self.remove_cutout(index=index)
            indexdummy= []
            for index in self.saved_starttime:
                indexdummy.append(index)
            for index in indexdummy:
                self.remove_savetimes(index=index)
            self.cut_index_count = {}
            self.cutout_frames = {}
            self.noise_check_list = {}
            self.apply_check_list = {}
            self.cutout_starttime = {}
            self.cutout_endtime = {}
            self.pause_length = {}
            self.SNR = {}
            self.front_gain_check_list = {}
            self.back_gain_check_list = {}
            self.front_gain_samples = {}
            self.back_gain_samples = {}
            # self.current_tier = {}

            # tier selection
            self.tier_check_list = {}
            self.selected_text = {}
            self.text_start = {}
            self.text_end = {}

            # savetimes
            self.saved_starttime = {}
            self.saved_endtime = {}
            self.saved_name = {}
            self.saved_export = {}
            self.time_index_count = {}
            self.time_count = 0
            
            if not workspace_path:
                return
            with open(workspace_path, 'rb') as f:
                savedict = pickle.load(f)
                self.cutout_count = savedict['cutout_count']
                self.tg_file_path = savedict['tg_file_path']
                self.file_path = savedict['file_path']
                self.starttime.set(savedict['starttime']) 
                self.endtime.set(savedict['endtime'])
                for index in savedict['cutout_starttime']:
                    self.cut_index_count[index] = savedict['cut_index_count'][index]
                    self.cutout_starttime[index] = StringVar()
                    self.cutout_starttime[index].set(savedict['cutout_starttime'][index])
                    self.cutout_endtime[index] = StringVar()
                    self.cutout_endtime[index].set(savedict['cutout_endtime'][index])
                    self.apply_check_list[index] = BooleanVar()
                    self.apply_check_list[index].set(savedict['apply_check_list'][index])
                    self.noise_check_list[index] = BooleanVar()
                    self.noise_check_list[index].set(savedict['noise_check_list'][index])
                    self.pause_length[index] = StringVar()
                    self.pause_length[index].set(savedict['pause_length'][index])
                    self.SNR[index] = StringVar()
                    self.SNR[index].set(savedict['SNR'][index])
                    self.front_gain_check_list[index] = BooleanVar()
                    self.front_gain_check_list[index].set(savedict['front_gain_check_list'][index])
                    self.back_gain_check_list[index] = BooleanVar()
                    self.back_gain_check_list[index].set(savedict['back_gain_check_list'][index])
                    self.front_gain_samples[index] = StringVar()
                    self.front_gain_samples[index].set(savedict['front_gain_samples'][index])
                    self.back_gain_samples[index] = StringVar()
                    self.back_gain_samples[index].set(savedict['back_gain_samples'][index])
                    self.add_cutout(index=index)
                for tier in savedict['tier_check_list']:
                    self.tier_check_list[tier] = BooleanVar()
                    self.tier_check_list[tier].set(savedict['tier_check_list'][tier])
                try:
                    for index in savedict['saved_starttime']:
                        self.saved_starttime[index] = StringVar()
                        self.saved_starttime[index].set(savedict['saved_starttime'][index])
                        self.saved_endtime[index] = StringVar()
                        self.saved_endtime[index].set(savedict['saved_endtime'][index])
                        self.saved_name[index] = StringVar()
                        self.saved_name[index].set(savedict['saved_name'][index])
                        try:
                            self.saved_export[index] = BooleanVar()
                            self.saved_export[index].set(savedict['saved_export'][index])
                        except:
                            pass
                        self.time_index_count[index] = savedict['time_index_count'][index]
                        self.time_count = max(self.time_count,int(index.split("_")[-1]))
                        self.savetimes(index=index)
                except:
                    # print("could not load saved times")
                    pass
            self.wavlabel.config(text=textwrap.fill(self.file_path,width=30))
            self.sample_rate, self.audio_data = wavfile.read(self.file_path)
            self.audio_data_plot = np.array(self.audio_data, copy=True)
            self.tg = textgrid.TextGrid.fromFile(self.tg_file_path)
            # self.tg_plot = textgrid.TextGrid.fromFile(self.tg_file_path)
            self.tglabel.config(text=textwrap.fill(self.tg_file_path, width=30))
            self.setup_checkbox_frame()
            self.get_tiernames()
            self.mintimelabel.config(text=textwrap.fill('min: '+str(self.tg.minTime),width=30))
            self.maxtimelabel.config(text=textwrap.fill('max: '+str(self.tg.maxTime),width=30))
            self.loadflag = 0
            if (self.tg_file_path is not None) and (self.file_path is not None):
                if self.starttime.get() == '':
                    self.starttime.set(str(self.tg.minTime))
                if self.endtime.get() == '':
                    self.endtime.set(str(min(float(self.tg.maxTime),float(self.tg.minTime)+10)))
                self.refresh_fig()
            self.root.title(f"Slicer TNT - {os.path.basename(workspace_path)}")
            self.update_all_bbox()

    def clear_window(self):
        if messagebox.askokcancel("Clear window", "Do you want to clear the window, discarding all unsaved progress?"):
            self.mainframe.destroy()
            self.create_mainframe()

    def toggle_freq_entry(self, *args):
        if self.spec_check.get():
            self.min_freq_entry.config(state='normal')
            self.max_freq_entry.config(state='normal')
        else:
            self.min_freq_entry.config(state='disabled')
            self.max_freq_entry.config(state='disabled')

    def setup_checkbox_frame(self):
        # try:
        #     self.checkbox_frame.destroy
        # except:
        #     pass
        self.checkbox_frame = Frame(self.mainframe)
        self.checkbox_frame.grid(column=4, row=1, sticky="nsew", rowspan=4)

        scrollbar = Scrollbar(self.checkbox_frame, orient=VERTICAL)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.checkbox_canvas = Canvas(self.checkbox_frame, yscrollcommand=scrollbar.set)
        self.checkbox_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar.config(command=self.checkbox_canvas.yview)

        self.checkbox_inner_frame = Frame(self.checkbox_canvas)
        self.checkbox_canvas.create_window((0, 0), window=self.checkbox_inner_frame, anchor="nw")

        self.checkbox_frame.columnconfigure(0, weight=1)
        self.checkbox_frame.rowconfigure(0, weight=1)

        # self.checkbox_inner_frame.bind("<Configure>", lambda e: self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all")))
        self.checkbox_inner_frame.update()
        frame_width = self.checkbox_inner_frame.winfo_width()
        self.checkbox_canvas.config(width=frame_width+20)
        self.checkbox_inner_frame.update_idletasks()
        self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))
        self.checkbox_frame.update_idletasks()

    def update_all_bbox(self):
        self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))
        self.timesave_canvas.configure(scrollregion=self.timesave_canvas.bbox("all"))
        self.cutout_canvas.configure(scrollregion=self.cutout_canvas.bbox("all"))

    def timebuttons(self,type):
        try:
            start_value = float(self.starttime.get()) 
            end_value = float(self.endtime.get())
            if type == 's++':
                start_value += 1
            elif type == 's+':
                start_value += 0.05
            elif type == 's-':
                start_value -= 0.05
            elif type == 's--':
                start_value -= 1
            elif type == 'e++':
                end_value += 1
            elif type == 'e+':
                end_value += 0.05
            elif type == 'e-':
                end_value -= 0.05
            elif type == 'e--':
                end_value -= 1
            self.starttime.set(str(start_value))
            self.endtime.set(str(end_value))
            self.refresh_fig()
        except ValueError:
            pass 
        
    def export_window(self):
        try:
            exp_dialog = Toplevel(self.mainframe)
            exp_dialog.title("Export options")
            Label(exp_dialog, text="Export directory: ").grid(column=0, row=0)
            self.exp_dir = Entry(exp_dialog)
            self.exp_dir.grid(column=1,row=0,sticky=(W,E))
            Label(exp_dialog, text="Export name: ").grid(column=0, row=1)
            self.exp_name = Entry(exp_dialog)
            self.exp_name.grid(column=1,row=1,sticky=(W,E))
            file_name = os.path.basename(self.file_path)
            try:
                default_name = os.path.splitext(file_name)[0]
            except:
                default_name = ""
            default_name = f'{default_name}_{self.starttime.get()}'
            self.exp_name.insert(0, default_name)
            
            # add dir search button
            Button(exp_dialog,text="Choose directory",command=self.browse_file).grid(column=2,row=0)

            # checkbox for export options
            Label(exp_dialog, text="Export Tiers:").grid(column=0, row=2)
            self.exp_checkbox_frame = Frame(exp_dialog)
            self.exp_checkbox_frame.grid(column=1, row=2, sticky='w')

            # get textgrid tiers
            self.get_exp_tiernames()

            # export options frame
            exp_options_frame = Frame(exp_dialog)
            exp_options_frame.grid(column=1,row=3,sticky='nsew',columnspan=2)

            # checkbox if output should be normalized
            self.normalize_export = BooleanVar(value=True)
            Checkbutton(exp_options_frame, text="Normalize export", variable=self.normalize_export).grid(column=0,row=0)
            
            # Normalization from to
            Label(exp_options_frame,text='Time span around frame to normalize from (in sec):').grid(column=0,row=4)
            # self.norm_start = StringVar(value=self.starttime.get())
            # self.norm_end = StringVar(value=self.endtime.get())
            self.norm_span = StringVar(value="10")
            Entry(exp_options_frame,textvariable=self.norm_span).grid(column=1,row=4)
            # Entry(exp_options_frame,textvariable=self.norm_start).grid(column=1,row=4)
            # Entry(exp_options_frame,textvariable=self.norm_end).grid(column=2,row=4)

            # checkbox for different sample rate
            self.resample_check = BooleanVar()
            Checkbutton(exp_options_frame, text="Samplerate", variable=self.resample_check).grid(column=1,row=0)
            self.resample_rate = StringVar(value=str(self.sample_rate))
            Entry(exp_options_frame,textvariable=self.resample_rate).grid(column=2,row=0)

            # dropdown menu for data type
            self.data_types = ['int8', 'int16', 'int32', 'int64',
                               'uint8', 'uint16', 'uint32', 'uint64',
                               'float32', 'float64']
            self.sel_data_type = StringVar(value=str(self.audio_data.dtype))
            Combobox(exp_options_frame,textvariable=self.sel_data_type,values=self.data_types).grid(column=3,row=0)

            # start and end values of export
            Label(exp_options_frame, text="Start and end of the frame: ").grid(column=0,row=1)
            self.exp_start = StringVar(value=self.starttime.get())
            self.exp_start_entry = Entry(exp_options_frame, textvariable=self.exp_start)
            self.exp_start_entry.grid(column=1,row=1)
            Button(exp_options_frame,text='0',command=self.set_export_start_zero,width=4).grid(column=2,row=1)
            self.exp_end = StringVar(value=self.endtime.get())
            self.exp_end_entry = Entry(exp_options_frame, textvariable=self.exp_end)
            self.exp_end_entry.grid(column=3,row=1)
            Button(exp_options_frame,text='end',command=self.set_export_end_total,width=4).grid(column=4,row=1)
            Button(exp_options_frame,text='<->',command=self.set_export_times,width=4).grid(column=5,row=1)
            
            # start the export with the original time values or at 0
            Label(exp_options_frame, text="Write time to textgrid starting with: ").grid(column=0,row=2)
            self.exp_time_start = StringVar(value='0')
            self.exp_time_entry = Entry(exp_options_frame, textvariable=self.exp_time_start)
            self.exp_time_entry.grid(column=1,row=2)
            Button(exp_options_frame,text='0',command=self.set_exp_zero,width=4).grid(column=2,row=2,sticky='w')
            Button(exp_options_frame,text='frame',command= self.set_exp_now,width=5).grid(column=2,row=2,sticky='e')

            # insert cut in and cut out checkboxes
            Label(exp_options_frame, text="Fade in (samples):").grid(column=0,row=3)
            self.fade_in = StringVar(value='0')
            Entry(exp_options_frame, textvariable=self.fade_in).grid(column=1,row=3)
            Label(exp_options_frame, text="Fade out (samples):").grid(column=2,row=3)
            self.fade_out = StringVar(value='0')
            Entry(exp_options_frame, textvariable=self.fade_out).grid(column=3,row=3)

            # insert export all function
            Button(exp_options_frame,text='Export all checked starttimes', command=lambda tg=self.tg: self.export_all(tg=tg)).grid(column=1,row=5)
            
            # insert export button
            Button(exp_options_frame,text='Export Files',command=lambda tg=self.tg: self.export_files(tg=tg)).grid(column=0,row=5)
        except ValueError:
            pass

    def export_all(self,tg):
        start_def = self.exp_start.get()
        end_def = self.exp_end.get()
        name_def = self.exp_name.get()
        for i, name in self.saved_name.items():
            if self.saved_export[i].get() == True:    
                self.exp_start.set(self.saved_starttime[i].get())
                self.exp_end.set(self.saved_endtime[i].get())
                file_name = os.path.basename(self.file_path)
                try:
                    default_name = os.path.splitext(file_name)[0]
                except:
                    default_name = ""
                default_name = f'{name_def}_{self.exp_start.get()}_{name.get()}'
                self.exp_name.delete(0,END)
                self.exp_name.insert(0,default_name)
                self.export_files(tg=tg)
        self.exp_start.set(start_def)
        self.exp_end.set(end_def)
        self.exp_name.delete(0,END)
        self.exp_name.insert(0,name_def)

    def export_files(self, tg):
        start_time = float(self.exp_start.get())
        start_sample = int(max(0, self.sample_rate * start_time))
        end_time = float(self.exp_end.get())
        end_sample = int(min(self.sample_rate * end_time, len(self.audio_data)))
        exp_audioslice = np.array(self.audio_data_plot[start_sample:end_sample],copy=True)
        exp_name = os.path.join(self.exp_dir.get(),self.exp_name.get())
        exp_name_wav = exp_name + '.wav'
        for index, variable in sorted(self.cutout_starttime.items(), key=lambda x: float(x[1].get()), reverse=True):
            if self.apply_check_list[index].get():
                if float(variable.get()) >= start_time and float(self.cutout_starttime[index].get()) < end_time:
                    cutstart = int(self.sample_rate*(max(start_time,float(self.cutout_starttime[index].get())) - start_time))
                    cutend = int(self.sample_rate*(min(end_time,float(self.cutout_endtime[index].get())) - start_time))
                    pause_length = float(self.pause_length[index].get())*self.sample_rate
                    pause_end = min(cutstart + pause_length, cutend)
                    rest_length = cutend - pause_end
                    pause_range = np.arange(int(cutstart), int(pause_end))
                    if self.noise_check_list[index].get():
                        noise_var = np.var(self.audio_data)/10**(float(self.SNR[index].get())/10)
                        exp_audioslice[pause_range] = np.sqrt(noise_var) * np.random.normal(0, 1, len(pause_range))
                    else:
                        exp_audioslice[pause_range] = 0
                    if self.front_gain_check_list[index].get():
                        nsamples = int(self.front_gain_samples[index].get())
                        gainsamples = np.arange(max(start_sample,cutstart-nsamples),cutstart)
                        gainrange = np.flip(np.arange(0,len(gainsamples))/len(gainsamples))
                        exp_audioslice[gainsamples] = exp_audioslice[gainsamples]*gainrange
                    if self.back_gain_check_list[index].get():
                        nsamples = int(self.back_gain_samples[index].get())
                        gainsamples = np.arange(min(end_sample,cutend),min(end_sample,cutend+nsamples))
                        gainrange = np.arange(0,len(gainsamples))/len(gainsamples)
                        exp_audioslice[gainsamples] = exp_audioslice[gainsamples]*gainrange
                    exp_audioslice = np.delete(exp_audioslice,np.arange(int(pause_end),int(cutend)))
        if self.resample_check.get():
            fs_exp = int(self.resample_rate.get())
            exp_audioslice = resample(exp_audioslice, int(len(exp_audioslice)*(fs_exp/self.sample_rate)))
        else:
            fs_exp = self.sample_rate
        if self.normalize_export.get():
            # start_time_norm = float(self.norm_start.get())
            start_time_norm = max(start_time-float(self.norm_span.get()),0)
            start_sample_norm = int(max(0, self.sample_rate * start_time_norm))
            # end_time_norm = float(self.norm_end.get())
            end_time_norm = min(end_time+float(self.norm_span.get()),float(self.tg.maxTime))
            end_sample_norm = int(min(self.sample_rate * end_time_norm, len(self.audio_data)))
            exp_norm = self.audio_data_plot[start_sample_norm:end_sample_norm]
            exp_norm = np.max(np.abs(exp_norm))
            exp_audioslice = exp_audioslice / exp_norm
            if np.issubdtype(np.dtype(getattr(np,self.sel_data_type.get())),np.integer):
                exp_audioslice = exp_audioslice * np.iinfo(np.dtype(getattr(np,self.sel_data_type.get()))).max
        if int(self.fade_in.get()) > 0:
            gainrange = np.arange(0,int(self.fade_in.get())).astype(float)/float(self.fade_in.get())
            exp_audioslice[0:int(self.fade_in.get())] = gainrange*exp_audioslice[0:int(self.fade_in.get())]
        if int(self.fade_out.get()) > 0:
            gainrange = np.flip(np.arange(0,int(self.fade_out.get())).astype(float)/float(self.fade_out.get()))
            exp_audioslice[-int(self.fade_out.get()):] = gainrange*exp_audioslice[-int(self.fade_out.get()):]
        wavfile.write(exp_name_wav,fs_exp,exp_audioslice.astype(np.dtype(self.sel_data_type.get())))
        tg_exp = textgrid.TextGrid(name=exp_name)
        
        self.exp_time_end = StringVar(value=str(float(self.exp_time_start.get()) + float(self.exp_end.get()) - float(self.exp_start.get())))
        time_diff = float(self.exp_start.get()) - float(self.exp_time_start.get())
        for name, var in self.exp_tier_check_list.items():
            if var.get():
                tier = tg.getFirst(name)
                tier_exp = textgrid.IntervalTier(name=name)
                for interval in tier:
                    if interval.minTime < float(self.exp_start.get()) and interval.maxTime > float(self.exp_start.get()):
                        int_exp = textgrid.Interval(minTime=0, maxTime=1, mark=interval.mark)
                        int_exp.minTime = float(self.exp_time_start.get())
                        if interval.maxTime > float(self.exp_end.get()):
                            int_exp.maxTime = float(self.exp_time_end.get())
                        else:
                            int_exp.maxTime = interval.maxTime - time_diff
                        tier_exp.addInterval(int_exp)
                    if interval.minTime > float(self.exp_start.get()) and interval.minTime < float(self.exp_end.get()):
                        int_exp = textgrid.Interval(minTime=0, maxTime=1, mark=interval.mark)
                        int_exp.minTime = interval.minTime - time_diff
                        if interval.maxTime < float(self.exp_end.get()):
                            int_exp.maxTime = interval.maxTime - time_diff
                        else:
                            int_exp.maxTime = float(self.exp_time_end.get())
                        tier_exp.addInterval(int_exp)
                for index, variable in sorted(self.cutout_starttime.items(), key=lambda x: float(x[1].get()), reverse=True):
                    if self.apply_check_list[index].get():
                        self.cut_start = float(self.cutout_starttime[index].get())-time_diff
                        self.cut_end = float(self.cutout_endtime[index].get())-time_diff
                        if self.cut_end > 0:
                            pause_length = float(self.pause_length[index].get())
                            self.pause_end = self.cut_start + pause_length
                            self.cut_start = max(self.cut_start,0)
                            self.pause_end = max(self.pause_end,0)
                            self.rest_length = self.cut_end - self.pause_end
                            tier_exp = self.manipulate_tier(tier_exp)
                tg_exp.append(tier_exp)
        exp_name_tg = exp_name + '.TextGrid'
        tg_exp.write(exp_name_tg)

    def manipulate_tier(self,tier):
        manip_tier = textgrid.IntervalTier(name=tier.name)
        for interval in tier.intervals:
            if (interval.minTime < self.cut_start and interval.maxTime < self.cut_start):
                int_manip = textgrid.Interval(minTime=interval.minTime,maxTime=interval.maxTime,mark=interval.mark)
                manip_tier.addInterval(int_manip)
            if interval.minTime < self.cut_start and interval.maxTime > self.cut_start:
                if interval.maxTime > self.cut_end:
                    interval_1 = textgrid.Interval(minTime=interval.minTime, maxTime=self.cut_start, mark=interval.mark)
                    interval_2 = textgrid.Interval(minTime=self.pause_end, maxTime=interval.maxTime-self.rest_length, mark=interval.mark)
                    manip_tier.addInterval(interval_1)
                    manip_tier.addInterval(interval_2)
                else:
                    int_manip = textgrid.Interval(minTime=interval.minTime,maxTime=interval.maxTime,mark=interval.mark)
                    int_manip.maxTime = self.cut_start
                    manip_tier.addInterval(int_manip)
            # if interval.minTime >= self.cut_start and interval.maxTime < self.cut_end:
            #     tier.removeInterval(interval)
            if interval.minTime >= self.cut_start and interval.maxTime > self.cut_end:
                int_manip = textgrid.Interval(minTime=interval.minTime,maxTime=interval.maxTime,mark=interval.mark)
                if interval.minTime > self.cut_end:
                    int_manip.minTime -= self.rest_length
                    int_manip.maxTime -= self.rest_length
                else:
                    int_manip.minTime = self.pause_end
                    int_manip.maxTime -= self.rest_length
                manip_tier.addInterval(int_manip)
        return manip_tier

    def apply_cutout(self):
        self.sample_rate, self.audio_data = wavfile.read(self.file_path)
        # tg = textgrid.TextGrid.fromFile(self.tg_file_path)
        for index, variable in sorted(self.cutout_starttime.items(), key=lambda x: float(x[1].get()), reverse=True):
            if self.apply_check_list[index].get():
                self.cut_start = float(self.cutout_starttime[index].get())
                self.cut_end = float(self.cutout_endtime[index].get())
                pause_length = float(self.pause_length[index].get())
                self.pause_end = self.cut_start + pause_length
                self.rest_length = self.cut_end - self.pause_end
                # manipulate audio
                start_sample = int(max(0,self.sample_rate*self.cut_start))
                end_sample = int(min(self.sample_rate*self.cut_end,len(self.audio_data)))
                pause_end_sample = int(min(self.pause_end, self.cut_end) * self.sample_rate)
                rest_range = np.arange(pause_end_sample, end_sample)
                pause_range = np.arange(start_sample, pause_end_sample)
                if self.noise_check_list[index].get():
                    noise_var = np.var(self.audio_data)/10**(float(self.SNR[index].get())/10)
                    self.audio_data[pause_range] = np.sqrt(noise_var) * np.random.normal(0, 1, len(pause_range))
                else:
                    self.audio_data[pause_range] = 0
                self.audio_data = np.delete(self.audio_data, rest_range)
                # manipulate tg
                # for tier in tg.tiers:
                #     self.manipulate_tier(tier)
        # self.tg = tg
        self.refresh_fig()

    def set_exp_zero(self):
        self.exp_time_start.set(str(0))
    
    def set_exp_now(self):
        self.exp_time_start.set(self.starttime.get())

    def browse_file(self):
        filepath = filedialog.askdirectory()
        self.exp_dir.delete(0, END)
        self.exp_dir.insert(0, filepath)
        
    def refresh_fig(self):
        plt.close(self.figure)
        start_time = float(self.starttime.get())
        end_time = float(self.endtime.get())
        start_sample = int(max(0, self.sample_rate * start_time))
        end_sample = int(min(self.sample_rate * end_time, len(self.audio_data)))
        self.audio_slice = self.audio_data_plot[start_sample:end_sample]
        self.which_tiers2show()
        heightratio = np.ones((1,len(self.selected_text)))
        heightratio = np.int64(np.concatenate((heightratio, (np.sum(heightratio) + 1).reshape(-1,1)),axis=1)).tolist()[0]
        self.figure, self.axes = plt.subplots(len(heightratio), 1, 
                                              figsize=(float(self.fig_width.get()), float(self.fig_height.get())), 
                                              gridspec_kw={'height_ratios': heightratio},sharex=True)
        self.axes = [self.axes] if not isinstance(self.axes, (list, np.ndarray)) else self.axes
        if self.spec_check.get():
            self.axes[-1].specgram(self.audio_slice, Fs=self.sample_rate, sides='onesided', xextent=(start_time,end_time))
            num_spec_samples = len(self.audio_slice) // 2 + 1
            spec_time = np.linspace(start_time, end_time, num=num_spec_samples)
            # self.axes[-1].set_xticks(np.linspace(0, end_time-start_time, num=5))
            self.axes[-1].set_xticks(np.linspace(start_time, end_time, num=5))
            self.axes[-1].set_xticklabels([f'{t:.2f}' for t in np.linspace(start_time, end_time, num=5)])
            min_freq = float(self.min_freq_entry.get()) if self.min_freq_entry.get() else 0
            max_freq = float(self.max_freq_entry.get()) if self.max_freq_entry.get() else 8000
            self.axes[-1].set_ylim(min_freq,max_freq)
            self.axes[-1].set_xlim(start_time,end_time)
        else:
            self.axes[-1].plot(np.linspace(start_time, end_time, num=len(self.audio_slice)), self.audio_slice, linewidth=1)
            self.axes[-1].set_xlabel('time in s')
            self.axes[-1].set_xticks(np.linspace(start_time, end_time, num=5))
            self.axes[-1].set_xticklabels([f'{t:.2f}' for t in np.linspace(start_time, end_time, num=5)])
            self.axes[-1].tick_params(axis='x',labeltop=False,labelbottom=True)
            self.axes[-1].tick_params(left=False)
            self.axes[-1].set_ylabel('')
            self.axes[-1].set_yticklabels([])
            self.axes[-1].set_xlim(start_time,end_time)
            self.axes[-1].set_ylim(np.min(self.audio_slice),np.max(self.audio_slice))

        for ii, tier_name in enumerate(self.selected_text):
            for i, label in enumerate(self.selected_text[tier_name]):
                if self.text_end[tier_name][i] >= start_time and self.text_start[tier_name][i] <= end_time:
                    start_text = max(self.text_start[tier_name][i],start_time)
                    self.axes[ii].text(x=start_text,y=0,s=textwrap.fill(label,width=10),wrap=True)
                    self.axes[ii].axvline(start_text, color='green', linestyle='--')
                    self.axes[ii].axvline(self.text_end[tier_name][i], color='red', linestyle='-.')
            # self.axes[ii].set_xlim(start_time,end_time)
            # self.axes[ii].plot(np.linspace(start_time, end_time, num=len(self.audio_slice)), np.zeros((len(self.audio_slice),1)), linewidth=1)
            self.axes[ii].set_ylim(-1,1)
            self.axes[ii].set_ylabel('')
            self.axes[ii].set_yticklabels([])
            self.axes[ii].set_xlabel('')
            self.axes[ii].set_xticklabels([])
            self.axes[ii].tick_params(axis='x',labeltop=False,labelbottom=False)
            self.axes[ii].tick_params(left=False)
            self.axes[ii].text(0,0,textwrap.fill(tier_name,width=20,max_lines=1),
                               transform=self.axes[ii].transAxes,fontsize=8,
                               verticalalignment='bottom', horizontalalignment='left',
                               bbox=dict(facecolor='lightblue', alpha=0.5))
        for i, ax in enumerate(self.axes):
            for index, variable in self.cutout_endtime.items():
                if self.apply_check_list[index].get():
                    if float(variable.get()) >= start_time and float(self.cutout_starttime[index].get()) < end_time:
                        ax.fill_between([float(self.cutout_starttime[index].get()),float(self.cutout_starttime[index].get())+float(self.pause_length[index].get())],-1000000,1000000,color='lightgrey',alpha=0.5)
                        ax.fill_between([float(self.cutout_starttime[index].get())+float(self.pause_length[index].get()),float(self.cutout_endtime[index].get())],-1000000,1000000,color='red',alpha=0.5)
                
        def update_status(event):
            if event.inaxes:
                x = event.xdata
                self.figure.canvas.toolbar.set_message(f"time={x:.2f}")

        self.figure_canvas.draw()
        plt.tight_layout(h_pad=0)
        # self.figure.set_tight_layout(True)
        self.figure_canvas.get_tk_widget().destroy()
        self.figure_canvas = FigureCanvasTkAgg(self.figure, master=self.mainframe)
        self.figure_canvas.get_tk_widget().grid(column=1,row=8,columnspan=4, sticky="nsew")
        self.toolbar_frame = Frame(self.mainframe)
        self.toolbar_frame.grid(column=1, row=9, sticky="nsew", columnspan=3)
        NavigationToolbar2Tk(self.figure_canvas, self.toolbar_frame)
        self.figure.canvas.mpl_connect("motion_notify_event", update_status)
        self.figure_canvas.draw()
    
    def play_wav(self):
        start_time = float(self.starttime.get())
        end_time = float(self.endtime.get())
        start_sample = int(max(0, self.sample_rate * start_time))
        end_sample = int(min(self.sample_rate * end_time, len(self.audio_data)))
        # play_audio = self.audio_data[start_sample:end_sample]
        play_audio = np.array(self.audio_slice, copy=True)
        for index, variable in sorted(self.cutout_starttime.items(), key=lambda x: float(x[1].get()), reverse=True):
            if self.apply_check_list[index].get():
                if float(variable.get()) >= start_time and float(self.cutout_starttime[index].get()) < end_time:
                    cutstart = int(self.sample_rate*(max(start_time,float(self.cutout_starttime[index].get())) - start_time))
                    cutend = int(self.sample_rate*(min(end_time,float(self.cutout_endtime[index].get())) - start_time))
                    pause_length = float(self.pause_length[index].get())*self.sample_rate
                    pause_end = min(cutstart + pause_length, cutend)
                    rest_length = cutend - pause_end
                    pause_range = np.arange(int(cutstart), int(pause_end))
                    if self.noise_check_list[index].get():
                        noise_var = np.var(self.audio_data)/10**(float(self.SNR[index].get())/10)
                        play_audio[pause_range] = np.sqrt(noise_var) * np.random.normal(0, 1, len(pause_range))
                    else:
                        play_audio[pause_range] = 0
                    if self.front_gain_check_list[index].get():
                        nsamples = int(self.front_gain_samples[index].get())
                        gainsamples = np.arange(max(1/10**(float(self.SNR[index].get())/10),cutstart-nsamples),cutstart)
                        gainrange = np.flip(np.arange(0,len(gainsamples))/len(gainsamples))
                        play_audio[gainsamples] = play_audio[gainsamples]*gainrange
                    if self.back_gain_check_list[index].get():
                        nsamples = int(self.back_gain_samples[index].get())
                        gainsamples = np.arange(min(end_sample-start_sample,cutend),min(end_sample-start_sample,cutend+nsamples))
                        gainrange = np.arange(1/10**(float(self.SNR[index].get())/10),len(gainsamples))/len(gainsamples)
                        play_audio[gainsamples] = play_audio[gainsamples]*gainrange
                    play_audio = np.delete(play_audio,np.arange(int(pause_end),int(cutend)))
        if self.normalize_playback.get():
            play_audio = play_audio / np.max(np.abs(self.audio_slice))
        sd.play(play_audio,self.sample_rate)

    def stop_wav(self):
        try:
            sd.stop()
        except:
            pass

    def choose_wav_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path is not None:
            self.wavlabel.config(text=textwrap.fill(self.file_path,width=30))
            self.sample_rate, self.audio_data = wavfile.read(self.file_path)
            self.audio_data_plot = np.array(self.audio_data, copy=True)
            if self.tg_file_path is not None:
                if self.starttime.get() == '':
                    self.starttime.set(str(self.tg.minTime))
                if self.endtime.get() == '':
                    self.endtime.set(str(min(float(self.tg.maxTime),float(self.tg.minTime)+10)))
                self.refresh_fig()
        else:
            self.wavlabel.config(text="No file.")
        

    def add_cutout(self,index=None):
        if index is None:
            if self.starttime.get() != '' and self.endtime.get() != '':
                self.cutout_count += 1
                index = f"frame_{self.cutout_count}"
                self.cut_index_count[index] = self.cutout_count
                self.cutout_starttime[index] = StringVar(value=str(self.starttime.get()))
                self.cutout_endtime[index] = StringVar(value=str(self.endtime.get()))
                self.pause_length[index] = StringVar(value=str(float(self.endtime.get())-float(self.starttime.get())))
                self.noise_check_list[index] = BooleanVar()
                self.SNR[index] = StringVar(value='40')
                self.apply_check_list[index] = BooleanVar()
                self.front_gain_check_list[index] = BooleanVar()
                self.back_gain_check_list[index] = BooleanVar()
                self.front_gain_samples[index] = StringVar(value='1000')
                self.back_gain_samples[index] = StringVar(value='1000')
            else:
                print('No start or endtimes given.')
                return
        frame = Frame(self.cutout_frame,relief="groove")
        frame.grid(column=0,row=1+self.cut_index_count[index],columnspan=2)
        Label(frame,text='From:').grid(column=0,row=0)
        Label(frame,text='To:').grid(column=0,row=1)
        Label(frame,text='Pause Length:').grid(column=0,row=2)
        Entry(frame,textvariable=self.cutout_starttime[index],width=8).grid(column=1,row=0)
        Entry(frame,textvariable=self.cutout_endtime[index],width=8).grid(column=1,row=1)
        Entry(frame,textvariable=self.pause_length[index],width=8).grid(column=1,row=2)
        # buttons for pause length=(0,wholepause)
        Button(frame,text='0',command=lambda ind=index: self.set_pause_zero(index=ind),width=4).grid(column=2,row=2,sticky='w')
        Button(frame,text='<->',command=lambda ind=index: self.set_pause_whole(index=ind),width=4).grid(column=2,row=2,sticky='e')
        # button to remove the cut out
        Button(frame,text='Remove',command=lambda ind=index: self.remove_cutout(index=ind)).grid(column=2,row=0)
        # check if to add noise
        Checkbutton(frame,text='Add noise', variable=self.noise_check_list[index]).grid(column=0,row=3)
        # enter SNR value
        Label(frame,text='SNR [dB]:').grid(column=1,row=3,sticky='w')
        Entry(frame,textvariable=self.SNR[index],width=3).grid(column=1,row=3,sticky='e')
        # check if pause should be applied
        Checkbutton(frame,text='Apply', variable=self.apply_check_list[index]).grid(column=2,row=1)
        # check if to only manipulate the current tier
        # self.current_tier[index] = BooleanVar()
        # Checkbutton(frame,text='only for current tier', variable=self.current_tier[index]).grid(column=1,row=3)

        # check if gain manipulation in front or back
        Checkbutton(frame,text='Decay to cut',variable=self.front_gain_check_list[index]).grid(column=0,row=4)
        Entry(frame,textvariable=self.front_gain_samples[index],width=5).grid(column=1,row=4,sticky='w')
        Label(frame,text='[samples]').grid(column=1,row=4,sticky='e')
        Checkbutton(frame,text='Attack from cut',variable=self.back_gain_check_list[index]).grid(column=2,row=4)
        Entry(frame,textvariable=self.back_gain_samples[index],width=5).grid(column=3,row=4,sticky='w')
        
        # append current frame to dict
        self.cutout_frames[index] = frame
        # self.cutout_canvas.update_idletasks()
        frame.update()
        frame_width = frame.winfo_width()
        self.cutout_canvas.config(width=frame_width+20)
        self.cutout_frame.update_idletasks()
        self.cutout_canvas.config(scrollregion=self.cutout_canvas.bbox("all"))

    def set_pause_zero(self,index):
        self.pause_length[index].set(str(0))

    def set_pause_whole(self,index):
        wholespan = float(self.cutout_endtime[index].get()) - float(self.cutout_starttime[index].get())
        self.pause_length[index].set(str(wholespan))

    def set_export_start_zero(self):
        self.exp_start.set('0')

    def set_export_end_total(self):
        self.exp_end.set(str(self.tg.maxTime))
    
    def set_export_times(self):
        self.exp_start.set(self.starttime.get())
        self.exp_end.set(self.endtime.get())

    def remove_cutout(self, index):
        frame = self.cutout_frames[index]
        frame.destroy()
        del self.cutout_frames[index]
        del self.apply_check_list[index]
        del self.cutout_starttime[index]
        del self.cutout_endtime[index]
        del self.pause_length[index]
        self.cutout_canvas.update_idletasks()
        self.cutout_canvas.config(scrollregion=self.cutout_canvas.bbox("all"))

    def choose_textgrid_file(self):
        self.tg_file_path = filedialog.askopenfilename()
        if self.tg_file_path is not None:
            self.tg = textgrid.TextGrid.fromFile(self.tg_file_path)
            # self.tg_plot = textgrid.TextGrid.fromFile(self.tg_file_path)
            self.tglabel.config(text=textwrap.fill(self.tg_file_path, width=30))
            self.setup_checkbox_frame()
            self.get_tiernames()
            self.mintimelabel.config(text=textwrap.fill('min: '+str(self.tg.minTime),width=30))
            self.maxtimelabel.config(text=textwrap.fill('max: '+str(self.tg.maxTime),width=30))
            if self.file_path is not None:
                if self.starttime.get() == '':
                    self.starttime.set(str(self.tg.minTime))
                if self.endtime.get() == '':
                    self.endtime.set(str(min(float(self.tg.maxTime),float(self.tg.minTime)+10)))
                self.refresh_fig()
        else:
            self.tglabel.config(text="No file.")

    def get_tiernames(self):
        self.items = self.load_textgrid_tiers()
        self.populate_checkboxes()

    def get_exp_tiernames(self):
        self.populate_exp_checkboxes()

    def load_textgrid_tiers(self):
        return [tier.name for tier in self.tg.tiers]

    def populate_checkboxes(self):
        for widget in self.checkbox_inner_frame.winfo_children():
            widget.destroy()
        if self.loadflag == 1:
            for item in self.items:
                checkbox = Checkbutton(self.checkbox_inner_frame, text=textwrap.wrap(item,width=30,placeholder=" [...]")[0], variable=self.tier_check_list[item])
                checkbox.grid(sticky=W)
        else:
            self.tier_check_list = {}
            for item in self.items:
                self.tier_check_list[item] = BooleanVar()
                checkbox = Checkbutton(self.checkbox_inner_frame, text=item, variable=self.tier_check_list[item])
                checkbox.grid(sticky=W)
        self.checkbox_frame.update_idletasks()
        self.checkbox_canvas.config(scrollregion=self.checkbox_canvas.bbox("all"))
    
    def populate_exp_checkboxes(self):
        for widget in self.exp_checkbox_frame.winfo_children():
            widget.destroy()
        self.exp_tier_check_list = {}
        for item in self.items:
            self.exp_tier_check_list[item] = BooleanVar(value=True)
            checkbox = Checkbutton(self.exp_checkbox_frame, text=item, variable=self.exp_tier_check_list[item])
            checkbox.grid(sticky=W)

    def which_tiers2show(self):
        self.selected_text = {}
        self.text_start = {}
        self.text_end = {}
        for item, var in self.tier_check_list.items():
            if var.get():
                self.get_selected_text(item)

    def get_selected_text(self, tier_name):
        self.selected_text[tier_name] = []
        self.text_start[tier_name] = []
        self.text_end[tier_name] = []
        try:
            # tier = next(t for t in self.tg_plot.tiers if t.name == tier_name)
            tier = next(t for t in self.tg.tiers if t.name == tier_name)
            for interval in tier.intervals:
                self.selected_text[tier_name].append(interval.mark)
                self.text_start[tier_name].append(interval.minTime)
                self.text_end[tier_name].append(interval.maxTime)
        except Exception as e:
            print("An error occurred:", e)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        sys.exit()

if __name__ == '__main__':
    root = Tk()
    Slicer(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    try:
        root.mainloop()
    except:
        pass