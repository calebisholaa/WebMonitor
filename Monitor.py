import requests
from bs4 import BeautifulSoup
import re
import asyncio
from pyppeteer import launch
import fitz  # PyMuPDF library
from difflib import HtmlDiff
import time
import os 
from reportlab.pdfgen import canvas
import logging
import warnings
warnings.filterwarnings('ignore')
from colorama import Fore, Style, init
import shutil

# Record the start time
start_time = time.time()
log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
log.info("Running Website Monitor")


programlink = [] 
pdfPrint ="&print"

base_filename =""
old_pdf = []
new_pdf = []
oldfiles_list  = []


#helper function to convert pdf to text
def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    doc.close()
    return text

#helper function; returns the changes/ difference in the text
def changes(pdf1_path, pdf2_path):
    text1 = pdf_to_text(pdf1_path)
    text2 = pdf_to_text(pdf2_path)

    # Perform text comparison 
    # Here, we use the difflib library for a basic comparison.
    from difflib import unified_diff

    diff = unified_diff(text1.splitlines(), text2.splitlines(), lineterm='')
    changes = '\n'.join(diff)

    return changes

#fuction compares the pdf  using the pdf_to_text helper function
def compare_pdfs(pdf1_path, pdf2_path):
    text1 = pdf_to_text(pdf1_path)
    text2 = pdf_to_text(pdf2_path)

    return text1, text2


def write_to_pdf(file_path, text):
    # Create a PDF document
    pdf_canvas = canvas.Canvas(file_path)

    # Set font and size
    pdf_canvas.setFont("Helvetica", 12)

    # Add text to the PDF
    pdf_canvas.drawString(100, 750, text)

    # Save the PDF
    pdf_canvas.save()

#this function generates the html file with viuals showing the difference
def generate_diff_html(pdf1_path, pdf2_path):
    text1, text2 = compare_pdfs(pdf1_path, pdf2_path)

    # Generate HTML diff
    d = HtmlDiff()
    diff_html = d.make_file(text1.splitlines(), text2.splitlines())

    return diff_html

def clean_filenames(text):
    # Remove illegal characters and replace them with underscores

    cleaned_name = re.sub(r'[\\/:"*?<>|&]', ' ', text)
   

    return cleaned_name
#get get file names from the url
def file_name_from_url(url):

    # Remove illegal characters and replace them with underscores

    cleaned_name = re.sub(r'[\\/:"*?<>|&]', '_', url)
   

    return cleaned_name

