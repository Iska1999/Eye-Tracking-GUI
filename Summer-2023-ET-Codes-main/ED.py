"""
Created on Wed Aug 26 11:24:49 2020
@author: Jad Atweh
"""
import pandas as pd
from scipy.signal import find_peaks
import math

def event_detection(df, out_file1, out_file2, duration_threshold, spatial_threshold, workload_type, participant_number, dir_path, display_saccades, tracker_type):
    if (tracker_type == "FOVIO"):
        samp_rate=16.6667
    elif (tracker_type == "Gazepoint"):
        samp_rate=6.66667
        
    time = df["MissionTime"]
    velocities = df["Velocity (degrees of visual angle/second)"]
    time = list(time) 
    velocities = list(velocities)

    PT = df["Peak Threshold"].iloc[0]
    onset_threshold = df["Onset Threshold"].iloc[0]
    offset_threshold = df["Offset Threshold"].iloc[0]

    onsets_times = []
    onsets_velocities = []
    onset_indices=[]
    offsets_times = []
    offsets_velocities = [] 
    offset_indices=[]
    peak_velocities=[]
    sac_amps= []
    saccade_duration = []

    eyetracking_statistics = open(f"{dir_path}/eyetracking_statistics.txt", "w")
    invalid_data = open(f"{dir_path}/invalid_data.txt", "w")

    ################################## FINDING ALL PEAK VELOCITIES #################################
    indices_of_peak_velocities = find_peaks(velocities, height = PT)[0]
    eyetracking_statistics.write(str(len(indices_of_peak_velocities)) + ' saccade peaks were detected\n')
    for each in range(len(indices_of_peak_velocities)):
        index=indices_of_peak_velocities[each]
        peak_velocities.append(velocities[index])
    average_peak_velocity=sum(peak_velocities)/len(peak_velocities)
    max_peak_velocity=max(peak_velocities)
    
    eyetracking_statistics.write(str(average_peak_velocity) + ' is the average peak velocity\n')
    eyetracking_statistics.write(str(max_peak_velocity) + ' is the max peak velocity\n')
    
    ################################## FINDING ALL ONSETS ################################
    onset_indices, onsets_times, onsets_velocities = find_onsets(indices_of_peak_velocities, velocities, onset_threshold, time)
    df["OnsetsTimes"] = pd.Series(onsets_times)
    df["OnsetsVelocities"] = pd.Series(onsets_velocities)
    
    ################################## FINDING ALL OFFSETS #################################
    offset_indices, offsets_times, offsets_velocities = find_offsets(indices_of_peak_velocities, velocities, offset_threshold, time)
    df["OffsetsTimes"] = pd.Series(offsets_times)
    df["OffsetsVelocities"] = pd.Series(offsets_velocities)
    
    ###################################### FIXATION DETECTION CODE ######################################### 
    fixation_indices = find_fixation_indices(onset_indices, offset_indices, velocities)
    eyetracking_statistics.write(str(len(fixation_indices)) + ' fixations were detected before constraints\n')
    fixations_after_constraints, fixation_center_points = find_fixations_after_constraints(df, spatial_threshold, samp_rate, duration_threshold, fixation_indices)
    eyetracking_statistics.write(str(len(fixations_after_constraints)) + ' fixations were detected after constraints\n')
    
    ###################################### SACCADES ######################################### 
    if (display_saccades):
        saccade_duration = find_saccade_durations(onsets_times, offsets_times)
        sac_amps = find_saccade_amplitudes(df, onsets_times, offsets_times)
    
    ###################################### AOI ######################################### 
    AOI=map_fixation_to_AOI(df, fixation_center_points)
        
    ########################################## CREATING OUTPUT FILE 2 ###########################################
    out = create_output_file2(df, fixation_center_points, onsets_times, offsets_times, samp_rate, sac_amps, saccade_duration, fixations_after_constraints, AOI, workload_type, participant_number, invalid_data, eyetracking_statistics, display_saccades, tracker_type)
 
    ########################################## CONVERT OUTPUT FILES TO CSV ###########################################
    df.to_csv(out_file1, index=False)
    out.to_csv(out_file2,index=False)

    eyetracking_statistics.close()
    invalid_data.close()
          
def find_onsets(peak_velocities_indices, velocities, onset_threshold, time):
    left_most=0
    onset_indices = []
    onsets_velocities = []
    onsets_times = []
    for each in range(len(peak_velocities_indices)):
        i=peak_velocities_indices[each]
        flag=False
        for v in range(i,left_most,-1):
            #this flag will tell us if we've found an onset
            if velocities[v]<onset_threshold and velocities[v]-velocities[v-1]<0 and velocities[v]-velocities[v+1]<0:
                    onset_indices.append(v)
                    onsets_velocities.append(velocities[v])
                    onsets_times.append(time[v])
                    #when we write in excel or text, we say peak #1 had onset velcoties[j]
                    #When flag is True, we correctly found onset
                    flag=True
                    break
        if not flag:
            onset_indices.append(i-1)
            onsets_times.append(999999)
            onsets_velocities.append(999999)
        left_most=i
    return onset_indices, onsets_times, onsets_velocities  

