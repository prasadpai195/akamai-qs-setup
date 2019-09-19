#!/usr/bin/env python
import requests
import json
from akamai.edgegrid import EdgeGridAuth,EdgeRc
from urllib.parse import urljoin
import re,os
import sys
import argparse
from datetime import datetime
import calendar
from termcolor import colored
edgerc_file = os.path.join(os.path.expanduser("~"), '.edgerc')
edgerc = EdgeRc(edgerc_file)
section="devopswb"
base_url = edgerc.get(section,'host')
baseurl=str('https://')+str(base_url)
client_token=edgerc.get(section,'client_token')
client_secret=edgerc.get(section,'client_secret')
access_token=edgerc.get(section,'access_token')
s = requests.Session()
s.auth = EdgeGridAuth(
client_token=client_token,
client_secret=client_secret,
access_token=access_token
)
def searchpropertydetails():
    data={"propertyName": "prvenkat_ion_devops_sd_template"}
    headers = {"content-type": "application/json"}
    result=s.post(urljoin(baseurl,'/papi/v1/search/find-by-value?accountSwitchKey=1-6JHGX'), data=json.dumps(data), headers=headers)
    return result
def getetagfromconfig(propertyId,propertyversion,contractId,groupId):
    propertyversion=str(propertyversion)
    result=s.get(urljoin(baseurl,'/papi/v1/properties/'+propertyId+'/versions/'+propertyversion+'/rules?contractId='+contractId+'&groupId='+groupId+'&accountSwitchKey=1-6JHGX'))
    temp_json=json.dumps(result.json())
    ruletree=json.loads(temp_json)
    result_final_etag=ruletree["etag"]
    return result_final_etag
def cloneproperty(propertyId,propertyversion,contractId,groupId,hostname,config_etag):
    data={"productId": "prd_Fresca","propertyName": hostname,"cloneFrom": {"propertyId": propertyId,"version": propertyversion,"cloneFromVersionEtag": config_etag,"copyHostnames": "false"}}
    headers = {"content-type": "application/json"}
    result=s.post(urljoin(baseurl,'/papi/v1/properties/?contractId='+contractId+'&groupId='+groupId+'&accountSwitchKey=1-6JHGX'), data=json.dumps(data), headers=headers)
    return result
def addHostNames(hostname,contractId,groupId,propertyId):
  headers={"content-type": "application/json"}
  data=[{"cnameTo":"test.jmorriss.com.edgesuite.net" ,"cnameFrom": hostname,"cnameType": "EDGE_HOSTNAME","secure":"false"}]
  result=s.put(urljoin(baseurl, '/papi/v1/properties/'+propertyId+'/versions/1/hostnames/?contractId='+ contractId+'&groupId='+groupId+'&validateHostnames=true&accountSwitchKey=1-6JHGX'),data=json.dumps(data),headers=headers)
  return result
def createCPCodes(contractId,groupId,hostname):
  headers={"content-type": "application/json"}
  data={"cpcodeName": hostname ,"productId": "prd_Fresca"}
  result=s.post(urljoin(baseurl,'/papi/v1/cpcodes?contractId='+contractId+'&groupId='+groupId+'&accountSwitchKey=1-6JHGX'), data=json.dumps(data), headers=headers)
  return result
def getCPCodes(cpcode,contractId,groupId):
   result=s.get(urljoin(baseurl,'/papi/v0/cpcodes/cpc_'+cpcode+'?contractId='+contractId+'&groupId='+groupId+'&accountSwitchKey=1-6JHGX'))
   return result
