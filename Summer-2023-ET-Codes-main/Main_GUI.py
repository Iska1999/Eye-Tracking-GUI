from tkinter import *
from os import path
import os
from MasterUI import eye_tracking
from ED import event_detection
import pandas as pd

class FovioConfiguration:
    def __init__(self, input_file, output_file1, output_file2, dir_name, start_time, end_time, fixation_radius, duration_threshold,
                 participant_number, workload_type, missing_info_options,
                 display_scatter_plot, display_saccades):
        self.input_file = input_file
        self.output_file1 = output_file1
        self.output_file2 = output_file2
        self.dir_name = dir_name
        self.start_time = int(float(start_time))
        self.end_time = int(float(end_time))
        self.fixation_radius = int(float(fixation_radius))
        self.duration_threshold = int(float(duration_threshold))
        self.participant_number = participant_number
        self.workload_type = workload_type
        self.missing_info_options = bool(missing_info_options)
        self.display_scatter_plot = bool(display_scatter_plot)
        self.display_saccades = bool(display_saccades)

class GazepointConfiguration:
    def __init__(self, input_file, output_file1, output_file2, dir_name, start_time, end_time, fixation_radius, duration_threshold,
                 participant_number, workload_type, missing_info_options,
                 display_scatter_plot, display_saccades, performance_file, xError, yError):
        self.input_file = input_file
        self.output_file1 = output_file1
        self.output_file2 = output_file2
        self.dir_name = dir_name
        self.start_time = int(float(start_time))
        self.end_time = int(float(end_time))
        self.fixation_radius = int(float(fixation_radius))
        self.duration_threshold = int(float(duration_threshold))
        self.participant_number = participant_number
        self.workload_type = workload_type
        self.missing_info_options = bool(missing_info_options)
        self.display_scatter_plot = bool(display_scatter_plot)
        self.display_saccades = bool(display_saccades)
        self.performance_file = performance_file
        self.xError = int(xError)
        self.yError = int(yError)
        
def call_functions(config, Status):
    #input:
    input_file = config.input_file
    output_file1 = config.output_file1
    output_file2 = config.output_file2
    start_time = config.start_time
    end_time = config.end_time
    dir_name = config.dir_name
    #Check validity:
    if output_file1 == '' or output_file1== '':
        Status.configure(text='Status: Output file name not specified!')
        return
    
    if not (path.exists(input_file)):
        Status.configure(text='Status: Invalid input path!')  
        return 

    if (path.exists(dir_name)):
        Status.configure(text="Status: Output folder already exists!")
        return
    
    if (not (output_file1.endswith('.csv') and output_file2.endswith('.csv'))):
        Status.configure(text='Status: Output file must be a csv file!')
        return
    
    #Call functions:
    if (os.path.isdir(input_file)):
        read_directory(input_file, output_file1, output_file2, dir_name, config)
    else:
        if (not (input_file.endswith(".txt") or input_file.endswith(".csv"))):
            Status.configure(text='Status: Input file must be a .txt or .csv file!')
            return
        read_file(input_file, output_file1, output_file2, dir_name, config)

def read_directory(input_name, output_name1, output_name2, dir_name, config):
    os.mkdir(dir_name)
    for name in os.listdir(input_name):
        read_file(input_name + '/' + name, output_name1, output_name2, f"{dir_name}/{name[:-4]}", config)
    
def read_file(input_file, output_file1, output_file2, dir_name, config):    
    os.mkdir(dir_name)
    if (not input_file.endswith(".csv") and not input_file.endswith(".txt")):
        error_file = open(f"{dir_name}/read_error.txt", "a")
        error_file.write(input_file + " is not a .txt or .csv file\n")
        error_file.close()
        return
    
    if input_file.endswith(".txt"):
        convert_txt_to_csv(input_file, f"{input_file[:-4]}.csv")
    
    tracker_type = entry.get()
    performance_file = ""
    xError = 0
    yError = 0
    if (tracker_type):
        tracker_type = "Gazepoint"
        performance_file = config.performance_file
        xError = config.xError
        yError = config.yError
    else:
        tracker_type = "FOVIO"
    
    df = eye_tracking(input_file[:-4] + '.csv', config.start_time, config.end_time, config.missing_info_options, config.display_scatter_plot, dir_name, tracker_type, performance_file, xError, yError)
    event_detection(df, f"{dir_name}/{output_file1}", f"{dir_name}/{output_file2}", config.duration_threshold, config.fixation_radius, config.workload_type, config.participant_number, dir_name, config.display_saccades, tracker_type)
    
