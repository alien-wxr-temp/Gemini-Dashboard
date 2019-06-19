import requests
import re
from bs4 import BeautifulSoup
import time
import operator

url = 'https://us-aus-cuic1:8444/cuicui/permalink/?viewId=65B8C92C10000165005C5FD87D5BEAE0&linkType=xmlType&viewType=Grid'
single = ['','','','','','','']

statelist = []
with open('C:/Users/eriwang/OneDrive - National Instruments/电话Dashboard项目/Gemini-Dashboard/PyGetXML/nameList.txt', 'r') as f:
    for line in f:
        statelist.append(['',line.strip(),'','','','',''])

def getXML(inc = 60):
    while True:
        xml = []
        availableList = []
        availableNum = 0
        busyList = []
        busyNum = 0

        myXML = requests.get(url, verify=False)
        ticks = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        soup = BeautifulSoup(myXML.text, "lxml")
        for row_tag in soup.report.children:
            j=0
            single = ['','','','','','','']
            for col_tag in row_tag.children:
                if (col_tag['name']=='AgentLogin' or col_tag['name']=='FullName' or col_tag['name']=='AgentState' or col_tag['name']=='TimeInState' or col_tag['name']=='OnShift'):
                    if (len(col_tag.contents) != 0):
                        single[j] = col_tag.contents[0]
                    else:
                        single[j] = 'NULL'
                    j=j+1
            xml.append(single)

        xml2 = [list(t) for t in set(tuple(_) for _ in xml)]
        xml2.sort(key=operator.itemgetter(1))
        i=0
        j=0
        while (i<len(statelist)):
            while (xml2[j][1]!=statelist[i][1]):
                j=j+1
            statelist[i][0]=xml2[j][0]
            statelist[i][2]=xml2[j][2]
            statelist[i][3]=xml2[j][3]
            statelist[i][4]=xml2[j][4]
            if (statelist[i][4]=='true' and statelist[i][2]=='Ready'):
                statelist[i][5]='Available'
                statelist[i][6]='1'
                availableNum = availableNum+1
                availableList.append(statelist[i][1])
            elif (statelist[i][4]=='true' and (statelist[i][2]=='Talking' or statelist[i][2]=='Work Ready')):
                statelist[i][5]='busy'
                statelist[i][6]='2'
                busyNum = busyNum+1
                busyList.append(statelist[i][1])
            else:
                statelist[i][5]='away'
                statelist[i][6]='3'
            i=i+1

        with open('C:/Users/eriwang/OneDrive - National Instruments/电话Dashboard项目/StateLog/'+ticks+'.txt', 'w') as f:
            for item in statelist:
                f.writelines(item)
                f.writelines('\n')
            f.close()

        with open('C:/Users/eriwang/OneDrive - National Instruments/电话Dashboard项目/ABLog/'+ticks+'.txt', 'w') as f:
            f.writelines('Available AE: '+str(availableNum)+' \n')
            for item in availableList:
                f.writelines(item)
                f.writelines('\n')
            f.writelines('\n')
            f.writelines('Busy AE: '+str(busyNum)+' \n')
            for item in busyList:
                f.writelines(item)
                f.writelines('\n')
            f.close()

        time.sleep(inc)

getXML(18)