def updateConfigRules(contractId,groupId,propertyId,originname,cpcode,cpcode_time,hostname):
  headers = {"content-type": "application/vnd.akamai.papirules.latest+json"}
  data={"rules":{"name":"default","children":[{"name":"Performance","children":[{"name":"CompressibleObjects","children":[],"behaviors":[{"name":"gzipResponse","options":{"behavior":"ALWAYS"}}],"criteria":[{"name":"contentType","options":{"matchCaseSensitive":False,"matchOperator":"IS_ONE_OF","matchWildcard":True,"values":["text/*","application/javascript","application/x-javascript","application/x-javascript*","application/json","application/x-json","application/*+json","application/*+xml","application/text","application/vnd.microsoft.icon","application/vnd-ms-fontobject","application/x-font-ttf","application/x-font-opentype","application/x-font-Truetype","application/xmlfont/eot","application/xml","font/opentype","font/otf","font/eot","image/svg+xml","image/vnd.microsoft.icon"]}}],"criteriaMustSatisfy":"all","comments":"Compressescontenttoimproveperformanceofclientswithslowconnections.AppliesLastMileAccelerationtorequestswhenthereturnedobjectsupportsgzipcompression."}],"behaviors":[{"name":"enhancedAkamaiProtocol","options":{"display":""}},{"name":"http2","options":{"enabled":""}},{"name":"allowTransferEncoding","options":{"enabled":True}},{"name":"removeVary","options":{"enabled":True}},{"name":"sureRoute","options":{"enabled":True,"forceSslForward":False,"raceStatTtl":"30m","testObjectUrl":"/akamai/test-object.html","toHostStatus":"INCOMING_HH","type":"PERFORMANCE","enableCustomKey":False,"srDownloadLinkTitle":""}},{"name":"prefetch","options":{"enabled":True}}],"criteria":[],"criteriaMustSatisfy":"all","comments":"Improvestheperformanceofdeliveringobjectstoendusers.Behaviorsinthisruleareappliedtoallrequestsasappropriate."},{"name":"Offload","children":[{"name":"CSSandJavaScript","children":[],"behaviors":[{"name":"caching","options":{"behavior":"MAX_AGE","mustRevalidate":False,"ttl":"1d"}},{"name":"prefreshCache","options":{"enabled":True,"prefreshval":90}},{"name":"prefetchable","options":{"enabled":True}}],"criteria":[{"name":"fileExtension","options":{"matchCaseSensitive":False,"matchOperator":"IS_ONE_OF","values":["css","js"]}}],"criteriaMustSatisfy":"any","comments":"OverridesthedefaultcachingbehaviorforCSSandJavaScriptobjectsthatarecachedontheedgeserver.Becausetheseobjecttypesaredynamic,theTTLisbrief."},{"name":"StaticObjects","children":[],"behaviors":[{"name":"caching","options":{"behavior":"MAX_AGE","mustRevalidate":False,"ttl":"7d"}},{"name":"prefreshCache","options":{"enabled":True,"prefreshval":90}},{"name":"prefetchable","options":{"enabled":True}}],"criteria":[{"name":"fileExtension","options":{"matchCaseSensitive":False,"matchOperator":"IS_ONE_OF","values":["aif","aiff","au","avi","bin","bmp","cab","carb","cct","cdf","class","doc","dcr","dtd","exe","flv","gcf","gff","gif","grv","hdml","hqx","ico","ini","jpeg","jpg","mov","mp3","nc","pct","pdf","png","ppc","pws","swa","swf","txt","vbs","w32","wav","wbmp","wml","wmlc","wmls","wmlsc","xsd","zip","pict","tif","tiff","mid","midi","ttf","eot","woff","woff2","otf","svg","svgz","webp","jxr","jar","jp2"]}}],"criteriaMustSatisfy":"any","comments":"Overridesthedefaultcachingbehaviorforimages,music,andsimilarobjectsthatarecachedontheedgeserver.Becausetheseobjecttypesarestatic,theTTLislong."},{"name":"UncacheableResponses","children":[],"behaviors":[{"name":"downstreamCache","options":{"behavior":"TUNNEL_ORIGIN"}}],"criteria":[{"name":"cacheability","options":{"matchOperator":"IS_NOT","value":"CACHEABLE"}}],"criteriaMustSatisfy":"all","comments":"Overridesthedefaultdownstreamcachingbehaviorforuncacheableobjecttypes.InstructstheedgeservertopassCache-Controland/orExpireheadersfromtheorigintotheclient."}],"behaviors":[{"name":"caching","options":{"behavior":"NO_STORE"}},{"name":"cacheError","options":{"enabled":True,"preserveStale":True,"ttl":"10s"}},{"name":"downstreamCache","options":{"allowBehavior":"LESSER","behavior":"ALLOW","sendHeaders":"CACHE_CONTROL_AND_EXPIRES","sendPrivate":False}},{"name":"tieredDistribution","options":{"enabled":True,"tieredDistributionMap":"CH2"}}],"criteria":[],"criteriaMustSatisfy":"all","comments":"Controlscaching,whichoffloadstrafficawayfromtheorigin.Mostobjectstypesarenotcached.However,thechildrulesoverridethisbehaviorforcertainsubsetsofrequests."},{"name":"NSoriginforStaticfonts","children":[],"behaviors":[{"name":"origin","options":{"originType":"NET_STORAGE","netStorage":{"downloadDomainName":"jmtest.download.akamai.com","cpCode":43363,"g2oToken":"43363=Utj9Z8y9z2H875WEj8THqg51v864so798O1fD64Y1B711n0X2k"}}},{"name":"caching","options":{"behavior":"MAX_AGE","mustRevalidate":False,"ttl":"10m"}}],"criteria":[{"name":"fileExtension","options":{"matchOperator":"IS_ONE_OF","values":["woff"],"matchCaseSensitive":False}}],"criteriaMustSatisfy":"all"},{"name":"ImageManager","children":[],"behaviors":[{"name":"caching","options":{"behavior":"MAX_AGE","mustRevalidate":False,"ttl":"30d"}},{"name":"imageManager","options":{"advanced":False,"apiReferenceTitle":"","applyBestFileType":True,"enabled":True,"policyTokenDefault":"prvenkat_ion_devops_sd_template","resize":False,"settingsTitle":"","superCacheRegion":"US","trafficTitle":"","cpCodeOriginal":{"id":13944,"description":"testCP1","products":[],"createdDate":1106691717000,"cpCodeLimits":"null","name":"testCP1"},"cpCodeTransformed":{"id":22635,"description":"Testexample.com","products":[],"createdDate":1139998479000,"cpCodeLimits":"null","name":"Testexample.com"}}}],"criteria":[{"name":"fileExtension","options":{"matchCaseSensitive":False,"matchOperator":"IS_ONE_OF","values":["jpg","gif","jpeg","png","imviewer"]}}],"criteriaMustSatisfy":"all","comments":"EnableScaleforMobiletoservethebestavailablesizefortherequestingdevice.(Carefultestingishighlyrecommended.)EnableUseBestFileTypetoservetheimageformatthatworksbestfortherequestingclient.Toconfigurebreakpointwidths,derivativeimagequality,andartistictransformations,saveandactivatethisconfiguration;then,createpoliciesforthispolicysetviaeitherImageManagerPolicyManagerortheOPENImageManagerAPI."}],"behaviors":[{"name":"origin","options":{"cacheKeyHostname":"ORIGIN_HOSTNAME","compress":True,"enableTrueClientIp":False,"forwardHostHeader":"REQUEST_HOST_HEADER","hostname":originname,"httpPort":80,"httpsPort":443,"originSni":True,"originType":"CUSTOMER","verificationMode":"PLATFORM_SETTINGS","originCertificate":"","ports":""}},{"name":"cpCode","options":{"value":{"id":cpcode,"description":hostname,"products":[],"createdDate":cpcode_time,"cpCodeLimits":"null","name":hostname}}},{"name":"allowPost","options":{"allowWithoutContentLength":False,"enabled":True}},{"name":"mPulse","options":{"apiKey":"","bufferSize":"","configOverride":"","enabled":True,"requirePci":False,"titleOptional":""}}],"options":{"is_secure":False},"variables":[],"comments":"ThebehaviorsintheDefaultRuleapplytoallrequestsforthepropertyhostname(s)unlessanotherruleoverridestheDefaultRulesettings."}}
  result=s.put(urljoin(baseurl, '/papi/v1/properties/'+propertyId+'/versions/1/rules/?contractId='+contractId+'&groupId='+groupId+'&validateRules=true&accountSwitchKey=1-6JHGX'),data=json.dumps(data),headers=headers)
  return result
def activateConfigStaging(contractId,groupId,propertyId):
  data = {"propertyVersion": 1 ,"network": "STAGING","note": "Initial Activation","notifyEmails": ["prvenkat@akamai.com"],"acknowledgeAllWarnings":1}
  headers = {"content-type": "application/json"}
  result=s.post(urljoin(baseurl,'/papi/v1/properties/'+propertyId+'/activations/?contractId='+contractId+'&groupId='+groupId+'&accountSwitchKey=1-6JHGX'), data=json.dumps(data), headers=headers)
  return result
def activateConfigProduction(contractId,groupId,propertyId):
  data = {"propertyVersion": 1 ,"network": "PRODUCTION","note": "Initial Activation","notifyEmails": ["prvenkat@akamai.com"],"acknowledgeAllWarnings":1}
  headers = {"content-type": "application/json"}
  result=s.post(urljoin(baseurl,'/papi/v1/properties/'+propertyid+'/activations/?contractId='+contractId+'&groupId='+groupId+'&accountSwitchKey=1-6JHGX'), data=json.dumps(data), headers=headers)
  return result