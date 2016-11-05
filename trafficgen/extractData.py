
import os
import datetime
from datetime import datetime, timedelta
import time
def adjustTime(up,line):
    dt = datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f")
    if up == 1:
       dt = dt + timedelta(seconds=1)
    else:
       dt = dt - timedelta(seconds=1)
    newtime = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    return newtime

def extractTime(up,line):
    result = []
    newtime = adjustTime(up,line)
    result.append(newtime)
    result.append(line.split(" ")[1])
    return result
    
  
def extractTimeAndDcy(up,line): 
    result = []
    #look for first occurence of -
    dashindex = line.index("-")
    result.append(adjustTime(up,line[dashindex+1:]))
    result.append(line.split(" ")[1])
    result.append(line.split("-")[0]) #dcy name
    return result
    

def readAttacks(myattackfile):
    count = 0;
    traceCount = 0 
    newRequestTime=[]
    forkRequestTime=[]
    RestoreRequestTime=[]
    CloseRequestTime = []
    with open(myattackfile, "r") as f:
        for line in f:
            line = line.rstrip()
            count = count+1
            if "Trace_NewRequest" in line:
            	timestamp = line.split("|")
           	newRequestTime = extractTime(0,timestamp[1])
            if "Trace_Recv_Fork" in line:
            	timestamp = line.split("|")
           	forkRequestTime = extractTime(1,timestamp[1])
            if "Trace_Restored" in line:
            	timestamp = line.split("|")
           	RestoreRequestTime = extractTime(0,timestamp[1])
            if "Trace_ConnectionClosed" in line:
            	timestamp = line.split("|")
           	CloseRequestTime = extractTimeAndDcy(1,timestamp[1])
	        print newRequestTime
	        print forkRequestTime
	        print RestoreRequestTime
	        print CloseRequestTime
                cmd =  "sysdig -r /var/lib/libhp/.mon/sys-dcy.scap container.name=%s and \'evt.time>=%s and evt.time<=%s\' > ~/stream-%d.scap" % (CloseRequestTime[2],RestoreRequestTime[1],CloseRequestTime[1],traceCount)
                print cmd
                os.system(cmd)
                #cmd = "sudo editcap -F libpcap -A \'%s\' -B \'%s\' /var/lib/libhp/.mon/net-%s.pcap streamtemp1-%s.cap" % (newRequestTime[0],forkRequestTime[0],"target",traceCount)
                #print cmd
                #os.system(cmd)
                cmd = "sudo editcap -F libpcap -A \'%s\' -B \'%s\'  /var/lib/libhp/.mon/net-%s.pcap stream-%s.cap" % (RestoreRequestTime[0],CloseRequestTime[0],CloseRequestTime[2],traceCount)
                print cmd
                os.system(cmd)

                traceCount = traceCount + 1

                
time.sleep(10)

os.system("sudo -i forever stop redherring")
time.sleep(10)
readAttacks("/var/lib/libhp/.mon/timestamp.txt")
time.sleep(10)
os.system("sudo -i /etc/init.d/proxy_startup.sh")
time.sleep(240)

