import numpy as np
import pandas as pd

mrp_name_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3}

outlet_name_mapping = {'OUT010': 0, 'OUT013': 1,'OUT017': 2,
                        'OUT018': 3,'OUT019': 4,'OUT027': 5,
                        'OUT035': 6,'OUT045': 7,'OUT046': 8,
                        'OUT049': 9}

outletType_name_mapping =  {'Grocery Store': 0,'Supermarket Type1': 1,
                            'Supermarket Type2': 2,'Supermarket Type3': 3}



def preprocess(json_data):
    MEAN_VISI = 0.07074283408443931
    mrp = float(json_data['mrp'])
    outlet_type = json_data['outlet_type']
    outlet = json_data['outlet']
    esta_years = int(json_data['esta_years'])
    visi = float(json_data['visi'])
    
    if mrp <=69: 
        mrp = 'a'
    elif mrp>69 and mrp<=137:
        mrp = 'b'
    elif mrp>137 and mrp<=203:
        mrp = 'c'
    else:
        mrp = 'd'
    if mrp in mrp_name_mapping.keys():
        mrp = mrp_name_mapping.get(mrp)
    if outlet_type in outletType_name_mapping.keys():
        outlet_type = outletType_name_mapping.get(outlet_type)
    else:
        print("invalid Outlet Type")
    if outlet in outlet_name_mapping.keys():
        outlet = outlet_name_mapping.get(outlet)
    esta_years = 2020 - esta_years
    visi = visi/MEAN_VISI
    data = pd.DataFrame({   'Outlet':[outlet],
                     'Outlet_Years':[esta_years],
                     'Outlet_Type':[outlet_type],
                     'Item_MRP':[mrp],
                     'Item_Visibility_MeanRatio':[visi]
                     })
    return data