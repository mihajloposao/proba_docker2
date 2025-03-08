import pandas as pd
from datetime import datetime
from collections import Counter
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ucitavanje ociscenih svih podataka i uzimanje u X samo imena namirnice i datuma kupovina
engine = create_engine("sqlite:///za_rutine.db", echo=True)
Base = declarative_base()

class Proizvodi(Base):
    __tablename__ = 'proizvodi'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Automatski se povećava
    datumb = Column(String)
    proizvodb = Column(String)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
proizvodi = session.query(Proizvodi).all()
X = []
for proizvod in proizvodi:
    X.append([proizvod.datumb,proizvod.proizvodb])
# Pravljenje dicta u kom su za svaku namirnicu svi datumi kupovina
namirnice_datumi_dict = {}

for red in X:
    datum = red[0]
    namirnica = red[1]
    if namirnica not in namirnice_datumi_dict:
        namirnice_datumi_dict[namirnica] = [datum]
    elif datum not in namirnice_datumi_dict[namirnica]:
        namirnice_datumi_dict[namirnica].append(datum)

# Sortiranje datuma da idu u rastucem redosledu
for namirnica in namirnice_datumi_dict:
    for i in range(len(namirnice_datumi_dict[namirnica])-1):
        for j in range(i+1,len(namirnice_datumi_dict[namirnica])):
            datum1=datetime.strptime(namirnice_datumi_dict[namirnica][i],"%d/%m/%Y")
            datum2 = datetime.strptime(namirnice_datumi_dict[namirnica][j], "%d/%m/%Y")
            if datum1>datum2:
                temp = namirnice_datumi_dict[namirnica][i]
                namirnice_datumi_dict[namirnica][i] = namirnice_datumi_dict[namirnica][j]
                namirnice_datumi_dict[namirnica][j] = temp

# Rastojanja izmedju dve kupovine
namirnice_rastojanja_dict = {}

for namirnica in namirnice_datumi_dict:
    for i in range(len(namirnice_datumi_dict[namirnica])-1):
        datum1 = datetime.strptime(namirnice_datumi_dict[namirnica][i], "%d/%m/%Y")
        datum2 = datetime.strptime(namirnice_datumi_dict[namirnica][i+1], "%d/%m/%Y")
        razlika = datum2-datum1
        if namirnica not in namirnice_rastojanja_dict:
            namirnice_rastojanja_dict[namirnica]=[razlika.days]
        else:
            namirnice_rastojanja_dict[namirnica].append(razlika.days)

# Izracunavanje najverovatnijeg rastojanja do sledece kupovine
namirnice_ocekivano_rastojanje_dict = {}

for namirnica in namirnice_rastojanja_dict:
    verovatnoce_ponavljanja_dict = Counter(namirnice_rastojanja_dict[namirnica])
    for i in verovatnoce_ponavljanja_dict:
        verovatnoce_ponavljanja_dict[i] = verovatnoce_ponavljanja_dict[i]/len(namirnice_rastojanja_dict[namirnica])
    namirnice_ocekivano_rastojanje_dict[namirnica]=0
    for i in verovatnoce_ponavljanja_dict:
        namirnice_ocekivano_rastojanje_dict[namirnica]+=i*verovatnoce_ponavljanja_dict[i]
    namirnice_ocekivano_rastojanje_dict[namirnica] = round(namirnice_ocekivano_rastojanje_dict[namirnica])

# Izracunavanje verovatnoce na osnovu dana

def sortiranje_po_danima(namirnice_datumi_dict):
    namirnice_po_danima_dict = {}

    for namirnica in namirnice_datumi_dict:
        for datum in namirnice_datumi_dict[namirnica]:
            dan = datetime.strptime(datum, "%d/%m/%Y").strftime("%A")
            if namirnica not in namirnice_po_danima_dict:
                namirnice_po_danima_dict[namirnica] = [dan]
            else:
                namirnice_po_danima_dict[namirnica].append(dan)
        namirnice_po_danima_dict[namirnica] = dict(Counter(namirnice_po_danima_dict[namirnica]))
    return namirnice_po_danima_dict

def sortiranje_po_klasama(namirnice_po_danima_dict):
    namirnice_po_klasama = {}
    for namirnica in namirnice_po_danima_dict:
        namirnice_po_klasama[namirnica] = {}
        for dan in namirnice_po_danima_dict[namirnica]:
            vrednost = namirnice_po_danima_dict[namirnica][dan]
            if vrednost not in namirnice_po_klasama[namirnica]:
                namirnice_po_klasama[namirnica][vrednost]=[dan]
            else:
                namirnice_po_klasama[namirnica][vrednost].append(dan)
    return namirnice_po_klasama

def verovatnoca(namirnice_po_klasama_dict):
    namirnice_verovatnoca_po_danu = {}
    for namirnica in namirnice_po_klasama_dict:
        namirnice_verovatnoca_po_danu[namirnica] = {}
        for prolaz1 in namirnice_po_klasama_dict[namirnica]:
            br = 0
            for prolaz2 in namirnice_po_klasama_dict[namirnica]:
                if prolaz1>=prolaz2:
                    br+=1
            for dan in namirnice_po_klasama_dict[namirnica][prolaz1]:
                namirnice_verovatnoca_po_danu[namirnica][dan] = round(br/ len(namirnice_po_klasama_dict[namirnica]),3   )
    return namirnice_verovatnoca_po_danu

verovatnoca_po_danu_dict={}
def verovatnoca_po_danu(namirnice_datumi_dict):
    namirnice_po_danima_dict = sortiranje_po_danima(namirnice_datumi_dict)
    namirnice_po_klasama_dict = sortiranje_po_klasama(namirnice_po_danima_dict)
    return verovatnoca(namirnice_po_klasama_dict)

verovatnoca_po_danu_dict = verovatnoca_po_danu(namirnice_datumi_dict)

def lista_preporucenih():
    lista_preporuka = []
    datum_sad = datetime.now()
    ime_dana_sad = datum_sad.strftime("%A")
    for namirnica in namirnice_rastojanja_dict:
        poslednja_kupovina = datetime.strptime(namirnice_datumi_dict[namirnica][-1], "%d/%m/%Y")
        prolteklo_vreme = datum_sad-poslednja_kupovina
        prolteklo_vreme = prolteklo_vreme.days
        if ime_dana_sad in verovatnoca_po_danu_dict[namirnica]:
            verovatnoca = (prolteklo_vreme/namirnice_ocekivano_rastojanje_dict[namirnica])*verovatnoca_po_danu_dict[namirnica][ime_dana_sad]
            verovatnoca = round(verovatnoca,3)
            if verovatnoca>=0.5:
                lista_preporuka.append(namirnica)
    return lista_preporuka

