#!/usr/bin/env python
import requests
import json
from akamai.edgegrid import EdgeGridAuth
from urllib.parse import urljoin
import re
import sys
import argparse
from datetime import datetime
import calendar
import time
from termcolor import colored
from controls import searchpropertydetails,getetagfromconfig,cloneproperty,addHostNames,createCPCodes,updateConfigRules,activateConfigStaging,getCPCodes,activateConfigProduction
if __name__ == '__main__':
    print(colored("\n \nThe process has started. This program will: \n 1. Clone the configuration \n 2. Create a new CPCODE\n 3. Add the origin hostname to the configuration\n 4. Deploy to staging and production",'white'))
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--d",help="ENTER YOUR HOSTNAME")
        parser.add_argument("--o",help="ENTER YOUR ORIGINHOSTNAME")
        hostname=str(parser.parse_args().d)    
        originname=str(parser.parse_args().o)
        print("\n")
        print(colored("--> Hostname is:"+hostname+"",'yellow'))
        print(colored("--> Origin is:"+originname+"",'yellow'))
    except:
        print(colored("Invalid arguments passed.Try again",'red'))
        exit()
    try:
        print(colored("\nExtracting the necessary details, please wait...",'yellow'))
        propdetailssearch=searchpropertydetails()
        if propdetailssearch.status_code != 200:
            print(colored("Something went wrong when extracting the details",'red'))
            print(colored(json.dumps(propdetailssearch.json(),indent=4),'red'))
            exit();
        else:
            datajson=json.dumps(propdetailssearch.json());
            data=json.loads(datajson);
            for items in data["versions"]["items"]:
                if items["stagingStatus"] == "ACTIVE":
                    contractId=items["contractId"]
                    groupId=items["groupId"]
                    propertyId=items["propertyId"]
                    propertyversion=items["propertyVersion"]
                    config_etag=getetagfromconfig(propertyId,propertyversion,contractId,groupId)
            print(colored("Done!",'yellow'))
            print(colored("Creating a new configuration now. Please hold on..",'yellow'))
            cloneresults=cloneproperty(propertyId,propertyversion,contractId,groupId,hostname,config_etag)
            if cloneresults.status_code != 201:
                print(colored("Something went wrong when cloning the configuration",'red'))
                print(colored(json.dumps(cloneresults.json(),indent=4),'red'))
                exit();
            else:
                print(colored("Cloning the template config successful now. Let us now add the hostname into the configuration. Please hold on.",'yellow'))
                outputcatch=re.search('(.*)\/properties\/(.*)\?(.*)',str(cloneresults.json()))
                newpropertyId=outputcatch.group(2)
                addhostnameresults=addHostNames(hostname,contractId,groupId,newpropertyId)
                if addhostnameresults.status_code != 200:
                    print(colored("Something went wrong when adding Host names",'red'))
                    print(colored(json.dumps(addhostnameresults.json(),indent=4),'red'))
                    exit();
                else:
                    print(colored("Host name addition successful. Let us create the CPCODE now",'yellow'))
                    cpcoderesults=createCPCodes(contractId,groupId,hostname)
                    if cpcoderesults.status_code != 201:
                        print(colored("Something went wrong when creating CPCODES",'red'))
                        print(colored(json.dumps(cpcoderesults.json(),indent=4),'red'))
                        exit();
                    else:
                        print(colored("CPCODE creation successful. Let us update the config now",'yellow'))
                        cpcodeapioutput=re.search('(.*)cpc_(.*)\?(.*)',str(cpcoderesults.json()))   
                        cpcode=int(cpcodeapioutput.group(2))
                        cpcode_status=getCPCodes(str(cpcode),contractId,groupId)
                        ch=re.search('(.*)([0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}Z)(.*)',str(cpcode_status.json()))
                        output_cp_code_time_capture=ch.group(2)
                        utc_time = datetime.strptime(output_cp_code_time_capture, "%Y-%m-%dT%H:%M:%SZ")
                        epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
                        cpcode_time=int(epoch_time)
                        updateconfigresult=updateConfigRules(contractId,groupId,newpropertyId,originname,cpcode,cpcode_time,hostname)
                        if updateconfigresult.status_code != 200:
                            print(colored("Something went wrong config update",'red'))
                            print(colored(json.dumps(updateconfigresult.json(),indent=4),'red'))
                            exit();
                        else:
                            print(colored("Configuration update successful. Let us activate the config now to staging netork",'yellow'))
                            resultactivatestaging=activateConfigStaging(contractId,groupId,newpropertyId)
                            if resultactivatestaging.status_code != 201:
                                print(colored("Something went wrong with activation",'red'))
                                print(colored(json.dumps(resultactivatestaging.json(),indent=4),'red'))
                                exit();
                            else:
                                print(colored("Staging activation succesful, lets activate to PRODUCTION now.",'yellow'))
                                resultactivateproduction=activateConfigProduction(contractId,groupId,newpropertyId)
                                if resultactivateproduction != 201:
                                    print(colored("Something went wrong with activation",'red'))
                                    print(colored(json.dumps(resultactivateproduction.json(),indent=4),'red'))
                                    exit();
                                else:
                                    print(colored("All operations complete. Thank you for using this program",'yellow'))
                                    exit();                                
    except Exception as e:
        print(str(e))
    