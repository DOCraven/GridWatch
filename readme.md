# GridWatch 
A tool to analyse generator output in the National Electricity Market (NEM) over a period of time


## Context
This script will download Demand and Dispatch data for the whole NEM and organise it into easily workable `xlsx` along state lines.  
The outputs are discussed below. 

## Dependencies 
This script requires Python 3.8 and the following libraries to be installed 
-  requests
-  shutil 
-  pandas 
-  numpy
-  bs4 (beautifulsoup)

Some systems may also require 
-  openpyxl
-  lxml

## How to Download 
1.  Click on the green `Clone or download` box
     - Please ensure you are downloading the `master` branch for the most up to date code. 
2.  Select `Download ZIP`
3.  Extract Zip to a working directory. 
4.  Continue as per below 


## How To Use
1.  Ensure Python is up to date
2.  Ensure all libraries are installed 
     -  `pip install [library]`
3.  Run `GridWatch - DOWNLOADER.py`
     - `GridWatch - DataMAKER.py` is automatically called. It can also be manually called for any reason. 
4.  Enter dates into the command prompt. 
     - There is mininal date error checking. Please ensure they are correct

### Additional Usage Notes
All DUID information is stored in `\DATA_FILES\DUID_STATE.csv`.   
If you need to change/modify a DUID (ie, LOYYA1 nameplate is halved), just update this file.   
If you need to add a new generator, just append the region, DUID, nameplate and fuel source to the list. 

## Scope
This program will scrape NEMWEB for SCADA dispatch files and demand files. 
The script `Gridwatch - DOWNLOADER.py` will download hourly data for a  specifed time frame. The default is the entire available NEMWEB archive, which is about 395 days. The resolution can be increased to half hourly, if required. 
	
-  DISPATCH DATA is 5 minutely instantaenous SCADA DATA and stored daily in NEMWEB
-  DEMAND DATA is the actual half hourly demand data, and stored weekly in NEMWEB
	
-  PRICE DATA is 5 minute spot price per region (VIC1, NSW1 etc) and stored monthly. It is currently not used for this revision. 
	
	
The script will align datasets to ensure the start and end date for each dataset is the same. This is somewhat wonky, but it should be good enough  

The script will download, extract and place the data in the appropiate sub directory for further working
The script is limited to downloading data from the archive ONLY. 

## Outputs

The script `GridWatch - DataMAKER.py` will organise the data into a state files with demand and each DUID SCADA dispatch in MW. This will be done for future data modelling (Machine Learning, statistical analysis etc and is not currently in this version as of 1.0.1)  
The data is currently presented as the highest and lowest demand for each 24 hour period. The data is split along region ID's (ie, VIC1, NSW1 etc) and presented in the following formats. 
	
	RAW: The highest and lowest dispatch for each 24 hour period for each DUID, in pure MW for each DUID
	
	%: The highest and lowest dispatch, as a percentage of the nameplace capacity, for each DUID
	
	UP: The sum of all DUID for the highest and lowest demand, as a percentage of their nameplates. This gives a "score" of output as a percentage of nameplate, over the number of days analysed. 
	

## Versioning 
SemVer is used for versioning.

## Known Issues
Sometimes the dates do not line up and the `GridWatch - DataMAKER.py` script will return an empty csv. The solution is to change the dates slightly. 
Best method to avoid this is to download approximately 360 days in the middle of the ~395 day availability.  
  
AEMO only store approximately a rolling 395 day window of data on [NEMWEB](https://www.nemweb.com.au/#). Thus, just keep your downloaded data indefinitely.  

