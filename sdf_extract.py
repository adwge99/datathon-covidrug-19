# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 23:52:00 2020

@author: LAURI
"""


import requests


ext='.sdf'

ids={'DrugBank':0,'PubChem':1,'Zinc':2}
urls=['https://www.drugbank.ca/structures/small_molecule_drugs/','https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/','https://zinc15.docking.org/substances/']
params=[ext,'/record/SDF/?record_type=3d&response_type=display',ext]
out_path='D:\Projects\Research\Health\COVID-19\sdf/'


def loadFileFromSite(site_name,name):
    id_site=ids[site_name]
    param=params[id_site]
    file=urls[id_site]+name+param
    r = requests.get(file)
    out_file=out_path+name+ext
    open(out_file,'wb').write(r.content)
    print(out_file+' saved!!')


listDB=[11331]
listPC=[2244]
listZinc=[287718,12358883]

for e in listDB:
    loadFileFromSite('DrugBank','DB'+str(e))

for e in listPC:
    loadFileFromSite('PubChem',str(e))

for e in listZinc:
    loadFileFromSite('Zinc','ZINC'+str(e).zfill(12))
