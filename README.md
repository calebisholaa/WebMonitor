# Webscrapper

## To get started 
1. pip install requirements.txt
2. Download today's files
	- I have provided a script to do this just run "DownloadAllPrograms.py"
	or 
	- You can use the ziped file of pdfs provided-unzip the file make sure the path to files is /FileDataBase and not FileDataBase/FileDataBase
3. There are two main script "Monitor.py" and "MainJob.py"
	- Monitor.py is the script needed to monitor the difference in the catalogs
	- MainJob runs the Monitor.py on a schduler everyday at 10am
## Notifications
This script works with Power Automate to send a teams card once a change is detected (this may limit the script to only run on a gradapp computer)
## Running on your local machine -IMPORTANT
1. This script contains paths to files and folders this script would fail if it's
  not running on gradApp computer or account

2. So update the following accordingly
	- Line 228 #dynamically get all filenames of  the old files
	  oldfiles(("C:/Users/your_username/Documents/PrintCompare/FileDataBase"))
	  you may change Documents if you choose or move this script to the Documents folder on your computer.
	- Line 272 if this script needs to run on a different computer need you need to update the following
		 with open(rf"C:\Users\gradapp\OneDrive - East Tennessee State University\Catalog Differences\{generate_readable_html_filename(programlink[i])}+.html", 'w', encoding='utf-8') as f:
                    f.write(diffHtml)

		- to a one drive location on your computer 
		- you need to develop power automate workflows to get the notifications.


## How it works

1. We start with a database of what the catalog is yesterday.
	- These are downloaded pdf files
	- Yesterday is saved with suffix "_old.pdf"
2. We download the catalog for toady 
	- These are pdf files 
	- Today is saved with suffix "_new.pdf"
3. Everyday at 10am the script runs
4. There is a log that displays what is going on in terminal for informational and debugging purpose
5. If there is a change there is a html file created ands saves in a OneDrive folder
	- The html hightlight what has been changed, deleted or added in a neat color code
	(Unfortunately this may build up over time so they need to be deleted after the user has checked for the change)
6. After the check for all programs is completed, yesterday gets deleted Today becomes yesterday and tommorow becomes today
7. The job concluds by moving files to the FilesDataBase
