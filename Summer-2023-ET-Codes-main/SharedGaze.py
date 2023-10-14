from math import sqrt
import pandas as pd
import os

dirPath1 = "Participant 1 results"
dirPath2 = "Participant 2 results"
numSimulations = 34
dataFileName = "output2.csv"
errorMargin = 10

def fixFileNamings(dirPath, participantNum):
    for file in os.listdir(dirPath):
        i = 0
        while (i<len(file) and not file[i].isdigit()):
            i += 1
        simNumber = ''
        while (i<len(file) and file[i].isdigit() and len(simNumber)<2):
            simNumber += file[i]
            i += 1
        
        try:
            if (file[-1].lower() == 't' or file[-1].lower() == 'd'):
                simType = file[-1].lower()
                os.rename(f"{dirPath}/{file}", f"{dirPath}/p{simNumber}p{str(participantNum)} {simType}")
            else:
                os.rename(f"{dirPath}/{file}", f"{dirPath}/p{simNumber}p{str(participantNum)}")
        except Exception as e:
            print(f"File {file} could not be renamed : {e}")

def getDistance(x1, x2 , y1, y2):
    return sqrt((x2 - x2)**2 + (y2 - y1)**2)

def getStats(durationDf, sharedGazeCount, totalCount, totalDuration, fileName):
    newRow = {}
    newRow['File Name'] = fileName
    newRow['Shared Gaze Count'] = sharedGazeCount
    newRow['Total Count'] = totalCount
    newRow['Shared Gaze Count %'] = (sharedGazeCount / totalCount) * 100
    newRow['Total Shared Gaze Duration'] = durationDf.sum()
    newRow['Total Duration'] = totalDuration
    newRow['Shared Gaze Duration %'] = (newRow['Total Shared Gaze Duration'] / newRow['Total Duration']) * 100
    newRow['Shared Gaze Duration Mean'] = durationDf.mean()
    newRow['Shared Gaze Duration St. Dev.'] = durationDf.std()
    return newRow

def findSharedGaze(dirPath1, dirPath2, numSimulations, dataFileName, errorMargin):
    outputDf = pd.DataFrame(columns = ['File Name', 'Shared Gaze Count', 'Total Count', 'Shared Gaze Count %', 'Total Shared Gaze Duration', 'Total Duration', 'Shared Gaze Duration %', 'Shared Gaze Duration Mean', 'Shared Gaze Duration St. Dev.'])
    for i in range(1, numSimulations+1):
        for simType in ['', ' t', ' d']:
            fileName1 = f"p{str(i)}p1{simType}"
            filePath1 = f"{dirPath1}/{fileName1}/{dataFileName}"
            if (not os.path.exists(filePath1)):
                print(f"File \"{filePath1}\" does not exist")
                continue
            
            fileName2 = f"p{str(i)}p2{simType}"
            filePath2 = f"{dirPath2}/{fileName2}/{dataFileName}"
            if (not os.path.exists(filePath2)):
                print(f"File \"{filePath2}\" does not exist")
                continue
            
            df1 = pd.read_csv(filePath1)
            df2 = pd.read_csv(filePath2)
            
            durationList = []
            totalDuration = 0
            sharedGazeCount = 0
            for index in range(min(df1.shape[0], df2.shape[0])):
                dist = getDistance(float(df1['X'][index]), float(df1['Y'][index]), float(df2['X'][index]), float(df2['Y'][index]))
                totalDuration += float(df1['Duration (ms)'][index])
                if (dist <= errorMargin):
                    durationList.append(float(df1['Duration (ms)'][index]))
                    sharedGazeCount += 1
            newRow = getStats(pd.DataFrame(durationList), sharedGazeCount, df1.shape[0], totalDuration, f"p{str(i)}{simType}")
            outputDf = pd.concat([outputDf, pd.DataFrame(newRow, index=[0])], ignore_index=True)
    outputDf.to_csv("Shared Gaze.csv", index=False)
        
findSharedGaze(dirPath1, dirPath2, numSimulations, dataFileName, errorMargin)
                