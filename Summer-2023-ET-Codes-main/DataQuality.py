import pandas as pd
import math
from datetime import datetime, timedelta
#Sam Smith
#04/09/2020

"""
Overall, I'd say this file is somewhat difficult to understand because there are many things
going on at once. The gist is that we are looking through a participant's performance file and 
finding when they clicked on the different tasks (target detection, reroute, chat message, fuel leak)
and checking to see that at the time of clicking those tasks, was the user actually looking where 
they clicked. This is basically a sanity check to ensure that the preprocessed data we are using to analyze is 
accurate. The goal of this file is to identify what is accurate and what isn't so we know what data
to rely on and analyze in the future. 
"""
#Column numbers in the eye tracking and performance files so accessing data is easier.
"""Pandas does allow us to access a data column directly with its name as well,
but sometimes I used these numbers to access specific cells."""
UAVNumber = 7
TaskType = 6
SysTimeP = 4
SysTimeET = 47
leftx = 24
lefty = 25


"""
These coordinates are based on the layout of the screen that the participants 
are looking at during the test. 
"""
#Coordinate fields for each UAV in the 2560 x 1440 resolution
#       x1    x2   y1   y2
UAV1 = [930, 1326, 194, 0]
UAV2 = [1326, 1738, 194, 0]
UAV3 = [1738, 2150, 194, 0]
UAV4 = [2150, 2560, 194, 0]
UAV5= [930, 1326, 194, 400]
UAV6 = [1326, 1738, 194, 400]
UAV7 = [1738, 2150, 194, 400]
UAV8 = [2150, 2560, 194, 400]
UAV9 = [930, 1326, 400, 606]
UAV10 = [1326, 1738, 400, 606]
UAV11 = [1738, 2150, 400, 606]
UAV12 = [2150, 2560, 400, 606]
UAV13 = [930, 1326, 606, 812]
UAV14 = [1326, 1738, 606, 812]
UAV15 = [1738, 2150, 606, 812]
UAV16 = [2150, 2560, 606, 812]

#This is the list of all of our UAVs
UAVs = [UAV1, UAV2, UAV3, UAV4, UAV5, UAV6, UAV7, 
        UAV8, UAV9, UAV10, UAV11, UAV12, UAV13, 
        UAV14, UAV15, UAV16]


#Global variables to help with later calculations 
system_time = ""
count = 0
coordinates = []

#Given pandas dataframe and first time, returns the index of the first time in the dataframe
def find_mission_start(first_perf_time,df):
    if (len(first_perf_time)==7):
        fulldate = datetime(100, 1, 1, 1, int(first_perf_time[0:2]), int(first_perf_time[3:5]), int(first_perf_time[6]) * 100000)
    elif (len(first_perf_time) == 11):
        fulldate = datetime(100, 1, 1, int(first_perf_time[0:2]), int(first_perf_time[3:5]), int(first_perf_time[6:8]), int(first_perf_time[9:11])*10000)
    time = fulldate.time()
    count = 0
    for each in (df["NST"]): 
        #Finding the first time within 10 ms
        if subSecs(time, 10000) <= each <= addSecs(time, 10000):
            return count
        count+=1
    
    #if we didn't find the start of the mission 
    return -1



"""
This function allows us to add time, because this is strangely difficult 
with the provided datetime functions.
The same goes for the subSecs function. 
"""

#tm is datetime.time object
#msecs is numer of milliseconds to add to the time.
def addSecs(tm, msecs):
    #arbitrary date, its the time that matters.
    #For some reason python doesnt allow you to deal strictly with times
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate + timedelta(microseconds=msecs)
    return fulldate.time()

def subSecs(tm, msecs):
    #arbitrary date, its the time that matters.
    #For some reason python doesnt allow you to deal strictly with times
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate - timedelta(microseconds=msecs)
    return fulldate.time()




