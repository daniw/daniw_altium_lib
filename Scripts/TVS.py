'''
Script to Generate Littel Fuse TVS Table

'''
from math import log10, floor
import requests
import re
import os
from pathlib import Path

import digikey
from digikey.v3.productinformation import KeywordSearchRequest, Filters, ManufacturerProductDetailsRequest,ParametricFilter
from digikey.v3.batchproductdetails import BatchProductDetailsRequest

import digikey_password

CACHE_DIR = Path('./digikey_cache')

digikey_password.digikey_password_init()
os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
os.environ['DIGIKEY_STORAGE_PATH'] = str(CACHE_DIR)
API_LIMIT = {}

################## ORDER CONFIG ######################################
PACKAGE = "SOD3717X135" # JEDEC SOD123



PACKAGE = "SOD3720X110" # JEDEC SOD123FL
CODES = ["SMF5.0A","SMF5.0CA", "SMF6.0A","SMF6.0CA", "SMF6.5A","SMF6.5CA", "SMF7.0A","SMF7.0CA", "SMF7.5A","SMF7.5CA", "SMF8.0A","SMF8.0CA", 
         "SMF8.5A","SMF8.5CA", "SMF9.0A","SMF9.0CA", "SMF10A","SMF10CA", "SMF11A","SMF11CA", "SMF12A","SMF12CA", "SMF13A","SMF13CA", "SMF14A","SMF14CA",
         "SMF15A","SMF15CA", "SMF16A","SMF16CA", "SMF17A","SMF17CA", "SMF18A","SMF18CA", "SMF20A","SMF20CA", "SMF22A","SMF22CA", "SMF24A","SMF24CA", 
         "SMF26A","SMF26CA", "SMF28A","SMF28CA", "SMF30A","SMF30CA", "SMF33A","SMF33CA", "SMF36A","SMF36CA", "SMF40A","SMF40CA", "SMF43A","SMF43CA", 
         "SMF45A","SMF45CA", "SMF48A","SMF48CA", "SMF51A","SMF51CA", "SMF54A","SMF54CA", "SMF58A","SMF58CA", "SMF60A","SMF60CA", "SMF64A","SMF64CA", 
         "SMF70A","SMF70CA", "SMF75A","SMF75CA", "SMF78A","SMF78CA", "SMF85A","SMF85CA", "SMF90A", "SMF100A", "SMF110A", "SMF120A", "SMF130A", 
         "SMF150A", "SMF160A", "SMF170A", "SMF180A", "SMF188A", "SMF200A", "SMF220A", "SMF250A"]
 
 
PACKAGE = "DIOM5226X230" # JEDEC DO-214AC
 
CODES = ["SMAJ5.0A", "SMAJ5.0CA", "SMAJ6.0A", "SMAJ6.0CA", "SMAJ6.5A", "SMAJ6.5CA", "SMAJ7.0A", "SMAJ7.0CA", "SMAJ7.5A", "SMAJ7.5CA", "SMAJ8.0A", "SMAJ8.0CA",
         "SMAJ8.5A", "SMAJ8.5CA", "SMAJ9.0A", "SMAJ9.0CA", "SMAJ10A", "SMAJ10CA", "SMAJ11A", "SMAJ11CA", "SMAJ12A", "SMAJ12CA", "SMAJ13A", "SMAJ13CA", "SMAJ14A", "SMAJ14CA",
         "SMAJ15A", "SMAJ15CA", "SMAJ16A", "SMAJ16CA", "SMAJ17A", "SMAJ17CA", "SMAJ18A", "SMAJ18CA", "SMAJ20A", "SMAJ20CA", "SMAJ22A", "SMAJ22CA", "SMAJ24A", "SMAJ24CA",
         "SMAJ26A", "SMAJ26CA", "SMAJ28A", "SMAJ28CA", "SMAJ30A", "SMAJ30CA", "SMAJ33A", "SMAJ33CA", "SMAJ36A", "SMAJ36CA", "SMAJ40A", "SMAJ40CA", "SMAJ43A", "SMAJ43CA", 
         "SMAJ45A", "SMAJ45CA", "SMAJ48A", "SMAJ48CA", "SMAJ51A", "SMAJ51CA", "SMAJ54A", "SMAJ54CA", "SMAJ58A", "SMAJ58CA", "SMAJ60A", "SMAJ60CA", "SMAJ64A", "SMAJ64CA",
         "SMAJ70A", "SMAJ70CA", "SMAJ75A", "SMAJ75CA", "SMAJ78A", "SMAJ78CA", "SMAJ85A", "SMAJ85CA", "SMAJ90A", "SMAJ90CA", "SMAJ100A", "SMAJ100CA", "SMAJ110A", "SMAJ110CA",
         "SMAJ120A", "SMAJ120CA", "SMAJ130A", "SMAJ130CA", "SMAJ150A", "SMAJ150CA", "SMAJ160A", "SMAJ160CA", "SMAJ170A", "SMAJ170CA", "SMAJ180A", "SMAJ180CA", "SMAJ188A", "SMAJ188CA",
         "SMAJ200A", "SMAJ200CA", "SMAJ220A", "SMAJ220CA", "SMAJ250A", "SMAJ250CA", "SMAJ300A", "SMAJ300CA", "SMAJ350A", "SMAJ350CA", "SMAJ400A", "SMAJ400CA", "SMAJ440A", "SMAJ440CA"]    
    
    
