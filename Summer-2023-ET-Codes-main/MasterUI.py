import pandas as pd
import statistics
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import DataQuality

def eye_tracking(file_name, start_time, end_time, missing_info_options, display_scatter, dir_path, tracker_type, performance_file="", xError=0, yError=0):
    # We will use the start and end times to only use the data within these two values and discard all the rest
    df = pd.read_csv(file_name) 
    
    if (tracker_type == 'FOVIO'): 
        df = addMissionTime(df, start_time, end_time)
        df.reset_index(drop=True, inplace=True)
        df = AddBestPog(df)
    elif (tracker_type == 'Gazepoint'):
        df = preProcessGazepoint(df)
        df = DataQuality.dq(df, performance_file, xError, yError)
        
    df=missingDataCheck(df,file_name, missing_info_options, display_scatter, dir_path, tracker_type)
    df=VelocityCalculation(df, tracker_type)
    df=ThresholdEstimation(df)
    
    # after all changes are made
    df.drop(df.filter(regex="Unnamed"),axis=1, inplace=True)
    if 'Panel' in df.columns:
        del df['Panel']
    if 'Panel.1' in df.columns:
        del df['Panel.1']
    if 'Occurences' in df.columns:
        del df['Occurences']
        
    return df

def addMissionTime(df, start_time, end_time):
    MissionTime=[0]
    Time=df["Capture Time"]
    for k in range(len(df)-1):
        MissionTime.append(float(MissionTime[k]+((Time[k+1]-Time[k])/1000))) #put MissionTime in milliseconds
    df['MissionTime'] = MissionTime
    
    df=df[(df['MissionTime']>=start_time)&(df['MissionTime']<=end_time)]
    
    return df

def preProcessGazepoint(df):
    # Default width is 2560 and default height is 1440 for Gazepoint
    # Tracker used is that of experiment 1
    # all the names of the columns we want to convert proportions to pixels for
    width_of_screen = int(2560)
    height_of_screen = int(1440)
    column_names_X = ['CursorX', 'LeftEyeX', 'RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX',
                        'LeftPupilX', 'RightPupilX']
    column_names_Y = ['CursorY', 'LeftEyeY', 'RightEyeY', 'FixedPogY', 'LeftPogY', 'RightPogY', 'BestPogY',
                        'LeftPupilY', 'RightPupilY']
    column_names_bool = ['LeftEyePupilValid', 'RightEyePupilValid', 'FixedPogValid', 'LeftPogValid',
                            'RightPogValid', 'BestPogValid', 'LeftPupilValid', 'RightPupilValid', 'MarkerValid']

    # turn TRUES and FALSES to 1s and 0s
    for each in column_names_bool:
        df[each].replace(True, 1, inplace=True)
        df[each].replace(False, 0, inplace=True)
        
    # CHANGE RESOLUTION OF X HERE
    for each in column_names_X:
        df[each] = df[each].multiply(width_of_screen)

    # CHANGE RESOLUTION OF Y HERE
    for each in column_names_Y:
        df[each] = df[each].multiply(height_of_screen)

def AddBestPog(df):
    # Find BestPogX and BestPogY values for FOVIO tracker
    BestPogX = []
    BestPogY = []
    for i in range(0,len(df.index)):
        if (df['Lft X Pos'][i]==0) and (df['Rt X Pos'][i] ==0):
            BestPogX.append(0)
        else:
            if (df['Lft X Pos'][i]!=0):
                BestPogX.append((df['Lft X Pos'][i]))
            elif (df['Rt X Pos'][i]!=0):
                BestPogX.append((df['Rt X Pos'][i]))
            
        if (df['Lft Y Pos'][i]==0) and (df['Rt Y Pos'][i] ==0):
            BestPogY.append(0)
        else:
            if (df['Lft Y Pos'][i]!=0):
                BestPogY.append((df['Lft Y Pos'][i]))
            elif (df['Rt Y Pos'][i]!=0):
                BestPogY.append((df['Rt Y Pos'][i]))                  
    df['BestPogX'] = BestPogX #Create a new column and append BestPogX
    df['BestPogY'] = BestPogY #Create a new column and append BestPogY
    return df  

