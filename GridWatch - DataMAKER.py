import csv
import os
import pandas as pd 
import datetime
import numpy as np 
import time
import subprocess
from os import walk
from dateutil.parser import parse
from datetime import datetime
from datetime import date


#############################################
#                                           #
#               VERSION 1.0.0               #
#                                           #   
#                                           #
#############################################
### CHANGE LOG 
#270220: Changed Version Number to 1.0 as per SEMVER (ie, first release) 




######## NOTES ##########
#please note, ALL TIMES MUST MATCH FOR CODE TO WORK
# THERE IS NO ERROR CATCHING TO ENSURE THE TIMES ARE CORRECT. IT IS UP TO THE END USER TO ENSURE THE CORRECT FILES ARE DOWNLOADED AND TIMES AND DATES MATCH 

# DATE FORMATE IS DD/MM/YYYY hh:mm:ss

### TO FIX ####


# INSERT DEMAND INTO FINAL_%

# INSERT TOTAL DAYS INTO EACH OUTPUT DF


# SWAP UPTIME AND TYPE IN FINAL_UP

# RAW saves as PERCENTAGE





# http://nemweb.com.au/Reports/Current/Dispatch_SCADA/


# DEMAND IS PER STATE AND AVAILABLE HERE. DEMAND FILES NEED TO BE ACTUAL HALF HOURLY
# http://nemweb.com.au/Reports/Current/Operational_Demand/Actual_HH/

# PRICING DATA IS NOT YET INSTALLED 
# IT WILL BE ADDED AT A LATER 

#########################################################################################
# PLEASE NOTE THIS FILE WILL EXTRACT CURRENT DATA DOWNLOADED VIA downloader.py.         #
#########################################################################################

#############################################
#                                           #
#               VERSION 1.5.1               #
#             RELEASE CANDIDATE             #   
#                                           #
#############################################
# ISSUES 
# Piya requests output header and first row is swapped 
# ie, 
# 
#           TOTAL DAYS: x
#               TIME 1  |   TIME 2   |   TIME 3   |


def fileScanner(path): 

    """ 
    this will scan all files in the root dir, subfolders, and return a list of file names
    """
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        f.extend(filenames)
        break
    return f

def stateInserter(df_STATE, df_SCADA):
    """
    Goes through the supplied STATE SCADA DATA, and appends the STATE of the DUID to the list.

    Please update the file in \\DATA_FILES\\DUID_STATE.csv if necessary. 
    
    """
    ## VARS ##
    
    #### STEP 1 read and organise data, insert state column in data, remove last line (includes "C	END OF REPORT	343")
    
    idx = 0 #location where to insert nameplate
    df_SCADA.insert(idx, column = "TYPE", value = '') #creates new (empty),  used later for fuel type
    df_SCADA.insert(idx, column = "NAMEPLATE (MW)", value = '')  #creates new (empty) column with the nameplate capacity at the 2nd row
    df_SCADA["STATE"] = "" #creates new column at the end, with nothing in each row
    

    for row in df_STATE.itertuples(): #iterate through the STATE CSV FILES to find the data 
        STATE = row[1] #find STATE DATA
        DUID = row[2] #FIND DUID DATA
        NAMEPLATE = row[3] #FIND NAMEPLATE CAP
        TYPE = row[4] #FIND FUEL SOURCE
      
        
        try: 
            df_SCADA.loc[DUID, "STATE"] = STATE #insert STATE
            df_SCADA.loc[DUID, "NAMEPLATE (MW)"] = NAMEPLATE #insert MAX capacity
            df_SCADA.loc[DUID, "TYPE"] = TYPE #insert FUEL TYPE
            
        except IndexError: 
            pass
    
    return df_SCADA

def rowInserter(STATE): 
    """
    inserts 2 rows (DEMAND, SPOT PRICE) into the Df
    """
    indexs = ["DEMAND (MW)", "SPOT PRICE ($)"] #create new empty index
    new_rows = pd.DataFrame(columns = None, index = indexs) #create new empty df with index from above
    STATE = pd.concat([new_rows, STATE], axis=1, sort = False) #concat that with the df given to the fcn

    return STATE

