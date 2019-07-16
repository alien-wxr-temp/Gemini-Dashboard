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
        statelist.append(['',line.strip(),'','','','',0,0,0,0,0])

inc = 27

allTalks = 0            #All Talks

while True:
    try:
        xml = []        #Origin xml data elements
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
            while (j<len(xml2) and xml2[j][1]!=statelist[i][1]):
                j=j+1
            statelist[i][0]=xml2[j][0]
            #OnShift or OffShift
            if (xml2[j][4]=='true'):
                xml2[j][4] = 'OnShift'
            else:
                xml2[j][4] = 'OffShift'
            #Talks Recording
            if statelist[i][2]=='Ready' and xml2[j][2]=='Talking' and statelist[i][4]=='OnShift' and xml2[j][4]=='OnShift':
                allTalks = allTalks+1
                statelist[i][10] = statelist[i][10]+1
            #Time Calculating
            if xml2[j][3]=='NULL' or int(xml2[j][3])>=18000:                            # 18000s=5h, time overflow
                xml2[j][3] = '18000'
                statelist[i][2] = xml2[j][2]
                statelist[i][3] = xml2[j][3]
                statelist[i][6] = int(statelist[i][3])
            else:
                if xml2[j][2]=='NULL':                                                  # capture an intermediate state
                    statelist[i][3] = xml2[j][3]
                    statelist[i][6] = statelist[i][6]+timetick2-timetick1
                elif statelist[i][4]=='OnShift' and statelist[i][2]!=xml2[j][2]:
                    deltaTime = statelist[i][6]+timetick2-timetick1-int(xml2[j][3])
                    if statelist[i][2]=='Ready':
                        statelist[i][7] = deltaTime
                        statelist[i][3] = xml2[j][3]
                        statelist[i][6] = int(statelist[i][3])
                    elif statelist[i][2]=='Talking':
                        statelist[i][6] = deltaTime+int(xml2[j][3])
                        statelist[i][3] = xml2[j][3]
                    elif statelist[i][2]=='Work Ready':
                        statelist[i][8] = deltaTime
                        statelist[i][3] = xml2[j][3]
                        statelist[i][6] = int(statelist[i][3])
                    elif statelist[i][2]=='Not Ready':
                        statelist[i][9] = deltaTime
                        statelist[i][3] = xml2[j][3]
                        statelist[i][6] = int(statelist[i][3])
                    else:
                        statelist[i][3] = xml2[j][3]
                        statelist[i][6] = int(statelist[i][3])
                    statelist[i][2] = xml2[j][2]
                elif statelist[i][2]=='Work Ready':
                    statelist[i][6] = statelist[i][6]+int(xml2[j][3])-int(statelist[i][3])
                    statelist[i][3] = xml2[j][3]
                else:
                    statelist[i][2] = xml2[j][2]
                    statelist[i][3] = xml2[j][3]
                    statelist[i][6] = int(statelist[i][3])
            statelist[i][4] = xml2[j][4]
            #State
            if statelist[i][4]=='OnShift':
                if statelist[i][2]=='Ready':
                    statelist[i][5]='Free'
                    freeNum = freeNum+1
                    freeList.append(statelist[i][1])
                elif statelist[i][2]=='Talking' or statelist[i][2]=='Work Ready':
                    statelist[i][5]='Busy'
                    busyNum = busyNum+1
                    busyList.append(statelist[i][1])
                elif statelist[i][2]=='Not Ready':
                    statelist[i][5]='Away'
                    awayNum = awayNum+1
                    awayList.append(statelist[i][1])
                else:
                    statelist[i][5]='ErrState'
            else:
                statelist[i][5]='Offline'
            i=i+1

        with open('./CurrentLog/CurrentState.txt', 'w') as f:
            f.writelines(time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime())+'\n')
            f.writelines('|Numbers |AE Name           |oldState   |oTime |ifShift  |newState |nTime |freeT |BusyT |AwayT |Talks \n')
            f.writelines('_'*101+'\n')
            for item in statelist:
                f.writelines('|'+item[0].ljust(8,' '))              #No.
                f.writelines('|'+item[1].ljust(18,' '))             #Name
                f.writelines('|'+item[2].ljust(11,' '))             #ifReady
                f.writelines('|'+item[3].ljust(6,' '))              #TimeInState
                f.writelines('|'+item[4].ljust(9,' '))              #ifOnShift
                f.writelines('|'+item[5].ljust(9,' '))              #State
                f.writelines('|'+str(item[6]).ljust(6,' '))         #LastingTime
                f.writelines('|'+str(item[7]).ljust(6,' '))         #FreeTime
                f.writelines('|'+str(item[8]).ljust(6,' '))         #BusyTime
                f.writelines('|'+str(item[9]).ljust(6,' '))         #AwayTime
                f.writelines('|'+str(item[10]).ljust(6,' '))        #TalksCount
                f.writelines('\n')
            f.close()

        # for LabView
        with open('./data.txt', 'w') as f:
            f.writelines(str(timetick2)+',')                        #Timetick
            f.writelines(str(freeNum)+',')                          #FreeNum
            f.writelines(str(busyNum)+',')                          #BusyNum
            f.writelines(str(awayNum)+',')                          #AwayNum
            f.writelines(str(allTalks)+',')                         #AllTalks
            for item in statelist:
                f.writelines(str(item[6])+',')                      #currentStateTime
               #f.writelines(str(item[7])+',')                      #FreeTime
               #f.writelines(str(item[8])+',')                      #BusyTime
               #f.writelines(str(item[9])+',')                      #AwayTime
                f.writelines(item[0]+',')                           #No.
                f.writelines(item[1]+',')                           #Name
                f.writelines(item[5]+',')                           #State
                f.writelines(str(item[10])+',')                     #TalksCount
            f.close()

        time.sleep(inc)
    except:
        print("exception and restart")
        with open('./CurrentLog/errorLog.txt','a') as f:
            f.write(time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime())+'\n')
            f.close()
        time.sleep(inc/3)
        continue
