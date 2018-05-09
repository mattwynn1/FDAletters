import requests
from bs4 import *
import mechanize
import csv
import unicodedata

#basic setup
year = 2013
url = "https://www.fda.gov/ICECI/EnforcementActions/WarningLetters/" + str(year) + "/default.htm"
response = requests.get(url)

html = response.content
soup = BeautifulSoup(html, "lxml")
table = soup.find('table')
pageno = 1
rooturl = 'https://www.fda.gov'

list_of_rows = []

while year < 2019:
    for row in table.findAll('tr')[1:]:
        #This section is clicking through to the letter itself
        doclink = row.find('a')['href']
        br = mechanize.Browser()
        br.open(rooturl + doclink)
        lettersoup = BeautifulSoup(br.response().read(), "lxml")
        lettertitle = br.title().replace(' ','').replace('/','')
        outfile = open('letters/' + lettertitle + '.html', 'wb')
        outfile.write('<html>')
        outfile.write(lettersoup.find('article').encode('utf-8'))
        outfile.write('</html>')
        outfile.close()
        #Here we're back to processing the data
        #Let's see if the letter was to a doctor
        if "Dear Dr." in str(lettersoup):
            docflag = "Addresses to Dr."
        else:
            docflag = "Not addressed to doctor"
        list_of_cells = []
        for cell in row.findAll('td'):
            text = cell.text.encode('utf-8').strip()
            list_of_cells.append(text)
        try:    
            list_of_cells.append(br.title().encode('utf-8').strip())
        except:
            list_of_cells.append("unicode error")  
        list_of_cells.append(docflag)
        list_of_rows.append(list_of_cells)
        br.close()
    if len(soup.findAll('a', href=True, text="Next")) > 0:
        pageno+=1
        url = "https://www.fda.gov/ICECI/EnforcementActions/WarningLetters/" + str(year) + "/default.htm"
        newurl = url + "?Page=" + str(pageno)
        print("heading to " + newurl)
        response = requests.get(newurl)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        table = soup.find('table')
    else:
        year+=1
        url = "https://www.fda.gov/ICECI/EnforcementActions/WarningLetters/" + str(year) + "/default.htm"
        print ("now going to " + url)
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        table = soup.find('table')
        pageno = 1

#write that shit
outfile = open('fdaresults.txt', 'wb')
writer = csv.writer(outfile)
writer.writerows(list_of_rows)