"""
This function uses the time column in the eyetracking data to create a MissionTime 
column that matches up with the mission time in the performance csv.

This allows us to more easily pinpoint where the participant was looking throughout the mission. We are using 
MissionTime as opposed to system time because mission time is more accurate and controllable.
MissionTime is a column we created whereas SystemTime is created by the eyetracking gazepoint 
software I believe. 
"""

#Only setting the mission time for start index + 900 to avoid unnecessary computation
#df is pandas dataframe
#start index and end indiciate start and end of for loop


#Creates a new column in the dataframe called "MissionTime" which makes the mission start time 0 and preserves the time difference between each row
def setMissionTime(df, start_index, end):
# It sets a new column in the DataFrame called "MissionTime" and initializes all values to 0.
# It then iterates over a range of indices from start_index to start_index + end.
# For each index i, it calculates the time difference between the current row's "Time" value and the previous row's "Time" value.
# It updates the "MissionTime" value for the current row by adding the calculated time difference to the previous row's "MissionTime" value.
    df["MissionTime"] = 0
    for i in range(start_index, start_index + end):
        if i > start_index: 
            x = (df.loc[i, "Time"]) - (df.loc[i-1, "Time"])#accesses the value of the "Time" column at index i
            df.loc[i, "MissionTime"] = float(df.loc[i-1, "MissionTime"]) + x
    return df

def create_ST_lst(df):#create system time list
    '''
This function takes a DataFrame df as a parameter.
It extracts the value of "SystemTime" from the second row of the DataFrame (index 1) and assigns it to the variable base.
The function then checks the length of base to determine the format of the time.
If base has a length of 7, it assumes the time is in the format "hh:mm:ss" and creates a datetime object with the year, month, day, hour, minute, and second set to fixed values and the hour, minute, and second extracted from base.
If base has a length of 11, it assumes the time is in the format "dd hh:mm:ss:ms" and creates a datetime object with the year, month, day, hour, minute, second, and microsecond set to fixed values and the hour, minute, second, and millisecond extracted from base.
The function then extracts the time component from the datetime object and assigns it to the variable time.
It creates a list arr containing the time value and returns it.
'''
    base = (df.loc[1, "SystemTime"])
    if (len(base) == 7):
        fulldate = datetime(100, 1, 1, 1, int(base[0:2]), int(base[3:5]), 0)
    elif (len(base) == 11):
        fulldate = datetime(100, 1, 1, int(base[0:2]), int(base[3:5]), int(base[6:8]), int(base[9:11])*10000)

    time = fulldate.time()
    arr = [time]
    # ser = pd.Series(arr)
    return arr


#This works but it's innacurate; might have to use Time column for more 
#accuracy 
"""
TODO: add df as an argument so you can set system time within function, 
figure out how to make this more accurate (Maybe using time column?)
"""

def deltas(df):
    #Inside the loop, it calculates the delta between the current time value (tm[i]) and the previous time value (tm[i-1]).
        dlst = []
        tm = df["Time"].tolist()
        for i in range(len(tm)):
            delta = float((tm[i]) - (tm[i-1])) * 1000000
            dlst.append(delta)
            
        return dlst

def set_NST(arr, df, delta_lst):#set normalised system time?

# This function takes three parameters: arr, df, and delta_lst.
# Inside the loop, it calls the addSecs function with arr[i-1] (the previous element of arr) and delta_lst[i] (the delta at index i) as arguments.
# The result of addSecs is assigned to the variable x.
# It appends x to the arr list.

    for i in range(1, df.index.stop):
        
        x = addSecs(arr[i-1], delta_lst[i]) 
        arr.append(x)


"""
df["NST"]: This creates a new column named "NST" in the DataFrame df. The column doesn't exist previously.
pd.Series(arr): This converts the arr list into a Pandas Series. A Pandas Series is a one-dimensional labeled array that can be assigned to a DataFrame column.
"""

def add_NST_to_df(arr, df):

    df["NST"] = pd.Series(arr)


