import requests
import re
from bs4 import BeautifulSoup
import time

url ='https://us-aus-cuic1:8444/cuicui/permalink/?viewId=65B8C92C10000165005C5FD87D5BEAE0&linkType=xmlType&viewType=Grid'

import time,os

def getXML(inc = 60):

  while True:
    myXML = requests.get(url, verify=False)
    ticks=str(int(time.time()))
    soup = BeautifulSoup(myXML.text, "lxml")

    with open('C:/Users/eriwang/OneDrive - National Instruments/电话Dashboard项目/XMLData/'+ticks+'.txt', 'w') as f:
        for row_tag in soup.report.children:
            f.write('No.'+row_tag['index']+'\n')
            for col_tag in row_tag.children:
                f.write(col_tag['index']+' '+col_tag['name']+' ')
                if (len(col_tag.contents) != 0):
                    f.write(col_tag.contents[0]+'\n')
                else:
                    f.write('NULL'+'\n')

    time.sleep(inc)

getXML(1)