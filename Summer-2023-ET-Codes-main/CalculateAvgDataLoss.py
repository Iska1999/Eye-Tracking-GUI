import os

def calculate_avg_data_loss(dir_name, output_file):
    count = 0
    totalDataLoss = 0
    file = open(output_file, "w")
    file.write(f"Data Loss For Directory: {dir_name}\n")
    file.write("--------------------------------\n")
    for folder in os.listdir(dir_name):
        try:
            error_file = open(f"{dir_name}/{folder}/ErrorLog_Statistics.txt", 'r')
            lines = error_file.readlines()
            totalDataLoss += float(lines[7][39:-2])
            file.write(f"{folder}: {lines[7][39:-2]}%\n")
            count += 1
            error_file.close()
        except:
            print(f"Error in {folder}")
    avg_data_loss = totalDataLoss/count
    file.write("\n--------------------------------\n")
    file.write(f"Average Data Loss: {avg_data_loss}%\n")
    file.close()

dir_name = "Participant 2"
output_file = f"DataLoss_{dir_name}.txt"
calculate_avg_data_loss(dir_name, output_file)
    
        