def find_offsets(peak_velocities_indices, velocities, offset_threshold, time):
    offset_indices = []
    offsets_velocities = []
    offsets_times = []
    for each in range(len(peak_velocities_indices)):
        i=peak_velocities_indices[each]
        if each==len(peak_velocities_indices)-1:
            right_most=len(velocities)-1
        else:
            right_most=peak_velocities_indices[each+1]
        flag=False   
        for v in range(i,right_most,1):
            if velocities[v]<offset_threshold:
                offset_indices.append(v)
                offsets_velocities.append(velocities[v])
                offsets_times.append(time[v])
                flag=True
                break
        if not flag:
            offset_indices.append(i+1)
            offsets_times.append(0)
            offsets_velocities.append(0)
    return offset_indices, offsets_times, offsets_velocities

def find_fixation_indices(onset_indices, offset_indices, velocities):
    fixation_indices=[]
    mini_lst = []
    
    #Need 3 while loops to find all the fixation indices in a file. 
    #The first searches for fixation indices before the first onset,
    #the second searches for fixation indices between the first saccade's offset to the last saccade's onset, 
    #and the third searches for fixation indices after the last saccade's offset
    
    #initialize list variables for searching for fixation indices
    fixation_indices=[]
    mini_lst = []
    j=0
    while j < onset_indices[0]:
        mini_lst.append(j)
        j+=1
    fixation_indices.append(mini_lst)
    
    for i in range(len(offset_indices)-1):
        j=offset_indices[i] + 1
        mini_lst = []
        while j < onset_indices[i+1]:
            mini_lst.append(j)
            j+=1
        fixation_indices.append(mini_lst)
        
    j=(offset_indices[len(offset_indices)-1])+1 #go to the index where the last offset was detected as the starting point to find the last collection of fixation indices
    mini_lst = []
    while j < len(velocities):#want to search across all velocities past the last saccade's offset so use the filtered velocity list as the structure to base this off of
        mini_lst.append(j)
        j+=1
    fixation_indices.append(mini_lst)
    return fixation_indices
        
#distance formula
def calculateDistance(x1,y1,x2,y2):  
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
    return dist  
   
def find_fixations_after_constraints(df, spatial_threshold, samp_rate, duration_threshold, fixation_indices):
    fixations_after_constraints = []
    center_points = []
    for fixation in fixation_indices:  
        if len(fixation) < 2: 
            continue
        
        index=1 
        center_index = 0
        center = fixation[center_index]
        fix_lst = [center]
        while index < len(fixation): 
            current_point = fixation[index]

            dist = calculateDistance(
                df.at[center, "BestPogX"],
                df.at[center, "BestPogY"],
                df.at[current_point, "BestPogX"],
                df.at[current_point, "BestPogY"]
            )

            if dist <= spatial_threshold:
                fix_lst.append(fixation[index])
                index+=1
                
                if index >= len(fixation):
                    if (len(fix_lst)-1) * samp_rate > duration_threshold:
                        fixations_after_constraints.append(fix_lst)
                        center_points.append(fix_lst[0])
            else:                                   
                if (len(fix_lst)-1) * samp_rate > duration_threshold:
                    fixations_after_constraints.append(fix_lst)
                    center_points.append(fix_lst[0])
                    #reset all indice/counters for next loop with a new center
                    center_index=index
                    index+=1
                else:
                    center_index+=1
                    index=center_index+1
                center=fixation[center_index]
                fix_lst=[center]
                            
    return fixations_after_constraints, center_points

def find_saccade_durations(onsets_times, offsets_times):
    saccade_duration=[]
    for each in range(len(onsets_times)):
        s=offsets_times[each]-onsets_times[each]
        saccade_duration.append(s)
    return saccade_duration

def find_saccade_amplitudes(df, onsets_times, offsets_times):
    sac_amps = []
    for i in range(len(onsets_times)):
        df1=df[(df.MissionTime>=onsets_times[i])&(df.MissionTime<=offsets_times[i])] #create a mini dataframe consisting of the data of 1 saccade
        vel = df1['Velocity (degrees of visual angle/second)'].sum() #sum the velocity values
        count=df1.MissionTime.count() #get number of elements to use in average calculation
        if (float(count!=0)):
            avg= float(vel)/float(count)
            time_diff = (offsets_times[i] - onsets_times[i])
            sac_amp = avg * time_diff
            sac_amps.append(sac_amp)
        else:
            sac_amps.append(0) #This value will be discarded, it is only to keep the list value in check with all other lists to prevent out of range errors
    return sac_amps

