from tkinter import *
import pandas as pd
import os
from MasterUI import eye_tracking
from ED import event_detection
import sys

class FovioConfiguration:
    def __init__(self, start_time, end_time, fixation_radius, duration_threshold, participant_number,
                 workload_type, missing_info_options, display_scatter_plot, display_saccades):
        self.start_time = int(float(start_time))
        self.end_time = int(float(end_time))
        self.fixation_radius = int(float(fixation_radius))
        self.duration_threshold = int(float(duration_threshold))
        self.participant_number = participant_number
        self.workload_type = workload_type
        self.missing_info_options = int(missing_info_options)
        self.display_scatter_plot = int(display_scatter_plot)
        self.display_saccades = int(display_saccades)

class GazepointConfiguration:
    def __init__(self, start_time, end_time, fixation_radius, duration_threshold, participant_number,
                 workload_type, missing_info_options, display_scatter_plot, display_saccades, performance_file, xError, yError):
        self.start_time = int(float(start_time))
        self.end_time = int(float(end_time))
        self.fixation_radius = int(float(fixation_radius))
        self.duration_threshold = int(float(duration_threshold))
        self.participant_number = participant_number
        self.workload_type = workload_type
        self.missing_info_options = int(missing_info_options)
        self.display_scatter_plot = int(display_scatter_plot)
        self.display_saccades = int(display_saccades)
        self.performance_file = performance_file
        self.xError = int(xError)
        self.yError = int(yError)

def convert_txt_to_csv(input_filename, output_filename):
    assert input_filename.endswith('.txt'), 'Input file must be a text file'
    assert output_filename.endswith('.csv'), 'Output file must be a csv file'
    
    df = pd.read_csv(input_filename, sep='\t', header=None, low_memory=False)
    df.to_csv(output_filename, index=False, header=False)

def read_file(input_file, output_file1, output_file2, dir_name, config):    
    os.mkdir(dir_name)
    
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

def call_functions(spreadsheet_path, output_folder_name, input_directory_path, tracker_type, Status):
    os.mkdir(output_folder_name)
    df = pd.read_csv(spreadsheet_path)

    for index, row in df.iterrows():
        input_file = row['Input File Name']
        try:
            if (tracker_type == "FOVIO"):
                config = FovioConfiguration(row['Start Time'], row['End Time'], row["Fixation Radius"], row["Duration Threshold"], row["Participant Number"], row["Workload Type"], row["Missing Data Check Information"], row["Display Scatter Plot"], row["Display Saccades"])
            elif (tracker_type == "Gazepoint"):
                config = GazepointConfiguration(row['Start Time'], row['End Time'], row["Fixation Radius"], row["Duration Threshold"], row["Participant Number"], row["Workload Type"], row["Missing Data Check Information"], row["Display Scatter Plot"], row["Display Saccades"], row["Performance File"], row["xError"], row["yError"])
                
            read_file(f"{input_directory_path}/{input_file}", "Output1.csv", "Output2.csv", f"{output_folder_name}/{input_file[:-4]}", config)
        except Exception as e:
            print(e)
            errorLog = open("ErrorLog.txt", "a")
            errorLog.write(f"Error with {input_file}\n")
            errorLog.close()
    Status.configure(text='Success!') 

def GUI():
    if (entry.get()):
        tracker_type = "Gazepoint"
    else:
        tracker_type = "FOVIO"
    
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

    window.title("Eye Tracking Event Detection")

    text1 = Label(frame0, text=f"\n Tracker Type: {tracker_type}\n")
    text1.pack()

    text = "\n Each row in the spreadsheet must follow the specified column format (columns must also have the same name):\n\nInput File Name\nStart Time (ms)\nEnd Time (ms)\nMissing Data Check Information (1 to delete rows in output file and 0 to mark in separate Excel file for review)\nDisplay Scatter Plot (1 to display and 0 to not display)\nDisplay Saccades (1 to display and 0 to not display)\nDuration Threshold (ms)\nFixation Radius (pixels)\nParticipant Number\nWorkload Type\n"
    if (tracker_type == "Gazepoint"):
        text += "Performance File\nxError\nyError\n\n"
    text += "\nNote: Please refrain from including the parentheses in the column names of the spreadsheet.\n"
    
    text2 = Label(frame1,
                text=text)
    text2.pack()

    text3 = Label(frame2,
                text='Enter Spreadsheet Name (include .csv):  ')
    text3.pack(side=LEFT)
    spreadsheet_name = Entry(frame3) # input name variable 
    spreadsheet_name.pack(side=LEFT)

    text4 = Label(frame4,
                    text='Enter Input Directory Path:  ')
    text4.pack()
    input_directory = Entry(frame5) #input directory variable
    input_directory.pack(side=LEFT)

    text5 = Label(frame6,
                text='Enter Output Folder Name:  ')
    text5.pack()
    output_folder = Entry(frame7) #output name variable
    output_folder.pack(side=LEFT)

    Status = Label(frame8, text='Status: N/A')
    Status.pack()

    def read_input():
        spreadsheet_path = spreadsheet_name.get()
        output_folder_name = output_folder.get()
        input_directory_path = input_directory.get()
        return [spreadsheet_path, output_folder_name, input_directory_path]

    one = Button(window, text="GO", width="10", height="2", command=lambda: call_functions(read_input()[0], read_input()[1], read_input()[2], tracker_type, Status))
    one.pack(side="top")

    window.mainloop()


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
                    text="GazePoint",
                    padx=20,
                    variable=entry,
                    value=1).pack()
button2 = Radiobutton(frame2,
                    text="FOVIO      ",
                    padx=20,
                    variable=entry,
                    value=0).pack()
# Create submit button
submit_btn = Button(window, text="Next", command=GUI)
submit_btn.pack()

# Run the tkinter event loop
window.mainloop()