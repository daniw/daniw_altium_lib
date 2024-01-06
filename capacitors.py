from math import log10, floor
import requests

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
#BASE_ORDER_CODE = 'CC0603 NPO9BN'
#DIELECTRIC = 'C0G'

BASE_ORDER_CODE = 'CC0603 X7R9BB'
DIELECTRIC = 'X7R'

VOLTAGE_RATING = 50
PACKAGE = "0603"
#E 12
E_LIST = [10,12,15, 18 ,22, 27, 33, 39, 47, 56, 68,82]
GAINS = [1,10,100]
UNITS = ["P", "N", "U"]
UNIT_GAIN = {"P":1, "N":1000, "U":1000000}
################## END ORDER CONFIG ##################################


def get_order_code(productNumber):
    '''
    Get Order information from manufacturer Part Number
    '''
    global API_LIMIT
    print(F"Check Product {productNumber}")
    # Generate Request with product number and maximum 10 entries. Market Place products are axcluded. 
    search_request = KeywordSearchRequest(keywords=productNumber, record_count=10, exclude_market_place_products=True)
    # Place request on digikey webservice
    result = digikey.keyword_search(body=search_request, api_limits=API_LIMIT)
    # select results if packaging is CUT-Tape (CT) and minimum order quantity is 1
    orderable_parts = [(t.standard_pricing[-1].unit_price, t.manufacturer.value, t.manufacturer_part_number, t.digi_key_part_number,  t.primary_datasheet) 
        for t in result.products if t.packaging.value_id == '2' and t.minimum_order_quantity == 1]
    # Sord by price
    orderable_parts = sorted(orderable_parts, key=lambda a: a[0])
    print(F"Got Parts: {orderable_parts}") 
    return orderable_parts

def get_code(Prefix, value):
    '''
    get Capacitor code for specific value
    '''
    value = value
    # R Notation
    if(value <100):
        first = floor(value/10)
        return F"{Prefix}{first}R{floor((value-first*10))}"
    else:        
        base10 = floor(log10(abs(value/10)))
        return F"{Prefix}{floor(value/pow(10,base10))}{base10-1}"

if __name__ == '__main__':
    with open('output.txt', 'w') as f:
        for unit in UNITS:
            for gain in GAINS:
                for e_value in E_LIST:
                    value =e_value*gain
                    if(value>=100):
                        unitvalue = F"{round(value/10)}{unit}"
                    else:
                        unitvalue = F"{value/10}{unit}"
                    orderable_parts = get_order_code(get_code(BASE_ORDER_CODE, value*UNIT_GAIN[unit]))
                    
                    if(len(orderable_parts) > 0):
                        f.write(F"{unitvalue}/{PACKAGE}/{VOLTAGE_RATING}V/{DIELECTRIC}	{unitvalue}/{PACKAGE}/{VOLTAGE_RATING}V/{DIELECTRIC}	CAP SM {PACKAGE} {unitvalue.lower()}F {VOLTAGE_RATING}V {DIELECTRIC} " + 
                        F"	GENERIC	{PACKAGE}	{unitvalue.lower()}F	SCH/C_EU.SchLib	C	PCB/SMT_CHIP.PcbLib	CAP{PACKAGE}_{DIELECTRIC}	{value*UNIT_GAIN[unit]*1e-13:.2}	" + 
                        F"{orderable_parts[0][4]}")
                        i=0
                        for t in orderable_parts: 
                            f.write(F"	{t[1]}	{t[2]}	Digi-Key	{t[3]}")
                            i += 1
                            if(i>=2): 
                                break;
                        f.write(F"\n")
    
    #
    print(F"Current Digikey Limit {API_LIMIT}")