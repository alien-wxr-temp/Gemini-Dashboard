import requests
import re
from bs4 import BeautifulSoup
import time
import operator

url = 'https://us-aus-cuic1:8444/cuicui/permalink/?viewId=65B8C92C10000165005C5FD87D5BEAE0&linkType=xmlType&viewType=Grid'

statelist = []
timetick1 = int(time.time())
timetick2 = int(time.time())
with open('./nameList.txt', 'r') as f:
    for line in f:
        statelist.append(['',line.strip(),'','',''])

inc = 27
while True:
    try:
        xml = []        #origin xml data elements
        freeList = []   #
        freeNum = 0     #
        busyList = []   #
        busyNum = 0     #
        awayList = []   #
        awayNum = 0     #

        #Web spider
        myXML = requests.get(url, verify=False)
        soup = BeautifulSoup(myXML.text, "lxml")
        timetick1 = int(timetick2)
        timetick2 = int(time.time())
        ticks = time.strftime("%Y%m%d-%H%M%S", time.localtime())

        for row_tag in soup.report.children:
            j=0
            single = ['','','','','']
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
            while (j<len(xml2) and xml2[j][1]!=statelist[i][1]):
                j=j+1
            
            statelist[i][0] = xml2[j][0]                                    #No.
            if xml2[j][2]=='NULL':                                          # capture an intermediate state
                statelist[i][2] = statelist[i][2]                           #AgentState
                statelist[i][3] = statelist[i][3]+timetick2-timetick1       #TimeInState
            else:
                statelist[i][2] = xml2[j][2]                                #AgentState
                statelist[i][3] = xml2[j][3]                                #TimeInState
            if (xml2[j][4]=='true'):
                statelist[i][4] = 'OnShift'                                 #OnShift
            else:
                statelist[i][4] = 'OffShift'                                #OffShift
            i=i+1

        with open('./CurrentLog/CurrentState.txt', 'w') as f:
            f.writelines(time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime())+'\n')
            f.writelines('|Numbers |AE Name           |oldState   |oTime |ifShift  \n')
            f.writelines('_'*59+'\n')
            for item in statelist:
                f.writelines('|'+item[0].ljust(8,' '))                      #No.
                f.writelines('|'+item[1].ljust(18,' '))                     #Name
                f.writelines('|'+item[2].ljust(11,' '))                     #ifReady
                f.writelines('|'+item[3].ljust(6,' '))                      #TimeInState
                f.writelines('|'+item[4].ljust(9,' '))                      #ifOnShift
                f.writelines('\n')
            f.close()

        # for LabView
        with open('./data.txt', 'w') as f:
            f.writelines(str(timetick2)+',')                                #TimeStamp
            for item in statelist:
                f.writelines(item[0]+',')                                   #No.
                f.writelines(item[1]+',')                                   #Name
                f.writelines(item[2]+',')                                   #ifReady
                f.writelines(item[3]+',')                                   #TimeInState
                f.writelines(item[4]+',')                                   #ifOnShift
            f.close()

        time.sleep(inc)
    except:
        print("exception and restart")
        with open('./CurrentLog/errorLog.txt','a') as f:
            f.write(time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime())+'\n')
            f.close()
        time.sleep(inc/3)
        continue