#deletes a file name take the file path as an argument
def delete_file_by_path(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except OSError as e:
        print(f"Error deleting {file_path}: {e}")

def delete_old_pdfs(directory):
    # List all files in the specified directory
    files = os.listdir(directory)

    # Iterate through the files
    for file_name in files:
        # Check if the file is a PDF and ends with "_old"
        if file_name.lower().endswith(".pdf") and file_name.lower().endswith("_old.pdf"):
            # Construct the full file path
            file_path = os.path.join(directory, file_name)

            # Delete the file
            os.remove(file_path)
            print(f"Deleted: {file_path}")

def oldfiles(directory):
    # List all files in the specified directory
    files = os.listdir(directory)

    # Iterate through the files
    for file_name in files:
        # Check if the file is a PDF and ends with "_old"
        if file_name.lower().endswith(".pdf") and file_name.lower().endswith("_old.pdf"):
            # Construct the full file path
            oldfiles_list.append(file_name)
           
    return oldfiles_list

#renames a file
def rename_file(old_filename, new_filename):
    try:
        os.rename(old_filename, new_filename)
    except OSError as e:
        print(f"Error renaming {old_filename}: {e}")

#Generate file names from the heading on the page
def generate_readable_html_filename(print_page_link):
    page = requests.get(print_page_link)
    soup  = BeautifulSoup(page.content, 'html.parser')
    info  = soup.find('h1')
   
    page_title = info.text
    file_name = clean_filenames(page_title)
    return file_name

def move_files(source_folder, destination_folder):
     # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    # Get a list of files in the source folder
    files = os.listdir(source_folder)
     #Move files with the specified suffix to the destination folder
    for file in files:
        if file.lower().endswith(".pdf") and file.lower().endswith("_old.pdf"):
            source_path = os.path.join(source_folder, file)
            destination_path = os.path.join(destination_folder, file)

            # Move the file
            shutil.move(source_path, destination_path)
            print(f"Moved: {file} to {destination_folder}")

#VERY IMPORTANT FUNCTION 
#This is where we dynamically get all the links to each catelog
def GetAllCatelogLinks():
    pattern = r'"(.*?)"'
    domain = "https://catalog.etsu.edu/"
    url ="https://catalog.etsu.edu/content.php?catoid=51&navoid=2480"   #<--- This is the landing page of the catalog page

    index = 0
    webpage = requests.get(url)

    soup = BeautifulSoup(webpage.content, 'html.parser')

    page = soup.find('table', {'class': 'toplevel table_default'})
        #main = page.find('tr', {'role': 'main'})
        #blockContent = main.find('td', {'class': 'block_n2_and_content'})
    links = page.find_all('a')
    for item in links:
        if('preview_program' in item.get('href', [])):
            strLink = str(item)
            links = re.findall(pattern, strLink)
            for i in range(len(links)):
                newlink = domain + links[i]
                newlink = newlink.replace("amp;", "")
                printLink = newlink + pdfPrint
                programlink.append(printLink)
                #  print(programlink)

    return programlink




async def generate_pdf(link, downloaded_pdf_path):
    browser = await launch()
    page = await browser.newPage()
    
    await page.goto(link)
    
    await page.pdf({'path': downloaded_pdf_path, 'format': 'A4'})
    
    await browser.close()


         
for i  in range(len(GetAllCatelogLinks())):
    # Run the function
    new_pdf.append(file_name_from_url(programlink[i])+"_new.pdf")  #dynamically generating filenames for new fle 
    #this fuction generates a new pdf file 
    asyncio.get_event_loop().run_until_complete(generate_pdf(programlink[i], file_name_from_url(programlink[i])+"_new.pdf"))
    time.sleep(1)



#dynamically get all filenames of  the old files.
old_pdf = oldfiles(("C:/Users/gradapp/Documents/PrintCompare/FileDataBase"))  #<-- This needs to change to your local path (path containg the pdfs)

#for every new link/Pdf check to see if there is a corresponding old link/pdf if not create empty one and add to 
#a list of pdfs
for i in range(len((new_pdf))):
    # Extract the base filename without the suffix
    base_filename = os.path.splitext(new_pdf[i])[0]

    # Construct the corresponding old PDF filename
    old_pdf_filename = base_filename.replace("_new", "_old") + ".pdf"

    # Check if the old PDF exists, if not, create it
    if old_pdf_filename not in old_pdf:
        # Create the old PDF 
        log.info(Fore.RED + f"Creating old PDF: {old_pdf_filename}" + Style.RESET_ALL)
        text = pdf_to_text(new_pdf[i])
        write_to_pdf(old_pdf_filename,"The link of the page changed")
        #add that new file to a list of old pdfs
        old_pdf.append(old_pdf_filename)

#sort them to reduce chances of mis match
old_pdf.sort()
new_pdf.sort()


for i in range(len((new_pdf))):

    # Extract the base filename without the suffix
    base_filename = os.path.splitext(new_pdf[i])[0]
    
    # Construct the corresponding old PDF filename
    old_pdf_filename = base_filename.replace("_new", "_old") + ".pdf"

    old_pdf_filenameCopy = old_pdf_filename

    if new_pdf[i].replace("_new","") == old_pdf_filenameCopy.replace("_old",""):  
    #check if there is a difference in both pdf files
        change_in_pdf = changes(new_pdf[i], old_pdf_filename)
        if change_in_pdf:
            diffHtml = generate_diff_html(new_pdf[i], old_pdf_filename)
            # Save the HTML to a file or display it as needed              
            #with open(rf"C:\Users\gradapp\OneDrive - East Tennessee State University\Catalog Differences_1\{file_name_from_url(programlink[i])}+.html", 'w', encoding='utf-8') as f:
                    # f.write(diffHtml)
            log.info(Fore.RED + f"Change detected on {generate_readable_html_filename(programlink[i])}" + Style.RESET_ALL)
            with open(rf"C:\Users\gradapp\OneDrive - East Tennessee State University\Catalog Differences\{generate_readable_html_filename(programlink[i])}+.html", 'w', encoding='utf-8') as f:
                    f.write(diffHtml)
            log.info(Fore.BLUE + f"Change saved to OneDrive.... initiating push notifications"+ Style.RESET_ALL)
        else:
            log.info(f"No change detected on {generate_readable_html_filename(programlink[i])}")



try:
    log.info("Start Deleting old files...")
    for i in range(len(old_pdf)):
        #delete all old file
        delete_file_by_path(file_name_from_url(programlink[i])+"_old.pdf")
except:
    log.info("Out of bounds occured, deleting remaining files")
    #this makes sure to delete lingering old files
    delete_old_pdfs("C:/Users/gradapp/Documents/PrintCompare")   #<-n change file path as need 


log.info("New files becoming old")
#New becomes old a
for i in range(len(new_pdf)):
    #rename new file as old file
    rename_file(file_name_from_url(programlink[i])+"_new.pdf",file_name_from_url(programlink[i])+"_old.pdf")


sourceFolder ="C:/Users/gradapp/Documents/PrintCompare"
destinationFolder = "C:/Users/gradapp/Documents/PrintCompare/FileDataBase"
log.info(Fore.YELLOW +"Cleaning up... moving files to database" + Style.RESET_ALL)
move_files(sourceFolder,destinationFolder)

log.info("Job completed")
# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

elapsed_time_min = elapsed_time/60

# Print the elapsed time
print(f"Elapsed time: {elapsed_time} seconds")
print(f"Elapsed time: {elapsed_time_min} seconds")