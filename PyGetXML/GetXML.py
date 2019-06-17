import requests
import re
from bs4 import BeautifulSoup

url ='https://us-aus-cuic1:8444/cuicui/permalink/?viewId=65B8C92C10000165005C5FD87D5BEAE0&linkType=xmlType&viewType=Grid'
myXML = requests.get(url, verify=False)
soup = BeautifulSoup(myXML.text, "lxml")

for row_tag in soup.report.children:
    print('No.'+row_tag['index'])
    for col_tag in row_tag.children:
            print(col_tag['index']+' '+col_tag['name'],end=' ')
            if (len(col_tag.contents) != 0):
                print(col_tag.contents[0])
            else:
                print('NULL')