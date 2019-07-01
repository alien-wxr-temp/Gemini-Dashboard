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
        statelist.append(['',line.strip(),'','','','',0,0,0,0])

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

            if xml2[j][3]=='NULL' or int(xml2[j][3])>=18000:
                xml2[j][3]='18000'
            else:
                if xml2[j][2]=='NULL':
                    statelist[i][6] = statelist[i][6]+timetick2-timetick1
                elif statelist[i][4]=='OnShift' and statelist[i][2]!=xml2[j][2]:
                    deltaTime = statelist[i][6]+timetick2-timetick1-int(xml2[j][3])
                    if statelist[i][2]=='Ready':
                        statelist[i][7] = statelist[i][7]+deltaTime
                    elif statelist[i][2]=='Talking':
                        statelist[i][6] = statelist[i][6]+deltaTime
                    elif statelist[i][2]=='Work Ready':
                        statelist[i][8] = statelist[i][8]+deltaTime
                    elif statelist[i][2]=='Not Ready':
                        statelist[i][9] = statelist[i][9]+deltaTime
            
            statelist[i][2] = xml2[j][2]
            statelist[i][3] = xml2[j][3]
            statelist[i][6] = int(statelist[i][3])
            statelist[i][4]=xml2[j][4]
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

        with open('./StateLog/'+ticks+'.txt', 'w') as f:
            for item in statelist:
                f.writelines('|'+item[0].ljust(7,' '))                  #No.
                f.writelines('|'+item[1].ljust(17,' '))                 #Name
                f.writelines('|'+item[2].ljust(10,' '))                 #ifReady
                f.writelines('|'+item[3].ljust(5,' '))                  #TimeInState
                f.writelines('|'+item[4].ljust(8,' '))                  #ifOnShift
                f.writelines('|'+item[5].ljust(8,' '))                  #State
                f.writelines('|'+str(item[6]).ljust(5,' '))             #LastingTime
                f.writelines('|'+str(item[7]).ljust(5,' '))             #FreeTime
                f.writelines('|'+str(item[8]).ljust(5,' '))             #BusyTime
                f.writelines('|'+str(item[9]).ljust(5,' '))             #AwayTime
                f.writelines('\n')
            f.close()

        with open('./StateLog/Current.txt', 'w') as f:
            for item in statelist:
                f.writelines('|'+item[0].ljust(7,' '))              #No.
                f.writelines('|'+item[1].ljust(17,' '))             #Name
                f.writelines('|'+item[2].ljust(10,' '))             #ifReady
                f.writelines('|'+item[3].ljust(5,' '))              #TimeInState
                f.writelines('|'+item[4].ljust(8,' '))              #ifOnShift
                f.writelines('|'+item[5].ljust(8,' '))              #State
                f.writelines('|'+str(item[6]).ljust(5,' '))         #LastingTime
                f.writelines('|'+str(item[7]).ljust(5,' '))         #FreeTime
                f.writelines('|'+str(item[8]).ljust(5,' '))         #BusyTime
                f.writelines('|'+str(item[9]).ljust(5,' '))         #AwayTime
                f.writelines('\n')
            f.close()

        with open('./ABLog/Current.txt', 'w') as f:
            f.writelines(time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime())+'\n')
            f.writelines('Free AE: '+str(freeNum)+' \n')
            print('Free AE: '+str(freeNum))
            for item in freeList:
                f.writelines('    '+item)
                print('    '+item)
                f.writelines('\n')
            f.writelines('\n')
            f.writelines('Busy AE: '+str(busyNum)+' \n')
            print('\nBusy AE: '+str(busyNum))
            for item in busyList:
                 f.writelines('    '+item)
                 print('    '+item)
                 f.writelines('\n')
            f.writelines('\n')
            f.writelines('Away AE: '+str(awayNum)+' \n')
            f.close()

        time.sleep(inc)
    except:
        print("exception and restart")
        with open('./Exception/errorLog.txt','a') as f:
            f.write(time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime())+'\n')
            f.close()
        time.sleep(inc/3)
        continue
