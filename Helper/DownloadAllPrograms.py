import requests
from bs4 import BeautifulSoup
import re
import asyncio
from pyppeteer import launch


programlink = [] 
pdfPrint ="&print"


def file_name_from_url(url):

    # Remove illegal characters and replace them with underscores

    cleaned_name = re.sub(r'[\\/:"*?<>|&]', '_', url)
   

    return cleaned_name

def GetAllCatelogLinks():
    pattern = r'"(.*?)"'
    domain = "https://catalog.etsu.edu/"
    url ="https://catalog.etsu.edu/content.php?catoid=51&navoid=2480"

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
    asyncio.get_event_loop().run_until_complete(generate_pdf(programlink[i], file_name_from_url(programlink[i])+"_old.pdf"))