def convert_txt_to_csv(input_filename, output_filename):
    assert input_filename.endswith('.txt'), 'Input file must be a text file'
    assert output_filename.endswith('.csv'), 'Output file must be a csv file'
    
    df = pd.read_csv(input_filename, sep='\t', header=None, low_memory=False)
    df.to_csv(output_filename, index=False, header=False)

def displayFovioGUI():
    # Create a new window
    window = Tk()

    # Create frames
    frame0 = Frame(window)
    frame1 = Frame(window)
    frame2 = Frame(window)
    frame3 = Frame(window)
    frame4 = Frame(window)
    frame5 = Frame(window)
    frame6 = Frame(window)
    frame7 = Frame(window)
    frame8 = Frame(window)
    frame9 = Frame(window)
    frame10 = Frame(window)
    frame11 = Frame(window)
    frame12 = Frame(window)
    frame13 = Frame(window)
    frame14 = Frame(window)
    frame15 = Frame(window)
    frame16 = Frame(window)
    frame17 = Frame(window)
    frame18 = Frame(window)
    frame19 = Frame(window)
    frame20 = Frame(window)

    # Pack frames
    frame0.pack()
    frame1.pack()
    frame2.pack()
    frame3.pack()
    frame4.pack()
    frame5.pack()
    frame6.pack()
    frame7.pack()
    frame8.pack()
    frame9.pack()
    frame10.pack()
    frame11.pack()
    frame12.pack()
    frame13.pack()
    frame14.pack()
    frame15.pack()
    frame16.pack()
    frame17.pack()
    frame18.pack()
    frame19.pack()
    frame20.pack()

    window.title("Eye Tracking Event Detection")

    text1 = Label(frame0,
                text='\n Tracker Type: FOVIO\n')
    text1.pack()

    text2 = Label(frame1, text='Enter Input File/Folder Name (include .csv or .txt if file):  ')
    text2.pack(side=LEFT)
    input_name = Entry(frame1) # input name variable 
    input_name.pack(side=LEFT)

    text3 = Label(frame2, text='Enter Output Folder Name:                                                  ')
    text3.pack(side=LEFT)
    output_folder = Entry(frame2) #output name variable
    output_folder.pack(side=LEFT)

    text4 = Label(frame3, text='Enter Output 1 File Name (include .csv):                            ')
    text4.pack(side=LEFT)
    output_name1 = Entry(frame3) #output name variable
    output_name1.pack(side=LEFT)

    text5 = Label(frame4, text='Enter Output 2 File Name (include .csv):                            ')
    text5.pack(side=LEFT)
    output_name2 = Entry(frame4) #output name variable
    output_name2.pack(side=LEFT)

    text6 = Label(frame5, text='Enter start time(ms):                                                             ')
    text6.pack(side=LEFT)
    t0 = Entry(frame5) # input name variable 
    t0.pack(side=LEFT)

    text7 = Label(frame6, text='Enter end time (ms):                                                              ')
    text7.pack(side=LEFT)
    tf = Entry(frame6) #output name variable
    tf.pack(side=LEFT)

    text8 = Label(frame7, text='Enter Fixation Radius (px):                                                    ')
    text8.pack(side=LEFT)
    fix_radius = Entry(frame7)
    fix_radius.pack(side=LEFT)

    text9 = Label(frame8, text='Enter Fixation Duration Threshold (ms):                              ')
    text9.pack(side=LEFT) 
    dur_thresh = Entry(frame8)
    dur_thresh.pack(side=LEFT)

    text10 = Label(frame9, text='Enter Participant Number:                                                     ')
    text10.pack(side=LEFT)
    participant = Entry(frame9)
    participant.pack(side=LEFT)

    text11 = Label(frame10, text='Enter Workload type:                                                             ')
    text11.pack(side=LEFT)
    workload = Entry(frame10)
    workload.pack(side=LEFT)

    text12 = Label(frame11, text='\nMissing Data Check Information:\n')
    text12.pack()

    v = IntVar()  # Options variable

    button2 = Radiobutton(frame12,
                        text="Delete rows in output file                   ",
                        padx=20,
                        variable=v,
                        value=0)
    button2.pack()
    
    button3 = Radiobutton(frame13,
                        text="Mark in separate Excel file for review",
                        padx=20,
                        variable=v,
                        value=1)
    button3.pack()

    text13 = Label(frame14, text='\nDisplay Scatter Plots:\n')
    text13.pack()

    s = IntVar() 

    button4 = Radiobutton(frame15,
                        text="Yes",
                        padx=20,
                        variable=s,
                        value=1)
    button4.pack()
    
    button5 = Radiobutton(frame16,
                        text="No ",
                        padx=20,
                        variable=s,
                        value=0)
    button5.pack()

    text14 = Label(frame17, text='\nDisplay Saccades:\n')
    text14.pack()

    displaySaccades = IntVar()

    button6 = Radiobutton(frame18,
                        text="Yes",
                        padx=20,
                        variable=displaySaccades,
                        value=1)
    button6.pack()
    
    button7 = Radiobutton(frame19,
                        text="No ",
                        padx=20,
                        variable=displaySaccades,
                        value=0)
    button7.pack()

    Status = Label(frame20, text='Status: N/A')
    Status.pack()

    def execute():
        Status.configure(text='Status: Processing...')
        try:
            #Input validity:
            input_file = input_name.get()
            output_file1 = output_name1.get()
            output_file2 = output_name2.get()
            dir_name = output_folder.get()
            start_time = t0.get()
            end_time = tf.get()
            fixation_radius = fix_radius.get()
            duration_threshold = dur_thresh.get()
            participant_number = participant.get()
            workload_type = workload.get()
            missing_info_options = v.get()
            display_scatter_plot = s.get()
            display_saccades = displaySaccades.get()
            config = FovioConfiguration(input_file, output_file1, output_file2, dir_name, start_time, end_time, fixation_radius, duration_threshold,
                            participant_number, workload_type, missing_info_options, display_scatter_plot, display_saccades)
            call_functions(config, Status)
            Status.configure(text='Success!') 
        except:
            Status.configure(text='Status: Error!')
            raise

    one = Button(window, text="GO", width="10", height="2", command = execute)
    one.pack(side="top")

    window.mainloop()
    
    
