NEMWEB DATA SCRAPER
V1.0.2
RELEASE CANDIDATE
README LAST UPDATED 21022020
#############################################################
				HOW TO USE 
#############################################################

1: Run "GridWatch - DOWNLOADER.py" by double clicking the file. 
2: Select which dates you want to scrape data for in YYYYMMDD format. 
	There is no valid date checking apart from have you entered 8 characters. It is up to you to determine the correct date (ie, 20190229 would not work in a non leap year)
3: The script will download and sort the data automatically, and finish. 

		Additional usage notes
		
4: All DUID information is stored in 'DATA FILES\DUID_STATE.csv'. 	
	If you need to change/modify a DUID (ie, LOYYA1 nameplate is halved) here is where you modify it. 
	If you need to add a new generator, just append the region, DUID, nameplate and fuel source to the list. 

#############################################################


#############################################################
						NOTES 
#############################################################

###################### 
DEPENDENCIES
######################
 
	This script requires PYTHON 3.8 and the following libraries in stalled. 
	
	requests
	shutil
	pandas 
	numpy 
	bs4 (beautifulsoup)
	
	you may also require 
	openpyxl
	
	
	OPEN COMMAND LINE > 'pip install [library] > ENTER
		FOR EXAMPLE: 'pip install pandas' to install pandas
	


This program will scrape NEMWEB for SCADA dispatch files and demand files. 
The script "downloader.py" will download hourly data for a a specifed time frame. The default is the entire available NEMWEB archive, which is about 395 days. 
	
	DISPATCH DATA is 5 minutely instantaenous SCADA DATA and stored daily in NEMWEB
	DEMAND DATA 
	
	DEMAND DATA is the actual half hourly demand data, and stored weekly in NEMWEB
	
	PRICE DATA is 5 minute spot price per region (VIC1, NSW1 etc) and stored monthly. It is currently not used for this revision. 
	
	
The script will align datasets to ensure the start and end date for each dataset is the same. 

The script will download, extract and place the data in the appropiate subdir for further working
	The script is limited to downloading data from the archive ONLY. 
	
###################### 
OUTPUTS 
######################
	
The script "GridWatch - DataMAKER.py" will organise the data into a state files with demand and each DUID SCADA dispatch in MW. This will be done for future data modelling (Machine Learning, statistical analysis etc)
The data is currently presented as the highest and lowest demand for each 24 hour period. The data is split along region ID's (ie, VIC1, NSW1 etc) and presented in the following formats. 
	
	RAW: The highest and lowest dispatch for each 24 hour period for each DUID, in pure MW for each DUID
	
	%: The highest and lowest dispatch, as a percentage of the nameplace capacity, for each DUID
	
	UP: The sum of all DUID for the highest and lowest demand, as a percentage of their nameplates. This gives a "score" of output as a percentage of nameplate, over the number of days analysed. 
	

###################### 
FILE FORMAT
######################

The file structure is pretty important. 
It needs to be the following. There is some error checking involved to ensure the integrity 




gridwatch
	>DATA_FILES - holds reference data - 
	>DEMAND FILES - holds demand data
	>DL - This is used to temporarily store the downloaded .ZIPS. At the conclusion of each extraction, this folder is emptied. 
	>OUTPUTS - Resultant data file for each state is available with sub directories. 
	>pandas - for dealing with dataframes
	>PRICE FILES - NOT USED IN THIS VERSION
	>SCADA FILES - holds dispatch data
	

###################### 
DATA FILES 
######################

	
The folder "DATA_FILES" holds reference data. If additional DUIDS come online, add them to the end of the csv file  "DUID_STATE.csv" 
If existing DUIDS change (for example, an increasie in nameplate capacity) the respective entry can be modified to reflect that. 
