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



PACKAGE = "SOD1608X065" # JEDEC SOD523
PACKAGE_ID = "400246"
CODES = ["BZT52C2V4T", "BZT52C2V7T", "BZT52C3V0T", "BZT52C3V3T", "BZT52C3V6T", "BZT52C3V9T", "BZT52C4V3T", 
"BZT52C4V7T", "BZT52C5V1T", "BZT52C5V6T", "BZT52C6V2T", "BZT52C6V8T", "BZT52C7V5T", "BZT52C8V2T", "BZT52C9V1T", 
"BZT52C10T", "BZT52C11T", "BZT52C12T", "BZT52C13T", "BZT52C15T", "BZT52C16T", "BZT52C18T", "BZT52C20T", 
"BZT52C22T", "BZT52C24T", "BZT52C27T", "BZT52C30T", "BZT52C33T", "BZT52C36T", "BZT52C39T"]
 
 
PACKAGE = "SOD3718X125" # JEDEC SOD-123
PACKAGE_ID = "404824"
CODES = ["BZT52C2V4", "BZT52C2V7", "BZT52C3V0", "BZT52C3V3", "BZT52C3V6", "BZT52C3V9", "BZT52C4V3", 
"BZT52C4V7", "BZT52C5V1", "BZT52C5V6", "BZT52C6V2", "BZT52C6V8", "BZT52C7V5", "BZT52C8V2", "BZT52C9V1", 
"BZT52C10", "BZT52C11", "BZT52C12", "BZT52C13", "BZT52C15", "BZT52C16", "BZT52C18", "BZT52C20", "BZT52C22", 
"BZT52C24", "BZT52C27", "BZT52C30", "BZT52C33", "BZT52C36", "BZT52C39", "BZT52C43", "BZT52C47", "BZT52C51", 
"BZT52C56", "BZT52C62", "BZT52C68", "BZT52C75"]



################## END ORDER CONFIG ##################################


def get_order_code(productNumber):
    '''
    Get Order information from manufacturer Part Number
    '''
    global API_LIMIT
    print(F"Check Product {productNumber}")
    # Generate Request with product number and maximum 10 entries. Market Place products are axcluded. 
    tvs_filters = Filters(parametric_filters = [ParametricFilter(parameter_id=7, value_id='2'),ParametricFilter(parameter_id=16, value_id=PACKAGE_ID)])#, ParametricFilter(parameter_id=-1, value_id='353')
    
    search_request = KeywordSearchRequest(keywords=productNumber, record_count=3, exclude_market_place_products=True, filters=tvs_filters)
    # Place request on digikey webservice
    result = digikey.keyword_search(body=search_request, api_limits=API_LIMIT)
    # select results if packaging is CUT-Tape (CT) and minimum order quantity is 1
    #print(result)
    orderable_parts = [t 
        for t in result.products if t.minimum_order_quantity == 1 and t.packaging.value_id == '2']
    # Sord by price
    orderable_parts = sorted(orderable_parts, key=lambda a: a.standard_pricing[-1].unit_price)
    print(F"Got Parts: {[t.manufacturer_part_number for t in orderable_parts]}") 
    return orderable_parts
  
def get_parameter_by_id(parameters, parameter_id):
    return [t.value for t in parameters if t.parameter_id == parameter_id][0];


if __name__ == '__main__':
    with open('zener.txt', 'w') as f:
        for code in CODES:
            # Digikey can not search with only two letters -> L at the end is necessary so "1R" gets "1RL"
            orderable_parts = get_order_code(code)
            
            if(len(orderable_parts) > 0):
                #print(orderable_parts[0]);
                #exit()
                f.write(F"{code}	{code}	{orderable_parts[0].product_description} " + 
                F"	{orderable_parts[0].manufacturer.value}	{get_parameter_by_id(orderable_parts[0].parameters,16)}	{code}	SCH/D_IEC.SchLib	" + 
                F"D_Zener	PCB/SOD.PcbLib	{PACKAGE}	{get_parameter_by_id(orderable_parts[0].parameters,920)}	" + 
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