"""
Given x and y coordinates, this function determines which UAV the corrdinates would
fall into. Future edit may be to combine this function with the secondary task function. 
"""
def which_uav(x, y):
    counter=0
    for uav in UAVs:
        xacc= (x >= uav[0] and x <= uav[1])
        yacc = (y >= uav[2] and y <= uav[3])
        if xacc and yacc:
            return counter+1
        counter+=1
    return "Inconclusive"

#Determines if participant is looking at one of the secondary tasks
def which_secondary_task(x, y, tasks):
    counter=0
    for task in tasks:
        xacc= (x >= tasks[task][0] and x <= tasks[task][1])
        yacc = (y >= tasks[task][2] and y <= tasks[task][3])
        if xacc and yacc:
            return task
        counter+=1
    return "Inconclusive"

#Helper function that essentially uses the distance formula to find distance between two points
def calculateDistance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist  

#This works!

def find_end(start, df):
    counter = 0
    for each in df["NST"]:
        if(each.minute - df["NST"][start].minute == 15):
            return counter
        counter +=1



def preProcess(df):
        # Default width is 2560 and default height is 1440 for Gazepoint
        column_names_X = []
        column_names_Y = []
        column_names_bool = []
        column_names_Pupil_Diameter = []
       
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
        column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']

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
            
