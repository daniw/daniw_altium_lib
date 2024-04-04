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
PACKAGE = "0402"
BASE_ORDER_CODE = F'RC{PACKAGE}FR-.'+'{2}'


#E 24
E_LIST = [10, 11, 12, 13, 15, 16, 18 ,20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91]
GAINS = [1,10,100]
UNITS = ["R", "K", "M"]
UNIT_GAIN = {"R":1, "K":1000, "M":1000000}
################## END ORDER CONFIG ##################################


def get_order_code(productNumber):
    '''
    Get Order information from manufacturer Part Number
    '''
    global API_LIMIT
    print(F"Check Product {productNumber}")
    # Generate Request with product number and maximum 10 entries. Market Place products are axcluded. 
    search_request = KeywordSearchRequest(keywords=productNumber.replace('.{2}',' '), record_count=20, exclude_market_place_products=True)
    # Place request on digikey webservice
    result = digikey.keyword_search(body=search_request, api_limits=API_LIMIT)
    # unfortunate manufacturer order code with 2-4 letters for resistance value and two digits for packaging in front need an extra verification step
    # to verify the correct resistance value. 
    pattern = re.compile(productNumber)
    # select results if packaging is CUT-Tape (CT) and minimum order quantity is 1
    orderable_parts = [(t.standard_pricing[-1].unit_price, t.manufacturer.value, t.manufacturer_part_number, t.digi_key_part_number,  t.primary_datasheet) 
        for t in result.products if t.packaging.value_id == '2' and t.minimum_order_quantity == 1 and pattern.match(t.manufacturer_part_number)]
    # Sord by price
    orderable_parts = sorted(orderable_parts, key=lambda a: a[0])
    print(F"Got Parts: {orderable_parts}") 
    return orderable_parts

def get_code(Prefix, value, unit):
    '''
    get resistance code for specific value
    '''
    value = value
    # R Notation
    first = floor(value/10)
    decimal = floor((value-first*10))
    if(decimal != 0):
        return F"{Prefix}{first}{unit}{decimal}"
    else:
        return F"{Prefix}{first}{unit}"
    


if __name__ == '__main__':
    with open('output_resistors.txt', 'w') as f:
        for unit in UNITS:
            for gain in GAINS:
                for e_value in E_LIST:
                    value =e_value*gain
                    unitvalue = get_code("", value, unit)
                    # Digikey can not search with only two letters -> L at the end is necessary so "1R" gets "1RL"
                    orderable_parts = get_order_code(get_code(BASE_ORDER_CODE, value, unit)+"L")
                    
                    if(len(orderable_parts) > 0):
                        f.write(F"{unitvalue}/{PACKAGE}	{unitvalue}/{PACKAGE}	RES SM {PACKAGE} {unitvalue} " + 
                        F"	GENERIC	{PACKAGE}	{unitvalue}	SCH/R_IEC.SchLib	R	PCB/SMT_CHIP.PcbLib	R{PACKAGE}-0.50-WW	{value*UNIT_GAIN[unit]*1e-1:.2}	" + 
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