def displayGazepointGUI():
    # Create a new window
    window = Tk()

    # Create frames
    frame0 = Frame(window)
    frame1 = Frame(window)
    frame2 = Frame(window)
    frame3 = Frame(window)
    frame4 = Frame(window)
    frame5 = Frame(window)
    frame6 = Frame(window)
    frame7 = Frame(window)
    frame8 = Frame(window)
    frame9 = Frame(window)
    frame10 = Frame(window)
    frame11 = Frame(window)
    frame12 = Frame(window)
    frame13 = Frame(window)
    frame14 = Frame(window)
    frame15 = Frame(window)
    frame16 = Frame(window)
    frame17 = Frame(window)
    frame18 = Frame(window)
    frame19 = Frame(window)
    frame20 = Frame(window)
    frame21 = Frame(window)
    frame22 = Frame(window)
    frame23 = Frame(window)
    frame24 = Frame(window)

    # Pack frames
    frame0.pack()
    frame1.pack()
    frame2.pack()
    frame3.pack()
    frame4.pack()
    frame5.pack()
    frame6.pack()
    frame7.pack()
    frame8.pack()
    frame9.pack()
    frame10.pack()
    frame11.pack()
    frame12.pack()
    frame13.pack()
    frame14.pack()
    frame15.pack()
    frame16.pack()
    frame17.pack()
    frame18.pack()
    frame19.pack()
    frame20.pack()
    frame21.pack()
    frame22.pack()
    frame23.pack()
    frame24.pack()  

    window.title("Eye Tracking Event Detection")

    text1 = Label(frame0,
                text='\n Tracker Type: GAZEPOINT\n')
    text1.pack()

    text2 = Label(frame1, text='Enter Input File/Folder Name (include .csv or .txt if file):  ')
    text2.pack(side=LEFT)
    input_name = Entry(frame1) # input name variable 
    input_name.pack(side=LEFT)

    text3 = Label(frame2, text='Enter Output Folder Name:                                                  ')
    text3.pack(side=LEFT)
    output_folder = Entry(frame2) #output name variable
    output_folder.pack(side=LEFT)

    text4 = Label(frame3, text='Enter Output 1 File Name (include .csv):                            ')
    text4.pack(side=LEFT)
    output_name1 = Entry(frame3) #output name variable
    output_name1.pack(side=LEFT)

    text5 = Label(frame4, text='Enter Output 2 File Name (include .csv):                            ')
    text5.pack(side=LEFT)
    output_name2 = Entry(frame4) #output name variable
    output_name2.pack(side=LEFT)

    text6 = Label(frame5, text='Enter start time(ms):                                                             ')
    text6.pack(side=LEFT)
    t0 = Entry(frame5) # input name variable 
    t0.pack(side=LEFT)

    text7 = Label(frame6, text='Enter end time (ms):                                                              ')
    text7.pack(side=LEFT)
    tf = Entry(frame6) #output name variable
    tf.pack(side=LEFT)

    text8 = Label(frame7, text='Enter Fixation Radius (px):                                                    ')
    text8.pack(side=LEFT)
    fix_radius = Entry(frame7)
    fix_radius.pack(side=LEFT)

    text9 = Label(frame8, text='Enter Fixation Duration Threshold (ms):                              ')
    text9.pack(side=LEFT) 
    dur_thresh = Entry(frame8)
    dur_thresh.pack(side=LEFT)

    text10 = Label(frame9, text='Enter Participant Number:                                                     ')
    text10.pack(side=LEFT)
    participant = Entry(frame9)
    participant.pack(side=LEFT)

    text11 = Label(frame10, text='Enter Workload type:                                                             ')
    text11.pack(side=LEFT)
    workload = Entry(frame10)
    workload.pack(side=LEFT)
    
    text12 = Label(frame11, text="Enter Performance File Path:                                                ")
    text12.pack(side=LEFT)
    performance_file = Entry(frame11)
    performance_file.pack(side=LEFT)
    
    text13 = Label(frame13, text="Enter xError:                                                                           ")
    text13.pack(side=LEFT)
    xError = Entry(frame13)
    xError.pack(side=LEFT)
    
    text14 = Label(frame14, text="Enter yError:                                                                           ")
    text14.pack(side=LEFT)
    yError = Entry(frame14)
    yError.pack(side=LEFT)

    text15 = Label(frame15, text='\nMissing Data Check Information:\n')
    text15.pack()

    v = IntVar()  # Options variable

    button2 = Radiobutton(frame16,
                        text="Delete rows in output file                   ",
                        padx=20,
                        variable=v,
                        value=0)
    button2.pack()
    
    button3 = Radiobutton(frame17,
                        text="Mark in separate Excel file for review",
                        padx=20,
                        variable=v,
                        value=1)
    button3.pack()

    text16 = Label(frame18, text='\nDisplay Scatter Plots:\n')
    text16.pack()

    s = IntVar() 

    button4 = Radiobutton(frame19,
                        text="Yes",
                        padx=20,
                        variable=s,
                        value=1)
    button4.pack()
    
    button5 = Radiobutton(frame20,
                        text="No ",
                        padx=20,
                        variable=s,
                        value=0)
    button5.pack()

    text17 = Label(frame21, text='\nDisplay Saccades:\n')
    text17.pack()

    displaySaccades = IntVar()

    button6 = Radiobutton(frame22,
                        text="Yes",
                        padx=20,
                        variable=displaySaccades,
                        value=1)
    button6.pack()
    
    button7 = Radiobutton(frame23,
                        text="No ",
                        padx=20,
                        variable=displaySaccades,
                        value=0)
    button7.pack()

    Status = Label(frame24, text='Status: N/A')
    Status.pack()

    def execute():
        try:
            Status.configure(text='Status: Processing...')
            input_file = input_name.get()
            output_file1 = output_name1.get()
            output_file2 = output_name2.get()
            dir_name = output_folder.get()
            start_time = t0.get()
            end_time = tf.get()
            fixation_radius = fix_radius.get()
            duration_threshold = dur_thresh.get()
            participant_number = participant.get()
            workload_type = workload.get()
            missing_info_options = v.get()
            display_scatter_plot = s.get()
            display_saccades = displaySaccades.get()
            performance_file = performance_file.get()
            xError = xError.get()
            yError = yError.get()
            config = GazepointConfiguration(input_file, output_file1, output_file2, dir_name, start_time, end_time, fixation_radius, duration_threshold,
                            participant_number, workload_type, missing_info_options, display_scatter_plot, display_saccades, performance_file, xError, yError)
            call_functions(config, Status)
            Status.configure(text='Success!')
        except:
            Status.configure(text='Status: Error!')
            raise
        

    one = Button(window, text="GO", width="10", height="2", command = execute)
    one.pack(side="top")

    window.mainloop()
    
    
def process_input():
    user_input = entry.get()  # Retrieve the input value
    window.destroy()
    if not user_input:
        displayFovioGUI()  
    else:
        displayGazepointGUI()
        
# Create tkinter window
window = Tk()

# Set window dimensions
window.geometry("350x250") 

# Create frames
frame0 = Frame(window)
frame1 = Frame(window)
frame2 = Frame(window)
frame3 = Frame(window)

# Pack frames
frame0.pack()
frame1.pack()
frame2.pack()
frame3.pack()

window.title("Eye Tracking Event Detection")

text1 = Label(frame0,
            text='\nChoose a tracker: \n')
text1.pack()

entry = IntVar()  # Tracker Type

button1 = Radiobutton(frame1,
                    text="Gazepoint",
                    padx=20,
                    variable=entry,
                    value=1)
button1.pack()

button2 = Radiobutton(frame2,
                    text="FOVIO      ",
                    padx=20,
                    variable=entry,
                    value=0)
button2.pack()

# Create submit button
submit_btn = Button(window, text="Next", command=process_input)
submit_btn.pack()

# Run the tkinter event loop
window.mainloop()