PACKAGE = "DIOM5436X265" # JEDEC DO-214AA
 
CODES = ["SMBJ5.0A", "SMBJ5.0CA", "SMBJ6.0A", "SMBJ6.0CA", "SMBJ6.5A", "SMBJ6.5CA", "SMBJ7.0A", "SMBJ7.0CA", "SMBJ7.5A", "SMBJ7.5CA", "SMBJ8.0A", "SMBJ8.0CA",
         "SMBJ8.5A", "SMBJ8.5CA", "SMBJ9.0A", "SMBJ9.0CA", "SMBJ10A", "SMBJ10CA", "SMBJ11A", "SMBJ11CA", "SMBJ12A", "SMBJ12CA", "SMBJ13A", "SMBJ13CA", "SMBJ14A", "SMBJ14CA",  
         "SMBJ15A", "SMBJ15CA", "SMBJ16A", "SMBJ16CA", "SMBJ17A", "SMBJ17CA", "SMBJ18A", "SMBJ18CA", "SMBJ20A", "SMBJ20CA", "SMBJ22A", "SMBJ22CA", "SMBJ24A", "SMBJ24CA",  
         "SMBJ26A", "SMBJ26CA", "SMBJ28A", "SMBJ28CA", "SMBJ30A", "SMBJ30CA", "SMBJ33A", "SMBJ33CA", "SMBJ36A", "SMBJ36CA", "SMBJ40A", "SMBJ40CA", "SMBJ43A", "SMBJ43CA",  
         "SMBJ45A", "SMBJ45CA", "SMBJ48A", "SMBJ48CA", "SMBJ51A", "SMBJ51CA", "SMBJ54A", "SMBJ54CA", "SMBJ58A", "SMBJ58CA", "SMBJ60A", "SMBJ60CA", "SMBJ64A", "SMBJ64CA",  
         "SMBJ70A", "SMBJ70CA", "SMBJ75A", "SMBJ75CA", "SMBJ78A", "SMBJ78CA", "SMBJ85A", "SMBJ85CA", "SMBJ90A", "SMBJ90CA", "SMBJ100A", "SMBJ100CA", "SMBJ110A", "SMBJ110CA",
         "SMBJ120A", "SMBJ120CA", "SMBJ130A", "SMBJ130CA", "SMBJ150A", "SMBJ150CA", "SMBJ160A", "SMBJ160CA", "SMBJ170A", "SMBJ170CA", "SMBJ180A", "SMBJ180CA", "SMBJ188A", "SMBJ188CA",
         "SMBJ200A", "SMBJ200CA", "SMBJ220A", "SMBJ220CA", "SMBJ250A", "SMBJ250CA", "SMBJ300A", "SMBJ300CA", "SMBJ350A", "SMBJ350CA", "SMBJ400A", "SMBJ400CA", "SMBJ440A", "SMBJ440CA"]


PACKAGE = "DIOM7959X265" # JEDEC DO-214AB
 
