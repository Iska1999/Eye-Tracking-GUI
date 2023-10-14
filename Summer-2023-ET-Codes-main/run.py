import os
import pandas as pd
from MasterUI import eye_tracking
from ED import event_detection

#Input Parameters:
tracker_type = "FOVIO"
startEndTimes = pd.read_excel('StartEndTimes.xlsx', header=None)
input_dir = "Participant 1"
output_dir = "Participant 1 results"
output_file1 = "output1.csv"
output_file2 = "output2.csv"
fixation_radius = 80
duration_threshold = 100
missing_info_options = 1
display_scatter_plot = 0
display_saccades = 1
participant_number = ""
workload_type = ""

class Configuration:
    def __init__(self, start_time, end_time, fixation_radius, duration_threshold,
                 participant_number, workload_type, missing_info_options,
                 display_scatter_plot, display_saccades):
        self.start_time = int(float(start_time))
        self.end_time = int(float(end_time))
        self.fixation_radius = int(float(fixation_radius))
        self.duration_threshold = int(float(duration_threshold))
        self.participant_number = participant_number
        self.workload_type = workload_type
        self.missing_info_options = int(missing_info_options)
        self.display_scatter_plot = int(display_scatter_plot)
        self.display_saccades = int(display_saccades)

def convert_filename_to_rowIndex(file_name):
    ans = ""
    i = 0
    while (i<len(file_name) and not file_name[i].isdigit()):
        i += 1
    
    while (i<len(file_name) and file_name[i].isdigit() and len(ans)<2):
        ans += file_name[i]
        i += 1  
        
    letter = file_name[-5].upper()
    if (letter == "T" or letter == "D"):
        ans += letter
        
    if (ans.isdigit()):
        ans = int(ans)
        
    return ans
    
def read_configuration(startEndTimes, file):
    rowIndex = convert_filename_to_rowIndex(file)
    start_time = startEndTimes.loc[startEndTimes[0] == rowIndex][1].values[0]
    end_time = startEndTimes.loc[startEndTimes[0] == rowIndex][2].values[0]
    return Configuration(start_time, end_time, fixation_radius, duration_threshold, participant_number, workload_type, missing_info_options, display_scatter_plot, display_saccades)

def convert_txt_to_csv(input_filename, output_filename):
    assert input_filename.endswith('.txt'), 'Input file must be a text file'
    assert output_filename.endswith('.csv'), 'Output file must be a csv file'
    
    df = pd.read_csv(input_filename, sep='\t', header=None, low_memory=False)
    df.to_csv(output_filename, index=False, header=False)

def read_file(input_file, output_file1, output_file2, dir_name, config):    
    os.mkdir(dir_name)
    if (input_file.endswith(".txt")):
        convert_txt_to_csv(input_file, f"{input_file[:-4]}.csv")
    df = eye_tracking(input_file[:-4] + '.csv', config.start_time, config.end_time, config.missing_info_options, config.display_scatter_plot, dir_name, tracker_type)
    event_detection(df, f"{dir_name}/{output_file1}", f"{dir_name}/{output_file2}", config.duration_threshold, config.fixation_radius, config.workload_type, config.participant_number, dir_name, config.display_saccades, tracker_type)

os.mkdir(output_dir)
for file in os.listdir(input_dir):
    try:
        config = read_configuration(startEndTimes, file)
        read_file(input_dir + '/' + file, output_file1, output_file2, f"{output_dir}/{file[:-4]}", config)
    except Exception as e:
        print(f"Error in {file} : {e}")
        
    