def missingDataCheck(df,file, missing_info_options, display_scatter, dir_path, tracker_type):
    errorLog = open(f"{dir_path}/ErrorLog.txt", "w+")
    errorLog.write(
    'File name:'+str(file)+'\n')
    errorLog.write(
    '-------------------------------------------------------------------------'+'\n')
    
    errorLog_Statistics = open(f"{dir_path}/ErrorLog_Statistics.txt", "w+")
    
    X_coords = []
    Y_coords = []
    negative_coordinates = []
    missing_packets = []
    marker_bad = []
    final_index = len(df.index)
    final_time = df.iloc[-1]['Capture Time'] 
    
    '''----------checking errors in the file-----------------'''
    #Function returns the following lists given the dataframe       
    if (tracker_type == 'FOVIO'):
        negative_coordinates,missing_packets,X_coords,Y_coords = CheckErrorsFovio(df, errorLog)
    elif (tracker_type == 'Gazepoint'):
        negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords = checkErrorsGazepoint(df, errorLog)
        
    '''----------gathering statistics-----------------'''
    Statistics(negative_coordinates, missing_packets, marker_bad, final_index, final_time, errorLog_Statistics, tracker_type)
    
    '''----------deleting errors from file-----------------'''
    # combining the lists together for duplicate rows
    combined_list = list(set(negative_coordinates).union(set(marker_bad)))
    df=DeleteErrors(combined_list,missing_packets,df, missing_info_options)
    
    '''-------------displaying the plot-------------------'''
    if (display_scatter):
        ScatterPlot(X_coords,Y_coords,file)
        
    '''-------------displaying the plot-------------------'''
    TimeGap(df, errorLog_Statistics, tracker_type)
    errorLog.close()
    errorLog_Statistics.close()
    return df
    
def Statistics(negative_coords, missing_data, bad_markers, final_index, final_time, output_file, tracker_type):  
    output_file.write("\nError Statistics\n")  
    #writing summary statistics
    output_file.write(f"\nTotal Negative/Zero/Impossible Coordinates: {str(len(negative_coords))}\n")
    output_file.write(f"Total Unordered Data Packets: {str(len(missing_data))}\n")
    if (tracker_type == "Gazepoint"):
        output_file.write(f"Total Invalid Data based on Gazepoint: {str(len(bad_markers))}\n")

    #calculating more summary statistics
    proportion_impossible = len(negative_coords) / final_index
    proportion_missing_packets = len(missing_data) / final_index
    proportion_gazepoint = len(bad_markers) / final_index
    percentage_impossible = proportion_impossible * 100
    percentage_missing_packets = proportion_missing_packets * 100
    percentage_gazepoint = proportion_gazepoint * 100

    #write these additional statistics to the output file
    output_file.write(f"Negative/Zero/Impossible Coordinates: {str(percentage_impossible)}%\n")
    output_file.write(f"Unordered Data Packets: {str(percentage_missing_packets)}%\n")
    if (tracker_type == 'Gazepoint'):
        output_file.write(f"Invalid Data based on Eye Tracker: {str(percentage_gazepoint)}%\n")
    output_file.write(f"Total percentage of lost data packets: {str(percentage_impossible+percentage_missing_packets+percentage_gazepoint)}%\n")

    # Time recorded is in ms, fetch last time recorded in csv file
    total_time_seconds = final_time / 1000
    total_time_minutes = total_time_seconds / 60

    output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(
        total_time_seconds) + ' seconds)' + '\n')

    # combining the lists together for duplicate rows
    combined_list = list(set(negative_coords).union(set(bad_markers)))
    
    if (tracker_type == 'FOVIO'):
        refresh_rate = 16.6667
    elif (tracker_type == 'Gazepoint'):
        refresh_rate = 6.6667
    
    total_error_time_seconds = len(combined_list) / refresh_rate
    total_error_time_seconds = total_error_time_seconds/1000 #convert to seconds
    total_error_time_minutes = total_error_time_seconds / 60
    
    output_file.write('Total Duration Of Invalid Data: ' + str(total_error_time_minutes) + ' minutes (' + str(total_error_time_seconds) + ' seconds)' + '\n')  
    
def CheckErrorsFovio(df, output_file):
    X_coords = []
    Y_coords = []
    valid_point = True #initial condition of boolean. If it fails any of the checks, it flips to FALSE. If it remains true, it is a valid point
    negative_coordinates = []
    missing_packets = []
    
    #identify and report bad data (coordinates that are negative or greater than 2560x1440)
    for i in range(0,df.index.stop):
        #Check if recorded coordinates are within the resolution ranges
        if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1600:
            output_file.write('Row ' + str(i + 2) + ': Negative/Zero/Impossible Coordinates\n')
            negative_coordinates.append(i)
            valid_point = False
        #ignore the first loop to avoid errors
        if i > 0:
            #check for missing data by verifying the continuity of the frames column
            if df['Frame'][i] != df['Frame'][i-1] + 1:
                output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters\n')
                missing_packets.append(i)
                valid_point = False
                
        if valid_point and (i%100==0): #modulo condition to reduce number of points and explore a wider scope (take 1 point every 100 iterations)
            X_coords.append(df['BestPogX'][i])
            Y_coords.append(df['BestPogY'][i])
        valid_point = True #reset boolean variable for next iteration
            
    return negative_coordinates, missing_packets, X_coords, Y_coords

