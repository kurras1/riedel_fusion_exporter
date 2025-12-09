import requests
import json
import copy
import re
import os

MNSET_IP_Address = os.getenv('MNSET_IP_Address', "0.0.0.0")
MNSET_NBAPI_Port = os.getenv('MNSET_NBAPI_Port', "9080")
MNSET_Fusion6B_Array_Name = os.getenv('MNSET_Fusion6B_Array_Name', "Fusion6B")
MNSET_Fusion3B_Array_Name = os.getenv('MNSET_Fusion3B_Array_Name', "Fusion3B")

Fusion6B_IP_Data_URL = f"http://{MNSET_IP_Address}:{MNSET_NBAPI_Port}/rest/{MNSET_Fusion6B_Array_Name}/0/emsfp/node/v1/self/ipconfig"
Fusion3B_IP_Data_URL = f"http://{MNSET_IP_Address}:{MNSET_NBAPI_Port}/rest/{MNSET_Fusion3B_Array_Name}/0/emsfp/node/v1/self/ipconfig"
Fusion6B_Self_Data_URL = f"http://{MNSET_IP_Address}:{MNSET_NBAPI_Port}/rest/{MNSET_Fusion6B_Array_Name}/0/emsfp/node/v1/self/system"
Fusion3B_Self_Data_URL = f"http://{MNSET_IP_Address}:{MNSET_NBAPI_Port}/rest/{MNSET_Fusion3B_Array_Name}/0/emsfp/node/v1/self/system"
FusionCompleteDataList = list()

FusionCoreTemp = list()
FusionCoreVoltage = list()
FusionUptime = list()
FusionFanSpeed = list()

def getDataFromMNSET():
    Fusion6B_IP_Data = json.loads(getHTTPData(Fusion6B_IP_Data_URL))
    Fusion3B_IP_Data = json.loads(getHTTPData(Fusion3B_IP_Data_URL))
    Fusion6B_Self_Data = json.loads(getHTTPData(Fusion6B_Self_Data_URL))
    Fusion3B_Self_Data = json.loads(getHTTPData(Fusion3B_Self_Data_URL))
    
    
    for Fusion in Fusion6B_IP_Data['contents']:
        if Fusion['code'] == 200:
            currentIP = Fusion['ipAdress']
            for Self in Fusion6B_Self_Data['contents']:
                if (Self['code'] == 200 and Self['ipAdress'] == currentIP):
                    CombinedFusionData = dict()
                    CombinedFusionData['hostname'] = json.loads(copy.deepcopy(Fusion['content']))['hostname']
                    CombinedFusionData['ipAddress'] = copy.deepcopy(Fusion['ipAdress'])
                    CombinedFusionData['unit'] = 'Fusion_6B'
                    CombinedFusionData['data'] = json.loads(copy.deepcopy(Self['content']))

                    FusionCompleteDataList.append(CombinedFusionData)
                    
    for Fusion in Fusion3B_IP_Data['contents']:
        if Fusion['code'] == 200:
            currentIP = Fusion['ipAdress']
            for Self in Fusion3B_Self_Data['contents']:
                if (Self['code'] == 200 and Self['ipAdress'] == currentIP):
                    CombinedFusionData = dict()
                    CombinedFusionData['hostname'] = json.loads(copy.deepcopy(Fusion['content']))['hostname']
                    CombinedFusionData['ipAddress'] = copy.deepcopy(Fusion['ipAdress'])
                    CombinedFusionData['unit'] = 'Fusion_3B'
                    CombinedFusionData['data'] = json.loads(copy.deepcopy(Self['content']))

                    FusionCompleteDataList.append(CombinedFusionData)

def convertTimestamp(timestamp):
    secs = int(re.sub("[^0-9]",'',timestamp.split(',')[0]))*24*60*60
    secs = secs + sum(int(x) * 60 ** i for i, x in enumerate(reversed(timestamp.split(',')[1].strip().split(':'))))
    return secs

def writePrometheusLabel(hostname, unit, ip_address):
    return f"instance=\"{ip_address}\",name=\"{hostname.replace(' ','_')}\",module=\"{unit}\""

def writePrometheusLine(hostname, unit, ip_address, core_temp=None, core_voltage=None, uptime=None, fan_speed=None):
    labels = writePrometheusLabel(hostname, unit, ip_address)
    
    if core_temp != None:
        return f"fusion_core_temp{{{labels}}} {core_temp}"
    elif core_voltage != None:
        return f"fusion_core_voltage{{{labels}}} {core_voltage}"
    elif uptime != None:
        return f"fusion_uptime{{{labels}}} {uptime}"
    elif fan_speed != None:
        return f"fusion_fan_speed{{{labels}}} {fan_speed}"
    else:
        return None 
    
def writePrometheusData():
    
    for Fusion in FusionCompleteDataList:
        FusionCoreTemp.append(
            writePrometheusLine(Fusion['hostname'], Fusion['unit'], Fusion['ipAddress'], core_temp=Fusion['data']['core_temp'])
            )
        FusionCoreVoltage.append(
            writePrometheusLine(Fusion['hostname'], Fusion['unit'], Fusion['ipAddress'], core_voltage=Fusion['data']['core_voltage'])
            )
        FusionUptime.append(
            writePrometheusLine(Fusion['hostname'], Fusion['unit'], Fusion['ipAddress'], uptime=convertTimestamp(Fusion['data']['uptime']))
            )
        try:
            FusionFanSpeed.append(
                writePrometheusLine(Fusion['hostname'], Fusion['unit'], Fusion['ipAddress'], fan_speed=Fusion['data']['fan_speed'])
                )
        except:
            pass
    
def formatPrometheusData():
    data = ""
    data += "# TYPE fusion_core_temp gauge"
    for Line in FusionCoreTemp:
        data += "\n"+Line
    data += "\n# TYPE fusion_core_voltage gauge"
    for Line in FusionCoreVoltage:
        data += "\n"+Line
    data += "\n# TYPE fusion_uptime counter"
    for Line in FusionUptime:
        data += "\n"+Line
    data += "\n# TYPE fusion_fan_speed gauge"
    for Line in FusionFanSpeed:
        data += "\n"+Line
    return data

def getHTTPData(url):
    #print("HTTP GET: ", url)
    response = requests.get(url)
    return response.text

def getPrometheusData():
    FusionCompleteDataList.clear()
    FusionCoreTemp.clear()
    FusionCoreVoltage.clear()
    FusionUptime.clear()
    FusionFanSpeed.clear()
    
    getDataFromMNSET()
    writePrometheusData()
    return formatPrometheusData()