CODES = ["SMCJ5.0A", "SMCJ5.0CA", "SMCJ6.0A", "SMCJ6.0CA", "SMCJ6.5A", "SMCJ6.5CA", "SMCJ7.0A", "SMCJ7.0CA", "SMCJ7.5A", "SMCJ7.5CA", "SMCJ8.0A", "SMCJ8.0CA",
         "SMCJ8.5A", "SMCJ8.5CA", "SMCJ9.0A", "SMCJ9.0CA", "SMCJ10A", "SMCJ10CA", "SMCJ11A", "SMCJ11CA", "SMCJ12A", "SMCJ12CA", "SMCJ13A", "SMCJ13CA", "SMCJ14A", "SMCJ14CA",  
         "SMCJ15A", "SMCJ15CA", "SMCJ16A", "SMCJ16CA", "SMCJ17A", "SMCJ17CA", "SMCJ18A", "SMCJ18CA", "SMCJ20A", "SMCJ20CA", "SMCJ22A", "SMCJ22CA", "SMCJ24A", "SMCJ24CA",  
         "SMCJ26A", "SMCJ26CA", "SMCJ28A", "SMCJ28CA", "SMCJ30A", "SMCJ30CA", "SMCJ33A", "SMCJ33CA", "SMCJ36A", "SMCJ36CA", "SMCJ40A", "SMCJ40CA", "SMCJ43A", "SMCJ43CA",  
         "SMCJ45A", "SMCJ45CA", "SMCJ48A", "SMCJ48CA", "SMCJ51A", "SMCJ51CA", "SMCJ54A", "SMCJ54CA", "SMCJ58A", "SMCJ58CA", "SMCJ60A", "SMCJ60CA", "SMCJ64A", "SMCJ64CA",  
         "SMCJ70A", "SMCJ70CA", "SMCJ75A", "SMCJ75CA", "SMCJ78A", "SMCJ78CA", "SMCJ85A", "SMCJ85CA", "SMCJ90A", "SMCJ90CA", "SMCJ100A", "SMCJ100CA", "SMCJ110A", "SMCJ110CA",
         "SMCJ120A", "SMCJ120CA", "SMCJ130A", "SMCJ130CA", "SMCJ150A", "SMCJ150CA", "SMCJ160A", "SMCJ160CA", "SMCJ170A", "SMCJ170CA", "SMCJ180A", "SMCJ180CA", "SMCJ188A", "SMCJ188CA",
         "SMCJ200A", "SMCJ200CA", "SMCJ220A", "SMCJ220CA", "SMCJ250A", "SMCJ250CA", "SMCJ300A", "SMCJ300CA", "SMCJ350A", "SMCJ350CA", "SMCJ400A", "SMCJ400CA", "SMCJ440A", "SMCJ440CA"]


PACKAGE = "DIOM7959X265" # JEDEC DO-214AB
 
