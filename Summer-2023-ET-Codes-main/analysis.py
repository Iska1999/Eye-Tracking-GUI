import pandas as pd
import os

dirPath = "Participant 1 results"
dataFileName = "output2.csv"
participantNum = 1
numSimulations = 34

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

def getFileStatistics(df, fileName):
    fixationDurations = df[df["Event Type"] == "Fixation"]["Duration (ms)"]
    newRow = {}
    newRow['File Name'] = fileName
    newRow['Fixation Count'] = df[df["Event Type"] == "Fixation"].shape[0]
    newRow['Total Count'] = df.shape[0]
    newRow['Fixation Count %'] = (newRow['Fixation Count'] / newRow['Total Count']) * 100
    newRow['Total Fixation Duration'] = fixationDurations.sum()
    newRow['Total Duration'] = df["Duration (ms)"].sum()
    newRow['Fixation Duration %'] = (newRow['Total Fixation Duration'] / newRow['Total Duration']) * 100
    newRow['Fixation Duration Mean'] = fixationDurations.mean()
    newRow['Fixation Duration St. Dev.'] = fixationDurations.std()
    return newRow
    
def getCombinedStats(rows, fixationDurationsCombined, fileName):
    newRow = {}
    newRow['File Name'] = fileName
    newRow['Fixation Count'] = sum([row['Fixation Count'] for row in rows])
    newRow['Total Count'] = sum([row['Total Count'] for row in rows])
    newRow['Fixation Count %'] = (newRow['Fixation Count'] / newRow['Total Count']) * 100
    newRow['Total Fixation Duration'] = sum([row['Total Fixation Duration'] for row in rows])
    newRow['Total Duration'] = sum([row['Total Duration'] for row in rows])
    newRow['Fixation Duration %'] = (newRow['Total Fixation Duration'] / newRow['Total Duration']) * 100
    newRow['Fixation Duration Mean'] = (sum([row['Fixation Duration Mean'] * row['Total Count'] for row in rows])) / (newRow['Total Count'])
    newRow['Fixation Duration St. Dev.'] = fixationDurationsCombined.std()
    return newRow

def getSimulationStatistics(dirPath, participantNum, numSimulations, dataFileName):
    outputDf = pd.DataFrame(columns=['File Name', 'Fixation Count', 'Total Count', 'Fixation Count %', 'Total Fixation Duration', 'Total Duration', 'Fixation Duration %', 'Fixation Duration Mean', 'Fixation Duration St. Dev.'])
    for i in range(1, numSimulations+1):
        rows = []
        fixationDurationsCombined = pd.DataFrame()
        for simType in ['', ' t', ' d']:
            fileName = f"p{str(i)}p{str(participantNum)}{simType}"
            filePath = f"{dirPath}/{fileName}/{dataFileName}"
            
            if (not os.path.exists(filePath)):
                print(f"File \"{filePath}\" does not exist")
                continue
            
            if (os.path.exists(filePath)):
                df = pd.read_csv(filePath)
                newRow = getFileStatistics(df, fileName)
                fixationDurations = df[df["Event Type"] == "Fixation"]["Duration (ms)"]
                outputDf = pd.concat([outputDf, pd.DataFrame(newRow, index=[0])], ignore_index=True)
                rows.append(newRow)
                fixationDurationsCombined = pd.concat([fixationDurationsCombined, fixationDurations], ignore_index = True)
            else:
                print(f"File {fileName} does not exist")
        
        if (len(rows) > 0):
            combinedStatsRow = getCombinedStats(rows, fixationDurationsCombined, f"p{i}p{str(participantNum)} combined")
            outputDf = pd.concat([outputDf, pd.DataFrame(combinedStatsRow, index=[0])], ignore_index=True)
            
    outputDf.to_csv("ED Stats.csv", index=False)
       
fixFileNamings(dirPath, participantNum)         
getSimulationStatistics(dirPath, participantNum, numSimulations, dataFileName)