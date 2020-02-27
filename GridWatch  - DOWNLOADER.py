#!/usr/bin/python3
import os
import requests
import re
import shutil
import webbrowser
import numpy as np 
import pandas as pd 
import datetime
import time
import subprocess

from datetime import datetime
from bs4 import BeautifulSoup`
from os import walk
from zipfile import ZipFile
import zipfile 

#### NOTES ####

#############################################
#                                           #
#               VERSION 1.0.0               #
#                                           #   
#                                           #
#############################################
### CHANGE LOG 
#270220: Changed Version Number to 1.0 as per SEMVER (ie, first release)
# ISSUES 
# Need to add in price files

#this changes the file for GIT, 


def innerZipper(zip): 
    """ UNZIPS ONLY HOURLY DATA FROM INSIDE A ZIP"""
    pattern = "(.*)00_(.*)" #only find hourly data
    archive = zipfile.ZipFile(zip) #get names of the zipfile 
    
    cwd = os.getcwd() + '\\' #get cwd, needed to ensure portability 
    DL = cwd + '\\DL'
    
    with zipfile.ZipFile(zip) as z:
        for i, names in enumerate(archive.namelist()): #iterate through 
            result = re.search(pattern, names) #search for pattern
            if result: #pattern found 
                with z.open(names) as zf, open(names, 'wb') as f:
                    shutil.copyfileobj(zf, f) #extracts to CWD, need to move it to DL
                    
                shutil.move(cwd + names, DL) #moves it to the DL folder
            
    
    return #nothing 

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def dateSelector(FILES):
    """Limits downloads to a date range"""
    ### find the first date
    first = FILES[0][-12:-4] #need to slice it to just include the date
    ### find the last date 
    last = FILES[-1][-12:-4] #again need to slice it 
    ### GET USER INPUT
    #need to contain it to ensure error checking, do that later
    selFirst = 'NONE'
    selLast = "NONE"


    print('PLEASE SELECT A DATE BETWEEN %s AND %s\nPRESS ENTER TO DOWNLOAD ALL AVAILABLE DATES\nFORMAT IS YYYYMMDD' %(first, last)) #maybe change later
    while True: 
        selFirst = input("\nSTART DATE: ") #first date
        selFirst = selFirst.upper() #sanitise input 
        #contain user input
        if selFirst == '' or len(selFirst) == 8: 
            break
        else: 
            print("\nPLEASE INPUT A CORRECT DATE OR PRESS ENTER'")
    
    while True: 
        selLast = input("END DATE: ") #last date
        selLast = selLast.upper() #sanitise input
        if selLast == "" or len(selLast) == 8: 
            break
        else: 
            print("\nPLEASE INPUT A CORRECT DATE OR PRESS ENTER")

    #if NULL is entered, make the selected date a wildcard
    if selFirst == '': #every date
        selFirst = "(.*)" #regex wildcard
    if selLast == '': #every date
        selLast = "(.*)" #regex wildcard
    
    ## SET UP PATTERNS
    firstDatePattern = "(.*)_" + selFirst + "(.*)" #used to find the actual first date
    lastDatePattern = "(.*)_" + selLast + "(.*)" #used to find the actual last date
    toDel = [] #array to hold files to delete
    for dates in FILES: #iterate downwards
        result = re.search(firstDatePattern, dates)
        if not result: #ie, not found
            toDel.append(dates) #append name to a new list to delete later
        elif result: #found the date
            #delete the lists 
            FILES = [x for x in FILES if x not in toDel] #remove unwanted files from the list to download
            break
    toDel = [] #array to hold files to delete
    for dates in reversed(FILES): #iterate from the bottom
        result = re.search(lastDatePattern, dates)
        if not result: #ie, not found 
            toDel.append(dates) #append name to a new list to delete later
        elif result: #found
            FILES = [x for x in FILES if x not in toDel] #remove unwanted files from the list to download
            break 

    noteSaver(selFirst, selLast)
    return FILES 

def PathChecker(): 
    """checks to see if output DIRS are created, if not, creates them"""
    cwd = os.getcwd()
    SCADA_PATH = cwd + '\\SCADA FILES'
    if not os.path.exists(SCADA_PATH): #make DL folder if it does not exist
        os.makedirs(SCADA_PATH)

    DEMAND_PATH = cwd + '\\DEMAND FILES'
    if not os.path.exists(DEMAND_PATH): #make DL folder if it does not exist
        os.makedirs(DEMAND_PATH)

    DL_PATH = cwd + '\\DL'
    if not os.path.exists(DL_PATH): #make DL folder if it does not exist
        os.makedirs(DL_PATH)

    PRICE_PATH = cwd + '\\PRICE FILES'
    if not os.path.exists(PRICE_PATH): #make DL folder if it does not exist
        os.makedirs(PRICE_PATH)

    return #nothing
    
def fileScanner(path): 
    """ 
    this will scan all files in the root dir, subfolders, and return a list of file names
    """
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        f.extend(filenames)
        break
    return f

def deleter(folder):
    """
    Emptys the folder specified
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))    

def fileFinder(URL, CALLER): 
    """
    Scrapes and returns a list of FILESs to download at the given URL
    """
    r = requests.get(URL) 
    soup = BeautifulSoup(r.text, 'lxml')
    
    all_hrefs = soup.find_all('a')
    all_links = [link.get('href') for link in all_hrefs]
    zip_files = [dl for dl in all_links if dl and '.zip' in dl]
    if CALLER == 'SCADA': #limit the dates
        amended_zip_files = dateSelector(zip_files)
        # days = len(amended_zip_files) #to create %up time, use it later
        return amended_zip_files
    elif CALLER == "DEMAND" or CALLER == "PRICE": #dont limit the dates here, but limit them in PostFinder
        return zip_files 
    
def downloader(zip_files): 
    """Downloads ZIP files, as found by fileFinder"""

    #get CWD
    cwd = os.getcwd()#get current dir
    download_folder = cwd + "\\DL"
    root = 'http://nemweb.com.au/' #ENTER THE ROOT OF THE WHOLE DIR (ie, just to the TLD)
    
    if not os.path.exists(download_folder): #make DL folder if it does not exist
        os.makedirs(download_folder)

    l = len(zip_files)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) #initial 0 setup

    for i, zip_file in enumerate(zip_files):
        
        # if LIMIT != 0: 
        #     if LIMITER >= LIMIT: #for testing 
        #         stop = True 

        # result = re.search(pattern, zip_file) #look for pattern, use to select Subset of Dates
        # if result: #if found
        full_url = root + zip_file #concat the full url
        r = requests.get(full_url)
        zip_filename = os.path.basename(zip_file)
        dl_path = os.path.join(download_folder, zip_filename)
        with open(dl_path, 'wb') as z_file:
            z_file.write(r.content)
        # LIMITER+=1
        #progress bar stuff
        time.sleep(0.01)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        # if stop: #this is to stop the entire file downloading 
        #     break

    return #nothig

def zipper(DL, SAVE_PATH, CALLER = "SCADA"):  #first level zipper, should only extract to DL folder 
    """ 
    Unzips all zip files into the dir given
    """

    files = fileScanner(DL)
    
    cwd = os.getcwd() + '\\'
    DLL = cwd + 'DL\\'
    l = len(files)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) #initial 0 setup

    for i, zipName in enumerate(files): 
        name = DLL + zipName
        innerZipper(name)
        try:
            os.remove(name)
        except (FileNotFoundError, PermissionError): 
            pass
        time.sleep(0.01)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    zipperArchive(DL, SAVE_PATH, CALLER) #unzip inner zips
    
    return #nothing 

def zipperArchive(DL, SAVE_PATH, CALLER = "SCADA"): #2nd level zipper, extracts to respective SCADA or DEMAND FOLDER 
    """ 
    Unzips all ARCHIVE zip files into the dir given
    """ 
   
    files = fileScanner(DL)
    TT = "00_" #only extract hourly data
    pattern = "(.*)" + TT + "(.*)"
    
    if CALLER == "SCADA":
        print('\nEXTRACTING SCADA ARCHIVE FILES')
        #progress bar
        l = len(files)
        printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) #initial 0 setup

        for i, zips in enumerate(files): #iterate through all DL's zips
            name = DL + "\\" + zips
            result = re.search(pattern, zips) #if a pattern is found (ie, hourly data)
            if result: 
                # Create a ZipFile Object and load sample.zip in it
                with ZipFile(name, 'r') as zipObj:
                    # Extract all the contents of zip file in current directory
                    zipObj.extractall(SAVE_PATH)
            try: 
                os.remove(name) #delete File            
            except (FileNotFoundError, PermissionError): 
                pass
            time.sleep(0.01)
            printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    elif CALLER == "DEMAND":

        print('\nEXTRACTING DEMAND ARCHIVE FILES\nProgress Bar is Wonky')
        #progress bar
        l = len(files)
        printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) #initial 0 setup

        postFinder(DL) #align both datasets ### HERE BE LOGIC ERRORS, CURRENTLY DELETEES THE ENTIRE DEMAND DATASET
        files = fileScanner(DL) #search through new files 

        for i, zips in reversed(list(enumerate(files))): #iterate through all DL's zips
            name = DL + "\\" + zips
            result = re.search(pattern, zips) #if a pattern is found (ie, hourly data)
            
            if result: 
                # Create a ZipFile Object and load sample.zip in it
                with ZipFile(name, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                    zipObj.extractall(SAVE_PATH)
            try: 
                os.remove(name) #delete File  
            except (FileNotFoundError, PermissionError): 
                pass
            time.sleep(0.01)
            printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    elif CALLER == "PRICE":

        print('\nEXTRACTING PRICE ARCHIVE FILES\nProgress Bar is Wonky')
        #progress bar
        l = len(files)
        printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) #initial 0 setup

        postFinder(DL) #align both datasets 
        files = fileScanner(DL) #search through new files 

        for i, zips in reversed(list(enumerate(files))): #iterate through all DL's zips
            name = DL + "\\" + zips
            result = re.search(pattern, zips) #if a pattern is found (ie, hourly data)
            
            if result: 
                # Create a ZipFile Object and load sample.zip in it
                with ZipFile(name, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                    zipObj.extractall(SAVE_PATH)
            try: 
                os.remove(name) #delete File  
            except (FileNotFoundError, PermissionError): 
                pass
            time.sleep(0.01)
            printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return #nothing 

def folderCleaner(PATH):
    """Removes all files in the path given"""

    shutil.rmtree(PATH)
    return #nothing 



def postFinder(DL): 
    """ Aligns DEMAND DATASET to the SCADA DATASET, DELETING ANYTHING THAT IS OUTSIDE OF THAT """
    deleteFiles = [] #empty list to delete stuff I dont need
    demandFiles = fileScanner(DL) #find all existing DEMAND FILES
    ActualSCADA = fileScanner(os.getcwd() + "\\SCADA FILES") #find all SCADA files in DIR
    firstDatePattern = "(.*)_" + str(ActualSCADA[0][-33:-21]) + "(.*)" #used to find the actual first date
    lastDatePattern = "(.*)_" + str(ActualSCADA[-1][-33:-21]) + "(.*)" #used to find the actual last date
    # lastDatePattern = "(.*)_201901300400(.*)" #HERE BE THE ISSUE, AS IF THE SCADA DATA IS LONGER THAN THE DEMAND DATA, IT WILL JUST ITERATE UPWARDS AND DELETE EVERTHING
    for zips in demandFiles:
        firstDate = re.search(firstDatePattern, zips)
        
        #find first date
        if not firstDate: #not found
            deleteFiles.append(zips) #add file to list to delete
        else: 
            break

    if len(demandFiles) > len(ActualSCADA): #if the DEMAND DATASET is larger than the SCADA DATASET
        for zips in reversed(demandFiles): #iterate from the end of the list upwards
            lastDate = re.search(lastDatePattern, zips)
            if not lastDate: 
                deleteFiles.append(zips)
            elif lastDate: 
                break
        
        ## DELETE THOSE FILES WE DONE WANT 
    for item in deleteFiles: 
        name = DL + "\\" + item
        try: 
            os.remove(name)
        except (FileNotFoundError, PermissionError): 
            pass
    
    return #nothing

def noteSaver(firstDate, lastDate): 
    """ Saves a file of the dates input"""
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    txt = 'GRIDWATCH CURRENT AS OF: ' + dt_string + '\nSTART DATE: ' + firstDate + '\nEND DATE: ' + lastDate

    with open("Output.txt", "w") as text_file: 
        text_file.write(txt)
###################################################

def downloadOrganiser(): 
    """
    Downloads SCADA and DEMAND DATA for a specific date range
    """
    #SCADA DATA is daily 
    #DEMAND DATA is weekly
    ### STEP 1 - set up the work env


    PathChecker() #make the appropiate folders 
    #start getting data
    SCADAurl = 'http://nemweb.com.au/Reports/Archive/Dispatch_SCADA/' #SCADA ARCHIVE
    DEMANDurl = 'http://nemweb.com.au/Reports/Archive/Operational_Demand/Actual_HH/' #DEMAND ARCHIVE
    PRICEurl = 'http://nemweb.com.au/Reports/Archive/Public_Prices/'
    download_folder = os.getcwd() + "\\DL" #get ABSOLUTE path of DOWNLOAD FOLDER 
    SCADASave = os.getcwd() + "\\SCADA FILES"
    DEMANDSave = os.getcwd() + "\\DEMAND FILES"
    PRICESave = os.getcwd() + '\\PRICE FILES'

    folderCleaner(download_folder) #ensure DL folder is empty on startup
    folderCleaner(SCADASave)
    folderCleaner(DEMANDSave)
    folderCleaner(PRICESave)

    PathChecker() #make the appropiate folders are there

    ### STEP 1 - Download SCADA FILES  
    print("\nDOWNLOADING SCADA FILES")
    CALLER = 'SCADA'
    downloader(fileFinder(SCADAurl, CALLER))
    

    ### STEP 2 - Extract SCADA FILES
    print("\nEXTRACTING SCADA FILES") 
    zipper(download_folder, SCADASave)


    ### STEP 3 - Clear DL Folder
    # print("\nDELETING SCADA FILES")
    deleter(download_folder)

    ### STEP 4 - Download DEMAND FILES 
    print("\nDOWNLOAD DEMAND FILES")
    CALLER = "DEMAND"
    downloader(fileFinder(DEMANDurl, CALLER))

    ### STEP 5 - Extract DEMAND FILES
    print("\nEXTRACTING DEMAND FILES") 
    Caller = "DEMAND"
    zipper(download_folder, DEMANDSave, Caller)

    ### STEP 6 - Clear DL Folder
    # print("\nDELETING DEMAND FILES")
    deleter(download_folder)

    ### STEP 7 - download PRICE FILES (DISABLED FOR V1.0.0)

    # print("\nDOWNLOADING PRICE FILES")
    # CALLER = 'PRICE'
    # downloader(fileFinder(PRICEurl, CALLER))
    
    # ### STEP 8 - extract price files 
    # print("\nEXTRACTING PRICE FILES") 
    # Caller = "PRICE"
    # zipper(download_folder, PRICESave, Caller)
    
    # ### STEP 9 - clear DL Folder
    # deleter(download_folder)

    return #nothing 


def main():


    ### STEP 1 - download SCADA and DEMAND for a specific date range
    start = datetime.now()
    current_time = start.strftime("%H:%M:%S")
    print("START TIME: ", current_time)
    
    downloadOrganiser()

    print('\n\nCALLING DATAMAKER SCRIPT')
    subprocess.call("GridWatch - DataMAKER.py", shell=True)

    finish = datetime.now()
    run = finish - start

    print("\nRUN TIME: ", run)


    #### STEP 2 - EXTRACT FILES ACCORDINGLY 

    #SCADA = SCADAExtractor()

    #Demand = DemandExtractor()

    ###



main()


print("CODE COMPLETED")
finished = str(input("PRESS ENTER TO CLOSE WINDOW"))