def checkErrorsGazepoint(df, output_file):
    X_coords = []
    Y_coords = []
    valid_point = True #initial condition of boolean. If it fails any of the checks, it flips to FALSE. If it remains true, it is a valid point
    negative_coordinates = []
    missing_packets = []
    marker_bad = []
    
    #identify and report bad data (coordinates that are negative or greater than 2560x1440)
    for i in range(0,df.index.stop):
        if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
            output_file.write('Row ' + str(i + 2) + ': Negative/Zero/Impossible Coordinates (Columns AE and AF)\n')
            negative_coordinates.append(i)
            valid_point = False    
        #ignore the first loop to avoid errors
        if i > 0:
            #check for missing data ... see how the packet counter is
            if df['Counter'][i] != df['Counter'][i-1] + 1:
                output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters (Column E)\n')
                missing_packets.append(i)
                valid_point = False
        #report when gazepoint has a 0 in the BESTPOGVALID column
        if df['BestPogValid'][i] != 1:
            output_file.write('Row ' + str(i + 2) + ': Invalid Data based on Gazepoint (Column AG)\n')
            marker_bad.append(i)
            valid_point = False
            
        if valid_point and (i%100==0): #modulo condition to reduce number of points and explore a wider scope (take 1 point every 100 iterations)
                X_coords.append(df['BestPogX'][i])
                Y_coords.append(df['BestPogY'][i])
        valid_point = True #reset boolean variable for next iteration
        
    return negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords
    
def ScatterPlot(X_coords,Y_coords,file):
    # displaying points on the background ... density inversely related to number
    plt.scatter(X_coords,Y_coords, s=2, c='r')
    plt.title(file)
    plt.show()
        
def DeleteErrors(combined_list, missing_packets,df, missing_info_options):
    if missing_info_options == 1: 
        df.drop(combined_list, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)
    elif missing_info_options == 2: 
        #do the stuff with marking the excel file here'

        defaultvals = ['0'] * len(df.index)

        for each in combined_list:
            defaultvals[each] = 'ERROR'

        for each in missing_packets:
            defaultvals[each] = 'Packet ERROR'

        series = pd.Series(defaultvals)
        df['MissingDataCheck'] = series  
    return df
    
def TimeGap(df, output_file, tracker_type):
    #This function calculates the time gap in seconds
    times=[]
    times = df['Capture Time']
    gap = 0
    
    for i in range(0,len(times)-1): 
        diff = times[i+1]-times[i]
        if diff>gap:
            gap=diff
            
    if (tracker_type == "FOVIO"):
        gap=gap/1000
        
    output_file.write('\nLargest Timegap of missing data: ' + str(gap) +' seconds' + '\n')    