def map_fixation_to_AOI(df, fixation_center_points):
    AOI=[]
    for each in range(len(fixation_center_points)):
        if 0<=df.at[fixation_center_points[each], "BestPogX"]<=1010 and 0<=df.at[fixation_center_points[each], "BestPogY"]<=927:
            AOI.append('AOI 1: Map')
        elif 0<=df.at[fixation_center_points[each], "BestPogX"]<=1010 and 951<=df.at[fixation_center_points[each], "BestPogY"]<=1600:
            AOI.append('AOI 2: Reroute Menu')
        elif 1036<=df.at[fixation_center_points[each], "BestPogX"]<=2560 and 0<=df.at[fixation_center_points[each], "BestPogY"]<811:
            AOI.append('AOI 3: Video Feeds')
        elif 1036<=df.at[fixation_center_points[each], "BestPogX"]<=2560 and 811<=df.at[fixation_center_points[each], "BestPogY"]<=1157:
            AOI.append('AOI 4: Fuel Leak Bars')
        elif 1036<=df.at[fixation_center_points[each], "BestPogX"]<=2560 and 1179<=df.at[fixation_center_points[each], "BestPogY"]<=1600:
            AOI.append('AOI 5: Chat Message Panel')
        else:
            #a special case if the centroid landed on any of the grey or black distances seperating each AOI
            AOI.append('Fixation is not in any of the designated AOIs')
    return AOI

def create_output_file2(df, fixation_center_points, onsets_times, offsets_times, samp_rate, sac_amps, saccade_duration, fixations_after_constraints, AOI, workload_type, participant_number, invalid_data_file, eyetracking_statistics_file, displaySaccades, tracker_type):
    out_data = []
    out_event=[]
    out_start_time = []
    out_amp =[]
    out_X=[]
    out_Y=[]
    out_duration = []
    out_AOI = []
    fixation_start_time = []
    for i in range(len(fixation_center_points)):
       fixation_start_time.append(df.at[fixation_center_points[i],"MissionTime"]) #Find start times of fixation from time of center point

    out =pd.DataFrame(out_data,columns=['Participant Number','Workload','Eyetracker','Event Type','Start time (s)','Duration (ms)','Amplitude (degrees)','X','Y','AOI'])
    i=0 #counter for saccades
    j=0 #counter for fixations
    while (i != len(onsets_times) and j != len(fixation_start_time)): 
        if (onsets_times[i] < fixation_start_time[j] and displaySaccades): #if saccade comes before fixation
            if(offsets_times[i] == 0):
                invalid_data_file.write('Invalid saccade detected (missed offset) and its onset time is '+str(onsets_times[i])+' s\n')
                i=i+1
            else:
                out_event.append("Saccade")
                out_amp.append(sac_amps[i]) 
                out_start_time.append(onsets_times[i])
                out_duration.append(saccade_duration[i])
                out_X.append("N/A")
                out_Y.append("N/A")
                out_AOI.append("N/A")
                i=i+1
        else: #Fixation comes before saccade
            if (onsets_times[i]==999999 and displaySaccades):
                invalid_data_file.write('Invalid saccade detected (missed onset) and its offset is '+str(offsets_times[i])+' s\n')
                i=i+1
            else:
                out_event.append("Fixation")
                out_amp.append("N/A")
                out_start_time.append(fixation_start_time[j]) #Find time of the center of the fixation
                out_duration.append((len(fixations_after_constraints[j])-1)*samp_rate) 
                out_X.append(df.at[fixation_center_points[j],"BestPogX"]) #Find X of the center of the fixation
                out_Y.append(df.at[fixation_center_points[j],"BestPogY"]) #Find Y of the center of the fixation
                out_AOI.append(AOI[j])
                j=j+1
  
    while (i < len(onsets_times) and displaySaccades):
        if(offsets_times[i] == 0):
            invalid_data_file.write('Invalid saccade detected (missed offset) and its onset time is '+str(onsets_times[i])+' s\n')
            i=i+1
        elif (onsets_times[i]==999999):
            invalid_data_file.write('Invalid saccade detected (missed onset) and its offset is '+str(offsets_times[i])+' s\n')
            i=i+1
        else:
            out_event.append("Saccade")
            out_amp.append(sac_amps[i]) 
            out_start_time.append(onsets_times[i])
            out_duration.append(saccade_duration[i])
            out_X.append("N/A")
            out_Y.append("N/A")
            out_AOI.append("N/A")
            i=i+1                        
                
    while (j < len(fixation_start_time)):            
        out_event.append("Fixation")
        out_amp.append("N/A")
        out_start_time.append(fixation_start_time[j]) #Find time of the center of the fixation
        out_duration.append((len(fixations_after_constraints[j])-1)*samp_rate) 
        out_X.append(df.at[fixation_center_points[j],"BestPogX"]) #Find X of the center of the fixation
        out_Y.append(df.at[fixation_center_points[j],"BestPogY"]) #Find Y of the center of the fixation
        out_AOI.append(AOI[j])
        j=j+1
               
    out["Event Type"] = out_event
    out["Start time (s)"] = out_start_time
    out["Duration (ms)"] = out_duration
    out["Amplitude (degrees)"] = out_amp
    out["X"] = out_X
    out["Y"] = out_Y
    out["AOI"] = out_AOI
    out['Eyetracker'] = tracker_type
    out["Workload"] = workload_type
    out["Participant Number"] = participant_number
    
    eyetracking_statistics_file.write("Sanity check that all valid saccades outputted to Output file 2 (should equal # of saccade peaks): "+str(i)+"\n")
    eyetracking_statistics_file.write("Sanity check that all valid fixations outputted to Output file 2 (should equal # of fixations detected): "+str(j)+"\n")
    return out