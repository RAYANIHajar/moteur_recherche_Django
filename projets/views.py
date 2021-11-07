from django.http import HttpResponseRedirect
from django.shortcuts import render
from selenium import webdriver
from .forms import SearchForm
from django import forms
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import pymongo
import json


def scrap(x, source):
    # permet de taper le lien suivant "pubmed" dans l'anglet chrome
    driver = webdriver.Chrome("C:/Users/HP/Downloads/Compressed/chromedriver.exe")

    if source == 'PubMed':
        driver.get("https://pubmed.ncbi.nlm.nih.gov")

        search = driver.find_element(By.XPATH, "//input[@class='term-input tt-input']")
        search.send_keys(x)
        search.send_keys(Keys.RETURN)

        pmid = driver.find_elements(By.XPATH, "//span[@class='docsum-pmid']")
        title = driver.find_elements(By.XPATH, "//a[@class='docsum-title']")
        author = driver.find_elements(By.XPATH, "//span[@class='docsum-authors full-authors']")
        jornal = driver.find_elements(By.XPATH, "//span[@class='docsum-journal-citation full-journal-citation']")

        pmids = []
        titles = []
        authors = []
        jornals = []

        for i in range(len(pmid)):
            pmids.append(pmid[i].text)
            titles.append(title[i].text)
            authors.append(author[i].text)
            jornals.append(jornal[i].text)

        f = open("dataset.csv", "w")
        f.truncate()
        f.close()
        df = pd.DataFrame(
            {'PMIDS': pmids, 'Title': titles, 'Authors': authors, 'Sources': jornals})
        df.to_csv('dataset.csv', mode='a', header=True)

        df = pd.read_csv("dataset.csv")
        # df.head()

        data = df.to_dict(orient="records")
        print(data)

        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["Data_set"]
        # print(db) // test

        db.Articls.insert_many(data)
        driver.quit()
        return data
    elif source == 'IEEE':
        driver.get("https://www.ieee.org/")

        search = driver.find_element(By.XPATH, "//input[@class='required form-control']")
        search.send_keys(x)
        search.send_keys(Keys.RETURN)

        title = driver.find_elements(By.XPATH, "//div[@class='gsc-thumbnail-inside']")
        source = driver.find_elements(By.XPATH, "//div[@class='gsc-url-top']")
        abstruct = driver.find_elements(By.XPATH, "//div[@class='gsc-table-result']")

        titles = []
        sources = []
        abstructs = []

        for i in range(len(title)):
            titles.append(title[i].text)
            sources.append(source[i].text)
            abstructs.append(abstruct[i].text)

        f = open("madata.csv", "w")
        f.truncate()
        f.close()
        df = pd.DataFrame(
            {'Title': titles, 'Sources': sources, 'Abstructs': abstructs})
        df.to_csv('madata.csv', mode='a', header=True)

        df = pd.read_csv("madata.csv")
        # df.head()

        data = df.to_dict(orient="records")
        print(data)

        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["IEEEScraping"]

        db.Articls.insert_many(data)
        driver.quit()
        return data
    elif source == 'Scopus':
        driver.get(
            "https://www.scopus.com/results/results.uri?sort=plf-f&src=s&nlo=&nlr=&nls=&sid=3802d76f7669ce5599fa073617336601&sot=b&sdt=cl&cluster=scopubyr%2c%222021%22%2ct&sl=35&s=TITLE-ABS-KEY%28%22Big+data+analytics%22%29&origin=resultslist&zone=leftSideBar&editSaveSearch=&txGid=187fafe705c27e16fd860cc150cc9afd")

        search = driver.find_element(By.XPATH, "//input[@id='seachwithinresults']")
        search.send_keys(x)
        search.send_keys(Keys.RETURN)

        # y a un probléme ici(On ne peut pas acceder au site sans login et password !

        title = driver.find_elements(By.XPATH, "//td[@data-type='docTitle']")
        author = driver.find_elements(By.XPATH, "//span[@class='ddmAuthorList']")
        year = driver.find_elements(By.XPATH, "//span[@class='ddmPubYr']")
        source = driver.find_elements(By.XPATH, "//td[@data-type='source']")

        # print(len(title))
        # print(len(author))
        # print(len(year))
        # print(len(source))

        titles = []
        authors = []
        years = []
        sources = []

        for i in range(len(title)):
            titles.append(title[i].text)
            authors.append(author[i].text)
            years.append(year[i].text)
            sources.append(source[i].text)

        f = open("madataa.csv", "w")
        f.truncate()
        f.close()
        df = pd.DataFrame(
            {'Title': titles, 'Authors': authors, 'Years': years, 'Sources': sources})
        df.to_csv('madataa.csv', mode='a', header=True)

        df = pd.read_csv("madataa.csv")
        # df.head()

        data = df.to_dict(orient="records")
        print(data)

        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["ScopusScraping"]

        db.Articls.insert_many(data)
        driver.quit()
        return data


def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['search']
            source = form.cleaned_data['source']
            if not source:
                source = 'PubMed'
            result = scrap(value, source)
    else:
        result = {}

    return render(request, 'index.html', {"result": result})