def VelocityCalculation(df, tracker_type):
    # In this function we calculate the velocity of gazepoints with the SG filter approach and append the to the dataframe.We also compute the velocity with the 2-tap (sample-to-sample approach)
    dfwidth=5 #window length for SG filter
    dfdegree=2 #order of the polynomial for SG filter
    dfo=1 #level of derivative for SG filter. 1 because we want to calculate velocity between points as we smooth

    if (tracker_type == "FOVIO"):
        w=2560 #width of screen in pixels
        h=1600 #height of screen in pixels
        screen=32 #diagonal of screen in inches
        D = 29.5 #participants distance from screen in inches
        herz=60 #refresh rate of eye tracker
        period = float(1.0/float(herz)) #period of the eye tracker (i.e. time between samples)
    elif (tracker_type == "Gazepoint"):
        w=2560 #width of screen in pixels
        h=1400 #height of screen in pixels
        screen=24 #diagonal of screen in inches
        D = 25.6 #participants distance from screen in inches
        herz=150 #refresh rate of eye tracker
        period = float(1.0/float(herz)) #period of the eye tracker (i.e. time between samples)
        
    #separate data out by x and y coordinates
    XCoord=df["BestPogX"]
    YCoord=df["BestPogY"]
    
    #filter x and y coordinates with the inputted filter length, polynomial order, and derivative level with SG approach
    FiltXCoord=savgol_filter(XCoord, window_length = dfwidth, polyorder = dfdegree, deriv = dfo)
    FiltYCoord=savgol_filter(YCoord, window_length = dfwidth, polyorder = dfdegree, deriv = dfo)
    
    #collecting information in order to convert derivative to visual angle and calculate velocity (i.e. divide by time elapsed)
    dt = period * float(dfwidth) #change of time between samples to account for the fact multiple were accounted for velocity calculation
    r = math.sqrt(float(w)*float(w) + float(h)*float(h)) #pythagorean theorem to get hypotenuse of screen (i.e. screen diagonal) in units of pixels
    ppi = r/float(screen) #pixels per inch
    
    #convert pixels to degrees of visual angle. store in a array for later mathematical calculations
    degx=[0]*len(FiltXCoord)
    degy=[0]*len(FiltYCoord)
    for point in range(len(FiltXCoord)):
        degx[point]=math.degrees(math.atan2((FiltXCoord[point]/ppi),(2*D)))
        degy[point]=math.degrees(math.atan2((FiltYCoord[point]/ppi),(2*D)))
    degx=np.array(degx)
    degy=np.array(degy)
    
    #calculate velocity for x and y and then combine for a singular velocity value
    velx= degx/dt 
    vely= degy/dt    
    vel=[0]*len(velx)
    for a in range(len(velx)):
        vel[a] = math.sqrt(velx[a]*velx[a] + vely[a]*vely[a])
    df["Velocity (degrees of visual angle/second)"]=vel
    
    ###2 tap (sample-to-sample) velocity calculation approach
    #keeping so (1) less chance of code breaking (2) for comparative reference
    Delta = [] #in pixels
    Angular_Velocity = []
    Delta_mm = []
    Delta_rad = [] 
    inch_to_mm=25.4
    rad_to_degrees = 57.29577951

    for i in range(0,len(df.index)):
        if i==len(df.index)-1: #in this case we reach the end of the dataframe and dont have an i+1
            x1 = df['BestPogX'][i-1]
            y1 = df['BestPogY'][i-1]  
            time_diff =abs(df['Capture Time'][i-1])
            
        else:
            
            x1 = df['BestPogX'][i+1]-df['BestPogX'][i]
            y1 = df['BestPogY'][i+1]-df['BestPogY'][i]
            time_diff=abs(df['Capture Time'][i+1]-df['Capture Time'][i]) 
           
        if (tracker_type == "FOVIO"):
            scale_factor = 1000
            pixel_to_mm=0.269279688
        elif (tracker_type == "Gazepoint"):
            scale_factor = 1
            pixel_to_mm=0.207565625
         
        Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
        Delta_mm.append(Delta[i]*pixel_to_mm)
        Delta_rad.append(math.atan(Delta_mm[i]/(D*inch_to_mm)))
        velocity = (Delta_rad[i]*rad_to_degrees*scale_factor)/(time_diff) #convert to degrees and divide by time difference
        Angular_Velocity.append(velocity)
      
    df['Delta (in pixels)'] = Delta #Create a new column and append the visual angle values in pixels
    df['Delta (in mm)'] = Delta_mm #Create a new column and append the visual angle values in mm
    df['Delta (in rad)'] = Delta_rad #Create a new column and append the visual angle values in rad
    df['2 point velocity (degrees/second)'] = Angular_Velocity #Create a new column and append the angular velocity in degrees per second
    
    return df

def ThresholdEstimation(df):
    mean = 0
    std_dev = 0
    summ = 0
    N = 0
    vel_list = []
    PTold = 250 #Dummy value .Initially, it is the value set by us (in the 100-300 degrees/sec range)
    PTnew = 0
    diff = PTnew - PTold
    velocities = df['Velocity (degrees of visual angle/second)'] #list of angular velocities, probably a column from a Pandas dataframe 
    mean_velocities=sum(velocities)/len(velocities)
    std_dev_velocities = statistics.stdev(velocities,mean_velocities)
    while abs(diff)>1:
        vel_list.clear #clear list at each iteration according to Holmqvist's desription of the algorithm
        summ = 0
        N = 0
        for vel in velocities:
            if vel < PTold:
                summ=summ+vel
                N=N+1
                vel_list.append(vel)   
        if (N!=0):
            mean=summ/N
        std_dev = statistics.stdev(vel_list,mean)
        PTold = PTnew
        PTnew = mean +6*std_dev
        onset_threshold = mean +3*std_dev
        offset_threshold = 0.7*onset_threshold + 0.3*(mean_velocities+3*std_dev_velocities)
        diff = PTnew - PTold
        
    df['Peak Threshold']=PTnew
    df['Onset Threshold']=onset_threshold
    df['Offset Threshold']=offset_threshold
    return df
