import requests
from bs4 import BeautifulSoup
import json
import csv

#import pandas as pd
import itertools as it
import time
import random

#proxies = pd.read_csv('ProxyList.txt', header=None)
#proxies = proxies.values.tolist()
#proxies = list(it.chain.from_iterable(proxies))

#ua = UserAgent()
#proxy_pool = it.cycle(proxies)


def getDrugInfos(nid, protList, add_prot=True):
    name = 'DB' + str(nid).zfill(5)
    url = 'https://www.drugbank.ca/drugs/' + name

    #proxy = next(proxy_pool)
    response = requests.get(url) #,proxies={"http": proxy, "https": proxy}, headers={'User-Agent': ua.random}, timeout=5)

    if response.status_code == 200:
        time.sleep(random.randrange(1, 3))
        key = name
        prots = []
        infos = dict()

        soup = BeautifulSoup(response.text, 'html.parser')

        ldt1 = soup.find_all("dt", {"class": "col-md-2 col-sm-4"})
        ldd1 = soup.find_all("dd", {"class": "col-md-10 col-sm-8"})

        for k, d in enumerate(ldt1):
            td = d.get_text()
            if 'Name' in td:
                infos = {'Name': ldd1[k].get_text()}
                break

        targets = soup.find("div", {"class": "bond-list-container targets"})

        if targets is not None:
            bl = targets.find("div", {"class": "bond-list"})

            if bl is not None:
                bc = bl.find_all("div", {"class": "bond card"})

                for b in bc:
                    cb = b.find("div", {"class": "card-body"})
                    if cb is not None:
                        c1 = cb.find("div", {"class": "row"})

                        if c1 is not None:
                            c2 = c1.find("div", {"class": "col-sm-12 col-lg-7"})

                            ldt2 = c2.find_all("dt", {"class": "col-md-5 col-sm-6"})
                            ldd2 = c2.find_all("dd", {"class": "col-md-7 col-sm-6"})

                            if len(ldt2) > 0:
                                for k, d in enumerate(ldt2):
                                    td = d.get_text()
                                    if 'Uniprot ID' in td:
                                        prot = ldd2[k].get_text()
                                        if add_prot:
                                            protList.add(prot)
                                        prots.append(prot)

                                for k, d in enumerate(ldt2):
                                    td = d.get_text()
                                    if 'General Function' in td:
                                        infos['GF'] = ldd2[k].get_text()

                                    if 'Specific Function' in td:
                                        infos['SF'] = ldd2[k].get_text()

                                infos['UniprotID'] = prots

        if not add_prot:
            value_r = False
            for p in prots:
                if p in protList:
                    value_r = True
                    break
            if not value_r:
                return None

        return (key, infos)
    else:
        return None


def addDrug(mol_dictionary, l):
    if l is not None:
        k, i = l
        mol_dictionary[k] = i
        print('Add ', k)


def getCOVID19Drugs(drugs_fn, fn1, fn2):
    with open(drugs_fn, "r") as f:
        line = f.read()

    drugs = [int(x) for x in line.split(',')]

    print(drugs)

    mol_dictionary = dict()
    protList = set()

    for drug in drugs:
        l = getDrugInfos(drug, protList)
        addDrug(mol_dictionary, l)

    jf = json.dumps(mol_dictionary)
    f = open(fn1, "w")
    f.write(jf)
    f.close()

    jf = json.dumps(list(protList))
    f = open(fn2, "w")
    f.write(jf)
    f.close()

    return mol_dictionary, protList


def readJson(fn1, fn2):
    with open(fn1, 'r') as f:
        mol_dictionary = json.load(f)
    with open(fn2, 'r') as f:
        protList = json.load(f)
    return mol_dictionary, protList


def saveCSV():
    with open('drugs.csv', 'w') as f:
        f.write('# DrugAccessNumber,Name,UniprotID,General Function, Specific Function\n')
        for key in mol_dictionary.keys():
            v = mol_dictionary[key]
            name = v['Name']
            if 'UniprotID' in v:
                uid = v['UniprotID']
                #                gf=v['GF']
                #                sf=v['SF']
                #                f.write("%s,%s,%s,%s,%s\n" % (key,name,uid,gf,sf))
                f.write("%s,%s,%s\n" % (key, name, uid))
            else:
                print(key, 'has no Uniprot ID')


def saveQD(fn):
    with open(fn + '_p_qd.txt', 'w') as f:
        f.write('# Proteins\n')
        for key in mol_dictionary.keys():
            v = mol_dictionary[key]
            if 'UniprotID' in v:
                uids = v['UniprotID']
                for uid in uids:
                    f.write("%s " % (uid))
                f.write('\n')

    with open(fn + '_m_qd.txt', 'w') as f:
        f.write('# Proteins\n')
        for key in mol_dictionary.keys():
            v = mol_dictionary[key]
            if 'UniprotID' in v:
                name = v['Name']
                f.write("%s %s\n" % (key, name))


# mol_dictionary,protList=getCOVID19Drugs('covid19_drugs.txt','covid19_dict.json','covid19_proteins.txt')

mol_dictionary, protList = readJson('covid19_dict.json', 'covid19_proteins.txt')

print('COVID Proteins:', protList)

#TEST SUR 20000 MOLECULES
for drug in range(1, 20000):
    print('Testing', drug, '...')
    l = getDrugInfos(drug, protList, add_prot=False)
    addDrug(mol_dictionary, l)
    saveQD('drugs')