def dq(df, inputP, xError, yError):
            #REMOVING BLANK LINE FROM GAZEPOINT
            df = df[1:df.index.stop]
            df.reset_index(drop=True, inplace=True)
            
            #if there is a blank line in performance, you can repeat the above two lines
            #with performance in place of df
            performance = pd.read_csv(inputP)

           
            
            arr = create_ST_lst(df) #creates a list of system times
            ds = deltas(df) #creates a list of deltas
            set_NST(arr, df, ds) #adds ds[i] to arr[i-1] and appends it to arr
            add_NST_to_df(arr, df) #adds arr to df as a column named NST
            #Does performance start with blank line as well? 
            start = find_mission_start(performance["SystemTime"][0], df)
            end = find_end(start, df)
            setMissionTime(df, start, end)
            
       
            """
            Create dictionary of the mission times (from the button clicks), assign 
            coordinates as values to the mission times key 
            """
            missionDict = {}
            #Tells us if target detection was accurate
            df["DataAccurate"] = ""
            #Tells which uav the target appeared in
            df["Task"] = ""
            #Tells us which uav the participant was looking at
            df["Qualitative"] = "N/A"

            """
            Uses distance formula to calculate how far eye coordinates are 
            from the center of a video feed or secondary task.
            """
            df["DistanceFromCenter"] = 0



            """
            When there is a target present, this loop looks at the mission time, finds a matching time in the 
            eye tracking file's mission time file (or a time that is very close to the same) and checks that the 
            participants eyes are looking in the correct area. This logic is repeated for the secondary tasks below. 
            """
            number_true = 0
            number_false = 0
            number_analyzed=0
            count=0
            for each in performance["TDTargetPresent"]:
                if each == 1.0:
                    raw_counter=0
                    clickTime = performance.iloc[count, 27]
                    for mt in df["MissionTime"]: #The difference between mt and clickTime is the time error
                        #Finding where button click time and MissionTime align
                        if -.01 <= mt -  clickTime <= .01 :
                            #print(raw.at[raw_counter, "BestPogY"])
                            number_analyzed+=1
                            uavNum = int(performance.at[count, "UAVNumber"])
                            uav = UAVs[uavNum-1]
                            x = df.at[raw_counter, "BestPogX"]
                            y = df.at[raw_counter, "BestPogY"]

                            #Now accuracy takes the errors into account 
                            xacc= (x >= uav[0] - xError and x <= uav[1] + xError)
                            yacc = (y >= uav[2] - yError and y <= uav[3] + yError)
                            """
                            Value will be True if both x and y coordinates are accurate 
                            according to the current UAV and False if not. 
                            """

                            """
                            Below if statement ensures that only a time that is close
                            to clickTime will be used for the dictionary so we can pinpoint 
                            accuracy at exact clicktime.
                            """
                            if xacc and yacc:
                                number_true +=1
                            else:
                                number_false+=1
                            if -.01 < mt -  clickTime < .01:
                                missionDict[clickTime] = xacc and yacc
                            
                            cur_uav = which_uav(x, y)

                            #Calculating how far away the coordinates are from either 
                            #the upper or lower bound of the uav feed

                            centerx = (uav[0] + uav[1])/2
                            centery = (uav[2] + uav[3])/2


                            #Updating the output csv file
                            df.at[raw_counter, "DataAccurate"] = xacc and yacc
                            df.at[raw_counter, "Task"] = "Target detection task for UAV " + str(uavNum)
                            df.at[raw_counter, "Qualitative"] = "Participant was looking at UAV " + str(cur_uav)
                            df.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

                        raw_counter+=1
                count+=1

            # print(missionDict)

            """
            Here, we repeat the logic used for target detection but in the context of 
            the secondary tasks. 
            """
            RRPanel = [0, 920, 930, 1440]
            FLPanel = [920, 2560, 812 ,1158]
            CMPanel = [920, 2560, 1158 ,1440]
            task_dict = {"RRTimeofRR" :RRPanel, "FLStopTime":FLPanel, "MessageTime":CMPanel}
            for task in task_dict:
                perf_counter=0
                for each in performance[task]:
                   
                    if not pd.isnull(each):
                        if task == "MessageTime":
                            if (performance.at[perf_counter,"MessageFrom"] != 'user'):
                                perf_counter+=1
                                continue
                            
                            
                        raw_counter=0
                        for mt in df["MissionTime"]:
                            if (-.01 <= mt- each <= .01):
                                number_analyzed+=1
                                x = df.at[raw_counter, "BestPogX"]
                                y = df.at[raw_counter, "BestPogY"]
                                xacc= (x >= task_dict[task][0] - xError and x <= task_dict[task][1] + xError)
                                yacc = (y >= task_dict[task][2] - yError and y <= task_dict[task][3] + yError)

                                centerx = (task_dict[task][0] + task_dict[task][1])/2
                                centery = (task_dict[task][2] + task_dict[task][3])/2
                                df.at[raw_counter, "Task"] = "Secondary detection task for "+ task
                                df.at[raw_counter, "DataAccurate"] = xacc and yacc
                                df.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)
                                
                                if xacc and yacc:
                                    number_true+=1
                                    df.at[raw_counter, "Qualitative"] = "Participant was correctly looking at the " + task
                                else: 
                                    cur_uav = which_uav(x, y)
                                    number_false+=1
                                    if cur_uav == "Inconclusive":
                                        cur_task = which_secondary_task(x, y, task_dict)
                                        if cur_task=="Inconclusive":
                                            df.at[raw_counter, "Qualitative"] = "Unable to pinpoint participant's gaze location."
                                        else:
                                            df.at[raw_counter, "Qualitative"] = "Participant was looking at "+ cur_task
                                    else:
                                        df.at[raw_counter, "Qualitative"] = "Participant was looking at "+ str(cur_uav)
                            raw_counter+=1
                    perf_counter+=1
           
            # raw.to_csv(output, index=False)
            #Creating summary statistics file (STILL IN PROGRESS)
            # percent_accurate = number_true/number_analyzed
            # summary_stats = open("quality_summary.txt", 'w')
            # summary_stats.write("The data was "+ str(100 * percent_accurate) + " percent accurate.\n")
            # summary_stats.write("Of the "+ str(number_analyzed)+  " data points analyzed, " + str(number_true)+" data points were accurate while " + str(number_false) + " were inaccurate." )
            # summary_stats.close()
            #returning from mission time start to the 900th point after that
            """
            Important to note that this function no longer puts the dataframe 
            into an output file. It just returns a dataframe. 
            """
            """
            TODO: Change the return df to return 900 seconds after starting point
            """
            return df[start:end]