CODES = ["5.0SMDJ5.0A", "5.0SMDJ5.0CA", "5.0SMDJ6.0A", "5.0SMDJ6.0CA", "5.0SMDJ6.5A", "5.0SMDJ6.5CA", "5.0SMDJ7.0A", "5.0SMDJ7.0CA", "5.0SMDJ7.5A", "5.0SMDJ7.5CA", "5.0SMDJ8.0A", "5.0SMDJ8.0CA",
         "5.0SMDJ8.5A", "5.0SMDJ8.5CA", "5.0SMDJ9.0A", "5.0SMDJ9.0CA", "5.0SMDJ10A", "5.0SMDJ10CA", "5.0SMDJ11A", "5.0SMDJ11CA", "5.0SMDJ12A", "5.0SMDJ12CA", "5.0SMDJ13A", "5.0SMDJ13CA", "5.0SMDJ14A", "5.0SMDJ14CA",  
         "5.0SMDJ15A", "5.0SMDJ15CA", "5.0SMDJ16A", "5.0SMDJ16CA", "5.0SMDJ17A", "5.0SMDJ17CA", "5.0SMDJ18A", "5.0SMDJ18CA", "5.0SMDJ20A", "5.0SMDJ20CA", "5.0SMDJ22A", "5.0SMDJ22CA", "5.0SMDJ24A", "5.0SMDJ24CA",  
         "5.0SMDJ26A", "5.0SMDJ26CA", "5.0SMDJ28A", "5.0SMDJ28CA", "5.0SMDJ30A", "5.0SMDJ30CA", "5.0SMDJ33A", "5.0SMDJ33CA", "5.0SMDJ36A", "5.0SMDJ36CA", "5.0SMDJ40A", "5.0SMDJ40CA", "5.0SMDJ43A", "5.0SMDJ43CA",  
         "5.0SMDJ45A", "5.0SMDJ45CA", "5.0SMDJ48A", "5.0SMDJ48CA", "5.0SMDJ51A", "5.0SMDJ51CA", "5.0SMDJ54A", "5.0SMDJ54CA", "5.0SMDJ58A", "5.0SMDJ58CA", "5.0SMDJ60A", "5.0SMDJ60CA", "5.0SMDJ64A", "5.0SMDJ64CA",  
         "5.0SMDJ70A", "5.0SMDJ70CA", "5.0SMDJ75A", "5.0SMDJ75CA", "5.0SMDJ78A", "5.0SMDJ78CA", "5.0SMDJ85A", "5.0SMDJ85CA", "5.0SMDJ90A", "5.0SMDJ90CA", "5.0SMDJ100A", "5.0SMDJ100CA", "5.0SMDJ110A", "5.0SMDJ110CA",
         "5.0SMDJ120A", "5.0SMDJ120CA", "5.0SMDJ130A", "5.0SMDJ130CA", "5.0SMDJ150A", "5.0SMDJ150CA", "5.0SMDJ160A", "5.0SMDJ160CA", "5.0SMDJ170A", "5.0SMDJ170CA", "5.0SMDJ180A", "5.0SMDJ180CA", "5.0SMDJ188A", "5.0SMDJ188CA",
         "5.0SMDJ200A", "5.0SMDJ200CA", "5.0SMDJ220A", "5.0SMDJ220CA", "5.0SMDJ250A", "5.0SMDJ250CA", "5.0SMDJ300A", "5.0SMDJ300CA", "5.0SMDJ350A", "5.0SMDJ350CA", "5.0SMDJ400A", "5.0SMDJ400CA", "5.0SMDJ440A", "5.0SMDJ440CA"]


################## END ORDER CONFIG ##################################


def get_order_code(productNumber):
    '''
    Get Order information from manufacturer Part Number
    '''
    global API_LIMIT
    print(F"Check Product {productNumber}")
    # Generate Request with product number and maximum 10 entries. Market Place products are axcluded. 
    tvs_filters = Filters(parametric_filters = [ParametricFilter(parameter_id=7, value_id='2'), ParametricFilter(parameter_id=-1, value_id='18')])
    
    search_request = KeywordSearchRequest(keywords=productNumber, record_count=3, exclude_market_place_products=True, filters=tvs_filters)
    # Place request on digikey webservice
    result = digikey.keyword_search(body=search_request, api_limits=API_LIMIT)
    # select results if packaging is CUT-Tape (CT) and minimum order quantity is 1
    orderable_parts = [t 
        for t in result.products if t.minimum_order_quantity == 1 and t.packaging.value_id == '2']
    # Sord by price
    orderable_parts = sorted(orderable_parts, key=lambda a: a.standard_pricing[-1].unit_price)
    print(F"Got Parts: {[t.manufacturer_part_number for t in orderable_parts]}") 
    return orderable_parts
  
def get_parameter_by_id(parameters, parameter_id):
    return [t.value for t in parameters if t.parameter_id == parameter_id][0];


if __name__ == '__main__':
    with open('output.txt', 'w') as f:
        for code in CODES:
            # Digikey can not search with only two letters -> L at the end is necessary so "1R" gets "1RL"
            orderable_parts = get_order_code(code)
            
            if(len(orderable_parts) > 0):
                f.write(F"{code}	{code}	{orderable_parts[0].product_description} " + 
                F"	{orderable_parts[0].manufacturer.value}	{get_parameter_by_id(orderable_parts[0].parameters,16)}	{code}	SCH/D_IEC.SchLib	D_TVS	PCB/SOD.PcbLib	{PACKAGE}	{get_parameter_by_id(orderable_parts[0].parameters,761)}	" + 
                F"{orderable_parts[0].primary_datasheet}")
                i=0
                for t in orderable_parts: 
                    f.write(F"	{t.manufacturer.value}	{t.manufacturer_part_number}	Digi-Key	{t.digi_key_part_number}")
                    i += 1
                    if(i>=2): 
                        break;
                f.write(F"\n")
    
    #
    print(F"Current Digikey Limit {API_LIMIT}")