def timeFixer(orig_time):
    """
    Changes the date format to a consistent format, irrespective of the input format
    """
    time = parse(orig_time) #recognises the format, 
    df = time.strftime('%d/%m/%Y %H:%M:%S' ) #changes it to the correct (specified) one

    return df

def demandInserter(VIC, QLD, NSW, SA, TAS, cwd):   
    """
    This will insert the hourly demand into the various state files. 
    """

    ### VARS

    path = cwd + "\\DEMAND FILES" #get path of demand files location 
    
    files = fileScanner(path) #find all files (add in CSV error handling?)
    demand_df = {'VIC1': [],'NSW1': [],'QLD1': [],'SA1': [],'TAS1': []} #create data for dataframe, populate this dataframe, then slice and insert it into the respective STATE DF
    df = pd.DataFrame(demand_df) #dataframe for time and demand
    dfDT = df.T #transpose it to make "VICT etc" the index (ROWS)
    


    for names in files: #iterate through
        csvName = path + "\\" + names #name path
        workingDEMAND_FILE = pd.read_csv(csvName, header = 1, index_col = 4) #index col = 6 means making REGIONID the index 
        
        time = timeFixer(workingDEMAND_FILE.loc["VIC1"]["INTERVAL_DATETIME"]) #find time, to insert as column heading in all dfs. ONLY RIP FROM VIC as they will all be the same. 
        
        dfDT[time] = "" #insert empty row
       
        ### MAKE NICER, this is just for testing 
        ## FIND THE DEMAND and TIME for each state, when given a folder to demand times 
        ### MUST MATCH THE SAME TIMES FOR THE SCADA GENERATION 
        #victoria
        
        VICdemand = workingDEMAND_FILE.loc["VIC1"]["OPERATIONAL_DEMAND.1"] #find demand for the state
        #append data to row
        VIC.at["DEMAND (MW)", time] = VICdemand #should insert value into state file
        
        #NSW
        NSWdemand = workingDEMAND_FILE.loc["NSW1"]["OPERATIONAL_DEMAND.1"] #find demand for the state
        NSW.at["DEMAND (MW)", time] = NSWdemand #should insert value into state file
        
        #QLD
        QLDdemand = workingDEMAND_FILE.loc["QLD1"]["OPERATIONAL_DEMAND.1"] #find demand for the state
        QLD.at["DEMAND (MW)", time] = QLDdemand #should insert value into state file
        
        #TAS
        TASdemand = workingDEMAND_FILE.loc["TAS1"]["OPERATIONAL_DEMAND.1"] #find demand for the state
        TAS.at["DEMAND (MW)", time] = TASdemand #should insert value into state file
        
        #SA
        SAdemand = workingDEMAND_FILE.loc["SA1"]["OPERATIONAL_DEMAND.1"] #find demand for the state
        SA.at["DEMAND (MW)", time] = SAdemand #should insert value into state file

    return #nothing

def peaker(df): 
    """ returns the MAX and MIN of a 24 hour period for the entire DF"""
    
    
    NumColumns = len(df.columns) #total number of columns, used to iterate through number of days
    NumColumns = NumColumns - 3  # total number of days, -3 to trim to size. 3 was gained through trial and error
    NumDays = NumColumns / 24 #work out how many days to extract the data from 
 
    finalcsv = df.iloc[:, 0:2] #copy index to new csv
    tempcsv = df.iloc[:, 0:2] #copy index to new csv

    first = 2 #start point for slicing the year into days
    last = 26 #end point for slicing years into days

    for days in range(0, int(NumDays)): #iterate through each 24 hour period 
        csv24 = df.iloc[:, first:last] #slice df into 24 hour period
                
        sliceddf = csv24.loc["DEMAND (MW)"] #slice 24 hour period into DEMAND ONLY
        try: 
            max24 = sliceddf.idxmax() #find MAX DEMAND of sliced DAY, return column name 
            min24 = sliceddf.idxmin() #find MIN DEMAND of sliced day, return column name
        except TypeError: 
            pass

        try: 
            tempcsv = csv24.loc[:, [min24, max24]] #access max and min via loc, throw it in a new [holding] csv
            finalcsv = finalcsv.join(tempcsv) #JOIN to output CSV
            tempcsv = df.iloc[:, 0:2] #clear tempcsv (ugly, I know, but #yolo)
        except (KeyError, ValueError): 
            pass
       
        
        # reindex posts, start again
        first = last #start of next day, 
        last = last + 24 #end of next day

    
    return finalcsv

