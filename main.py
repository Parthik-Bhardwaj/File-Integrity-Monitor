#!/usr/local/bin/python3

import os
import hashlib
import time
from datetime import datetime

# Scan for files will start from same place. By default, it'll be the same place where script is placed
ROOT_DIRECTORY = "."

# File to store file names along with their hashes
BASELINE_RESULTS = "baseline.txt"

# Logs file for alert logs
ALERT_FILE = "alert.log"

# Files to ignore as they'll keep on changing
IGNORE_LIST = [BASELINE_RESULTS, ALERT_FILE, "main.py", '.DS_Store']

# Seconds to wait after each scan
SLEEP_TIME = 5

baseline_map = {}

def generateHash(filePath):
    try:
        with open(filePath, 'r') as f:
            data = f.read()
            digest = hashlib.sha3_512(data.encode())
            return digest.hexdigest()
    except:
        # If an error occured while opening the file, the file won't be assigned any hash. "ERROR!" will be placed in place of hash 
        print("Error: Unable to open file: "+ filePath)
        return "ERROR!"        
    

def createBaseline():

    # Delete baseline results that exists
    os.remove(BASELINE_RESULTS)

    directory_map = {}
    for (dir_path, dir_names, file_names) in os.walk(ROOT_DIRECTORY):
        directory_map[dir_path] = file_names

    for dir in directory_map.keys():

        # Skip if a folder is empty
        if len(directory_map[dir]) == 0:
            continue
        
        for file in directory_map[dir]:
            # ignore files in IGNORE_LIST
            if file in IGNORE_LIST:
                continue
            
            fullFilePath = dir + "/" + file
            fileHash = generateHash(fullFilePath)
            baseline_map[fullFilePath] = [fileHash, False]
            with open(BASELINE_RESULTS, 'a') as f:
                f.write(fullFilePath + '\t' + fileHash + '\n')
  


def runMonitor():
    
    directory_map = {}
    for (dir_path, dir_names, file_names) in os.walk(ROOT_DIRECTORY):
        directory_map[dir_path] = file_names

    for dir in directory_map.keys():
        
        # Skip if a folder is empty
        if len(directory_map[dir]) == 0:
            continue
        
        for file in directory_map[dir]:
            # ignore files in IGNORE_LIST
            if file in IGNORE_LIST:
                continue
            
            fullFilePath = dir + "/" + file
            if fullFilePath in baseline_map.keys():
                if generateHash(fullFilePath) == baseline_map[fullFilePath][0]:
                    baseline_map[fullFilePath][1] = True
                else:
                    timestamp = datetime.fromtimestamp(datetime.now().timestamp())
                    msg = f"[{timestamp}]:\t{fullFilePath} has been modified.\n"  
                    print(msg)
                    with open(ALERT_FILE, 'a') as f:
                        f.write(msg) 

                    baseline_map[fullFilePath][1] = True

            else:
                timestamp = datetime.fromtimestamp(datetime.now().timestamp())
                msg = f"[{timestamp}]:\t{fullFilePath} has been created.\n"  
                print(msg)
                with open(ALERT_FILE, 'a') as f:
                    f.write(msg) 

    for file in baseline_map.keys():
        if baseline_map[file][1]:
            baseline_map[file][1] = False
        else: # The logic checks for any file part of baseline but not currently present. This means the file is deleted   
            timestamp = datetime.fromtimestamp(datetime.now().timestamp())
            msg = f"[{timestamp}]:\t{file} has been deleted.\n"  
            print(msg)
            with open(ALERT_FILE, 'a') as f:
                f.write(msg) 

                           




if __name__ == '__main__':

    print("Welcome to File Integrity Monitor!\n")
    print("Choose an option from below:")
    print("1. Create a new baseline and run File Integrity monitor\n2. Run File Integrity Monitor with previous baseline")
    choice = int(input("Choice: "))

    if choice == 1:
        createBaseline()
        while(True):
            runMonitor()
            time.sleep(SLEEP_TIME)

    
    elif choice == 2:
        with open(BASELINE_RESULTS, 'r') as f:
            line = f.readline()
            line = line.split("\t")
            if len(line) == 2:
                baseline_map[line[0].strip()] = line[1].strip()    
            else:
                if not line[0] == "\n":    
                    print("The baseline file is either empty or corrupted. Running new baseline scan.")
                    createBaseline()

        if len(baseline_map.keys()) == 0:
            print("Baseline file not found. Creating new baseline.")
            createBaseline()

        while(True):
            runMonitor()
            time.sleep(SLEEP_TIME)

