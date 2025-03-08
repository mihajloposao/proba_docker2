from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB

def prepoznavanje_naziva(ociscen_naziv):
    engine = create_engine("sqlite:///prepoznavanje_imena.db", echo=True)
    Base = declarative_base()

    class Nazivi(Base):
        __tablename__ = 'nazivi'
        id = Column(Integer, primary_key=True, autoincrement=True)  # Automatski se povećava
        originalni_naziv = Column(String)
        moj_naziv = Column(String)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    nazivi = session.query(Nazivi).all()
    X = []
    Y = []
    for naziv in nazivi:
        X.append(naziv.originalni_naziv)
        Y.append(naziv.moj_naziv)
    # Pravljenje bag-of-words modela za namirnice
    cv = CountVectorizer()
    X = cv.fit_transform(X).toarray()
    # Treniranje modela za prepoznavanje namirnica
    gnb = GaussianNB()
    gnb.fit(X, Y)
    return gnb.predict(cv.transform([ociscen_naziv]).toarray())
def obrada_naziva(naziv):
    # Brisanje nepotrebnih znakova i prebacivanje u lower case
    za_unos = str(naziv).lower()
    # Brisanje svih karaktera koji nisu slova
    za_unos = "".join([i if i.isalpha() else " " for i in za_unos])
    # Brisanje svih reci gracih od dva slova
    za_unos = "".join([i + " " for i in za_unos.split(" ") if len(i) > 2])
    # Brisanje reci kom i maxi
    za_unos = za_unos.replace("kom", "").replace("maxi", "").strip()
    return za_unos
def web_scraping(qr):
    Base = declarative_base()
    engine = create_engine('sqlite:///za_rutine.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    class Proizvodi(Base):
        __tablename__ = 'proizvodi'
        id = Column(Integer, primary_key=True, autoincrement=True)  # Automatski se povećava
        datumb = Column(String)
        proizvodb = Column(String)
    Base.metadata.create_all(engine)
    link = qr
    #Pravim options da bi radio na serveru
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    driver.maximize_window()
    # Pronalazenje datuma i naziva radnje
    if driver.current_url == "data:,":
        driver.quit()
    else:
        datum = driver.find_element(By.ID, 'sdcDateTimeLabel').text.split(" ")[0].replace(".", "/", 2).replace(".", "")
        # Funkcija za cekanje kako bi se ucitao ceo html do poziva
        time.sleep(0.5)
        # Klik na dugme za rasirivanje tabele sa proizvodima
        klik = driver.find_element(By.XPATH, "/html/body/div/div/form/div[3]/div/div/div[1]/h5/a")
        klik.click()
        time.sleep(0.5)
        # Uzimanje svih proizvoda iz tabele
        proizvodi = driver.find_element(By.XPATH, '//*[@id="collapse-specs"]/div/div/table/tbody[2]').find_elements(
            By.TAG_NAME, "tr")
        # Prolazak kroz sve proizvode i nalazenje njihovog naziva, cene i kolicine
        for i in proizvodi:
            pojedninacno = i.find_elements(By.TAG_NAME, "td")
            naziv = prepoznavanje_naziva(obrada_naziva(pojedninacno[0].text))[0]
            novi_proizvod = Proizvodi(datumb=datum,proizvodb = naziv)
            session.add(novi_proizvod)
            session.commit()
        session.close()
        driver.quit()

def csv_u_bazu():
    Base = declarative_base()
    engine = create_engine('sqlite:///.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    df = pd.read_csv("")
    vrednosti = df.iloc[:].values

    class Proizvodi(Base):
        __tablename__ = 'proizvodi'
        id = Column(Integer, primary_key=True, autoincrement=True)  # Automatski se povećava
        datumb = Column(String)
        proizvodb = Column(String)
    Base.metadata.create_all(engine)
    for red in vrednosti:
        novi_sample = Proizvodi(datumb=red[0], proizvodb=red[2])
        session.add(novi_sample)
        session.commit()
    session.close()

def proba():
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