def divider(df):
    """Converts the actual output to a % of nameplate capacity"""
    topRows = df.iloc[0:1, :] #top row, ie demand
    
    df.drop(df.index[[0,1]], inplace = True) #DROP TOP ROWS TO AVOID DIVIDING IT ETC
    cols = df.columns[df.columns.str.contains('(.*):00')] #find the columns I actually want 
    df[cols] = df[cols].div(df.iloc[:,0], axis=0) #divide by the nameplate cap
    dff = topRows.append(df) #slap the demand onto the top of the divided df
    
    return dff

def sumSorter(df):
    """ Sums each row of a df, returns only the sum"""

    ### NO DEMAND, NO NAMEPLATE (NOT NEEDED), INCLUDES FUEL SOURCE

    dfR = df.iloc[:, 2:] #SLICE DF INTO RESPONSE
    nameplate = df.loc[:, 'NAMEPLATE (MW)'] #just get the nameplace capacity, store it as an object
    
    df_f = df.iloc[:, 1:2] #create final output DF with format of input DF
    df_f["UPTIME"] = dfR.sum(axis=1) #insert uptime percentage into sum of DF
    #insert the nameplate
    df_f.insert(0, 'NAMEPLATE (MW)', nameplate) #insert the nameplate capacity into the column called "NAMEPLATE (MW)" at index = 0 (ie, the beginning)
    df_f.sort_values('UPTIME',ascending = False ,  inplace = True) #sort the values highest to lowest

    return df_f

def PathChecker(): 
    """checks to see if output DIRS are created, if not, creates them"""
    cwd = os.getcwd()
    UP_PATH = cwd + '\\OUTPUTS'
    if not os.path.exists(UP_PATH): #make DL folder if it does not exist
        os.makedirs(UP_PATH)

    return #nothing
    
def highLOW(df):
    """returns a split of the DF every HI and LOW 
    ie, every 2nd orow"""
    # ODD = HIGHS
    # EVEN = LOWS

    #copy the index and first 2 rows to output files
    d = df.loc['DEMAND (MW)', :] #save top demand thingo as series 
    e = d.to_frame() #convert to a df
    demand = e.T #transpose to make series into a df and usable later 
    demand.drop(['NAMEPLATE (MW)', 'TYPE'], axis = 1, inplace = True) #drop useless columns 
    
    df.drop('DEMAND (MW)', inplace = True) #drops demand row
    df_high = df.iloc[:, 0:2] #OUTPUT HIGH with index]
    df_low = df_high #EMPTY DF ready for OUTPUT LOW with INDEX
    #delete the first two rows of original 
    df.drop(columns = ['NAMEPLATE (MW)', 'TYPE'], inplace = True) #reorganise df to assist with ODD/EVEN 
    #GET EVENS (ie, high demand)
    lows = df.loc[:,::2] #EVEN OUTPUTS
    #GET LOWS (ie, low demand)
    df.insert(0, column = "NAN", value = '') #insert dummy column to shift everything to the right 1, thereby making EVEN into ODDS
    highs = df.loc[:,::2] # ODD NUMBERS
    highs.drop('NAN', axis = 1, inplace = True) #drop dummy column to make it all nice again
    
    # SLAP high and lows into output DF that has index etc
    dfH = pd.concat([df_high, highs], axis = 1)
    dfL = pd.concat([df_low,lows], axis = 1)
    
    ### GET COLUMN NAMES ###
    highList = list(dfH.columns)
    lowList = list(dfL.columns)

    # create two new DF with the appropiate demand 
    demandH = demand.drop(lowList[2:], axis = 1) #only contains the timestamp for high demand (no SCADA OUTPUT)
    demandL = demand.drop(highList[2:], axis = 1)  #only contains the timestamp for low demand (no SCADA OUTPUT)
    #reinsert the namplate and type column to make inserting it later easier. Each column is empty  
    demandH.insert(0, 'TYPE', '')
    demandH.insert(0, 'NAMEPLATE (MW)', '')
    demandL.insert(0, 'TYPE', '')
    demandL.insert(0, 'NAMEPLATE (MW)', '')
    

    #join both dfs
    
    high_out = pd.concat([demandH,dfH], axis = 0)
    low_out = pd.concat([demandL,dfL], axis = 0)
    ### NO DEMAND, INCLUDES NAMEPLATE AND FUEL TYPE
    return (high_out, low_out)

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

def percentagiser(df, days): 
    """returns a DF with a % uptime"""

    df1 = df #create copy of the data frame, to join together at the end
    fuel = df.loc[:, 'TYPE'] #get the fuel type to insert later
    nameplate = df.loc[:, 'NAMEPLATE (MW)'] #get nameplate cap to insert later
    
    df.drop(['NAMEPLATE (MW)', 'TYPE'], axis = 1, inplace = True)#remove everything that isnt necessary, resulting in a 1xN df for mathematical purposes
    df2 = df.apply(lambda x : (x / days) * 100) #apply division of total number of days
    
    df1['PERCENTAGE UPTIME']= df2['UPTIME'] #insert uptime into copy df 
    df1.insert(0, 'TYPE', fuel) #insert the fuel source into the column called "TYPE" at index = 0 (ie, the start)
    df1.insert(0, 'NAMEPLATE (MW)', nameplate) #insert the fuel source into the column called "TYPE" at index = 0 (ie, the start)

    return df1

def demand_setup(df): #dont think it is used
    """ RETURNS ONLY THE DEMAND FOR EACH STATE"""
    demand = df.iloc[:1, :]
    return demand

def dayInserter(df, days):
    """Inserts total days worked on into the DF"""
    
    df.iat[0, 0] = 'TOTAL DAYS: ' + str(days) #insert total days
    

    return df 


def sheetWriter(dfH, dfL, dfPerc, dfRAW, name): 
    """Sanitize and write a number of DF's to an .XLSX, as a new sheet"""
    #sanitize HIGH and LOW OUTPUTS
    dfH.iat[0, 3] = pd.to_numeric('') #clear unnecessary summed demand from the df
    dfL.iat[0, 3] = pd.to_numeric('') #clear unnecessary summed demand from the df
    dfH.iat[0, 2] = pd.to_numeric('') #clear unnecessary summed demand from the df
    dfL.iat[0, 2] = pd.to_numeric('') #clear unnecessary summed demand from the df

    #sanitize RAW output 
    dfRAW.drop('SPOT PRICE ($)', axis = 0, inplace = True) #removes spotprice

    with pd.ExcelWriter(name) as writer: #disregard error, as it works without it
        try:
            dfH.to_excel(writer, sheet_name='HIGH') #write high uptime to sheet 
            dfL.to_excel(writer, sheet_name='LOW') #write low uptime to sheet
            dfPerc.to_excel(writer, sheet_name='%') #write combined HIGH & LOW percentage to sheet
            dfRAW.to_excel(writer, sheet_name='RAW') #write raw (DUID OUTPUT in MW) to sheet
        except PermissionError: #if file is open, shouldnt as we use timestamps to ensure unigque files
            pass 

    return #nothing 

#################

def gridWatch(): ## MAIN


    #### SET UP WORK ENC
    cwd = os.getcwd() #get current path
    now = datetime.now()
    timeStamp = str(now.strftime("%Y-%m-%d_%H-%M_"))
    SCADA_State = pd.read_csv(cwd + "\\DATA_FILES\\DUID_STATE.csv") 
    PathChecker() #check outputs dirs
    
    SCADA_df = pd.DataFrame(index=SCADA_State["DUID"]) #move DUID to row index
    
    ##### STEP 1 read data files

    path = cwd + "\\SCADA FILES" #SCADA FILES LIVE HERE
    
    
    files = fileScanner(path) #find all files

    ### STEP 2 insert state value, and append data
    
    print('SETTING UP THE DATA ENVIRONMENT')
    
    l = len(files)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50) #initial 0 setup
    for i, Names in enumerate(files): #iterate through
        csvName = path + "\\" + Names #read full name, including append path to filename
        #read SCADA CSV into memory, header = 1 fixes the dataframe not lining up with the header, throw in a try catch for only opening CSV 
        workingSCADA_FILE = pd.read_csv(csvName, sep=r'\s*,\s*', header = 1, index_col = 5, engine='python') 
        try: 
            SCADA_df = pd.concat([SCADA_df, workingSCADA_FILE["SCADAVALUE"]], axis=1, sort = True) #append each new SCADA file
        except ValueError: 
            pass
        ## EXTRACT TIME STAMP AND INSERT INTO CLUMNS 
        SCADA_TIME_RAW = workingSCADA_FILE.iloc[5][4] #from an arbiatary column, hardcoded as they all have the same numbers. CURRENTLY IS YYYY/MM/DD HH:MM:SS and has unnecessary double commas ("")
        SCADA_TIME_SAN = SCADA_TIME_RAW.replace('"', '') #sanitize the commas, however still outputs as YYYY:MM:DD HH:MM:SS
        SCADA_TIME = timeFixer(SCADA_TIME_SAN) #format the date properly 
        SCADA_df= SCADA_df.rename(columns={"SCADAVALUE": SCADA_TIME}) #insert timestamp into SCADA MW VALUE
        time.sleep(0.01)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    print('\nINSERTING STATE DATA')    
    SCADA_df = stateInserter(SCADA_State, SCADA_df) #append STATE DATA
    
    ### STEP 3 split df into state lines and do some stuff to make the data nice

    print("\nSTATE SORTING")
    Sorted = SCADA_df.groupby("STATE") #group data accoridng to STATE
    #split data into each state, and also return each states columns (nameplate, fuel)
    VIC = Sorted.get_group("VIC1")
    NSW = Sorted.get_group("NSW1")
    QLD = Sorted.get_group("QLD1")
    TAS = Sorted.get_group("TAS1")
    SA = Sorted.get_group("SA1")

    ### INSERT DEMAND AND SPOT PRICE COLUMN INTO EACH STATE
    print("\nINSERTING DEMAND DATA INTO EACH STATE")
    
    TVIC = rowInserter(VIC)
    TNSW = rowInserter(NSW)
    TQLD = rowInserter(QLD)
    TTAS = rowInserter(TAS)
    TSA = rowInserter(SA)
    
    ### STEP 4 insert hourly demand into respective states, making sure to align it with hourly SCADA
    print("\nINSERTING HOURLY DEMAND INTO EACH STATE")
    demandInserter(TVIC, TQLD, TNSW, TSA, TTAS, cwd)

    ### STEP 5 - find highest and lowest demand for each 24hour, get rid of every other hour 
    print("\nFINDING HIGHEST AND LOWEST DEMAND FOR EACH STATE\nThis Takes a while, please be patient")
    
    VIC24 = peaker(TVIC)
    VIC24_FINAL = VIC24.copy() #final copy, as original copy is modified and used for later operations 
    NSW24 = peaker(TNSW)
    NSW24_FINAL = NSW24.copy()
    QLD24 = peaker(TQLD)
    QLD24_FINAL = QLD24.copy()
    TAS24 = peaker(TTAS)
    TAS24_FINAL = TAS24.copy()
    SA24 = peaker(TSA)
    SA24_FINAL = SA24.copy()
    
    ### STEP 7 Return % of NAMEPLATE CAP  - deletes the demand data
    print("\nCONVERTING MW TO % OF NAMEPLACE CAPACITY")

    VIC_per = divider(VIC24) 
    VIC_per_FINAL = VIC_per.copy() #final copy, as original copy is modified and used for later operations 
    NSW_per = divider(NSW24)
    NSW_per_FINAL = NSW_per.copy()
    QLD_per = divider(QLD24)
    QLD_per_FINAL = QLD_per.copy()
    TAS_per = divider(TAS24)
    TAS_per_FINAL = TAS_per.copy()
    SA_per = divider(SA24)
    SA_per_FINAL = SA_per.copy()
    
    ### STEP 8 - split each high and low into a new DF
    print("\nSPLITTING EACH STATE INTO HIGH AND LOW DEMAND")
    VIC_H, VIC_L = highLOW(VIC_per)
    NSW_H, NSW_L = highLOW(NSW_per)
    QLD_H, QLD_L = highLOW(QLD_per)
    TAS_H, TAS_L = highLOW(TAS_per)
    SA_H, SA_L = highLOW(SA_per)

    ### STEP 8 SORT HIGHEST TO LOWEST
        #HIGHEST
    print("\nCREATING OUTPUT METRIC (highest to lowest %)")
    #UPTIME HIGH
    VIC_UPTIME_h = sumSorter(VIC_H)
    NSW_UPTIME_h = sumSorter(NSW_H)
    QLD_UPTIME_h = sumSorter(QLD_H)
    TAS_UPTIME_h = sumSorter(TAS_H)
    SA_UPTIME_h = sumSorter(SA_H)

    #UPTIME LOW
    VIC_UPTIME_l = sumSorter(VIC_L)
    NSW_UPTIME_l = sumSorter(NSW_L)
    QLD_UPTIME_l = sumSorter(QLD_L)
    TAS_UPTIME_l = sumSorter(TAS_L)
    SA_UPTIME_l = sumSorter(SA_L)

    ### STEP 9 - convert to % vs days
    print('CONVERTING UPTIME TO PERCENTAGE')
    days = (len(VIC_per.columns)-1)/2 #find the total number of days - 
    
    VIC_UPTIME_H = percentagiser(VIC_UPTIME_h, days)
    VIC_UPTIME_L = percentagiser(VIC_UPTIME_l, days)

    NSW_UPTIME_H = percentagiser(NSW_UPTIME_h, days)
    NSW_UPTIME_L = percentagiser(NSW_UPTIME_l, days)

    QLD_UPTIME_H = percentagiser(QLD_UPTIME_h, days)
    QLD_UPTIME_L = percentagiser(QLD_UPTIME_l, days)

    TAS_UPTIME_H = percentagiser(TAS_UPTIME_h, days)
    TAS_UPTIME_L = percentagiser(TAS_UPTIME_l, days)

    SA_UPTIME_H = percentagiser(SA_UPTIME_h, days)
    SA_UPTIME_L = percentagiser(SA_UPTIME_l, days)

    ### STEP 10 - SAVE OUTPUTS AS SHEETS IN XLSX FILE

    print("\nSAVING VARIOUS OUTPUT FILES")
    #dayInserter inserts total number of days into the respective df
    sheetWriter(dayInserter(VIC_UPTIME_H, days), dayInserter(VIC_UPTIME_L, days), dayInserter(VIC_per_FINAL, days), dayInserter(VIC24_FINAL, days), "OUTPUTS\\" + timeStamp + "VIC_FINAL.xlsx")



        #COMBINED - commented out by default
    sheetWriter(dayInserter(NSW_UPTIME_H, days), dayInserter(NSW_UPTIME_L, days), dayInserter(NSW_per_FINAL, days), dayInserter(NSW24_FINAL, days), "OUTPUTS\\" + timeStamp + "NSW_FINAL.xlsx")
    sheetWriter(dayInserter(QLD_UPTIME_H, days), dayInserter(QLD_UPTIME_L, days), dayInserter(QLD_per_FINAL, days), dayInserter(QLD24_FINAL, days), "OUTPUTS\\" + timeStamp + "QLD_FINAL.xlsx")
    sheetWriter(dayInserter(TAS_UPTIME_H, days), dayInserter(TAS_UPTIME_L, days), dayInserter(TAS_per_FINAL, days), dayInserter(TAS24_FINAL, days), "OUTPUTS\\" + timeStamp + "TAS_FINAL.xlsx")
    sheetWriter(dayInserter(SA_UPTIME_H, days), dayInserter(SA_UPTIME_L, days), dayInserter(SA_per_FINAL, days), dayInserter(SA24_FINAL, days), "OUTPUTS\\" + timeStamp + "SA_FINAL.xlsx")

    print("\n\nEND OF CODE")



    return #nothing 

### MAIN 

gridWatch()

