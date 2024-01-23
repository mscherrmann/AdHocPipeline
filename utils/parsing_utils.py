# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 07:50:35 2021

@author: scherrmann
"""

import re
from bs4 import NavigableString
import hashlib
from bs4 import BeautifulSoup

def parse_ad_hoc(raw_html,file_name):
    # Function to parse html files of ad-hoc announcements from the Unternehmensregister.
    
    # File_name to int
    if isinstance(file_name, str):
        if ".html" in file_name:
            file_name = file_name.split(".")[0]
        file_name = int(file_name)
        
    
    # First of all, remove all html formatting elements
    for form in ["b","strong","i","em","mark","small","del","ins","sub","sup"]:
        raw_html=raw_html.replace("<"+form+">","")
        raw_html=raw_html.replace("</"+form+">","")
    
    # Initialize document dictionary
    doc={}
    doc["title_text"] = ""
    doc["date_text"] = ""
    doc["time_text"] = ""
    doc["source_text"] = ""
    doc["body_text"] = []
    doc["category"] = ""
    doc["hash"] = hashlib.md5(raw_html.encode()).hexdigest()
    doc["isin_all"] = "" # All isins that occur in the document
    doc["isin"] = "" # The isin of the company that is given in the respective table
    doc["wkn"] = ""
    doc["comp_name"] = ""
    doc["file_id"] = file_name
    doc["contains_name"] = False
    doc["subject"] = ""
    doc["comp_adress"] = ""
    doc["comp_mail"] = ""
    doc["comp_web_adress"] = ""
    doc["comp_exchanges"] = ""
    doc["language"] = ""
    
    doc_tree = BeautifulSoup(raw_html, "html.parser") #Create tree of whole document
    table_element = doc_tree.find(id='begin_pub') #Extract the tree of the table with id "begin_pub"
    doc_text = table_element.get_text()
    table = table_element.find('table')
    
    # Parse all isins in the document
    doc["isin_all"]=list(set([x.group() for x in re.finditer(r'(AT|CA|CH|CN|DE|DK|FI|FR|GB|IL|LU|MT|NL|SE|US|XC|XF|XS)\w{9}\d',re.sub(r'\s{2,}', " ", doc_text))]))
    if len(doc["isin_all"])==1:
        doc["isin_all"]=doc["isin_all"][0]
    
    # Parse general information
    if not table:
          doc["body_text"]=extract_strings(table_element)
          doc["body_text"]=[x for x in doc["body_text"] if x!="\xa0" and x!=""]
          pattern = re.compile("\d{1,2}\.\d{1,2}\.\d{4}")
          doc["date_text"]=pattern.search(doc_text).group(0)
          return doc
    table_element=table.find("tbody")
    table_element=table_element.find_all("tr")
    for i in range(len(table_element)):
        row=table_element[i]
        cols=row.find_all("p")
        if len(cols)<2:
            continue
        keyword=re.sub(r'\s{2,}', " ", cols[0].get_text()).strip()
        if keyword=="Betreff:":
            doc["subject"] = re.sub(r'\s{2,}', " ", cols[1].string)
        elif keyword=="Schlagworte:":
            doc["category"]=[x.strip().lower() for x in re.sub(r'\s{2,}', " ", cols[1].string).split("/")]
            doc["category"]=list(set(doc["category"]))
            if len(doc["category"])==1:
                doc["category"]=doc["category"][0]
        elif keyword=="Ergänzende Angaben:":
            doc["title_text"]=re.sub(r'\s{2,}', " ", cols[1].string)
            
    # Parse "Angaben zum Inhalt"
    table=table.find_next_sibling('table')
    table_element=table.find("tbody")
    table_element=table_element.find("tr")
    table_element=table_element.find_all("td")
    table_element=table_element[1]
    for tab in table_element.select('table'): #Remove table elements
        tab.extract()
    doc["body_text"]=extract_strings(table_element)
    
    doc["body_text"]=[x for x in doc["body_text"] if x!="\xa0" and x!=""]
    
    # Parse "Angaben zum Emittenten"
    table=table.find_next_sibling('table')
    table_element=table.find("tbody")
    table_element=table_element.find_all("tr")
    for i in range(len(table_element)):
        row=table_element[i]
        cols=row.find_all("p")
        if len(cols)<2:
            continue
        keyword=re.sub(r'\s{2,}', " ", cols[0].get_text()).strip()
        if keyword=="Name:":
            doc["comp_name"] = re.sub(r'\s{2,}', " ", cols[1].string)
        elif keyword=="Adresse:":
            doc["comp_adress"]=re.sub(r'\s{2,}', " ", cols[1].string)
        elif keyword=="E-Mail-Adresse:":
            doc["comp_mail"]=re.sub(r'\s{2,}', " ", cols[1].string)
        elif keyword=="Internet-Adresse::":
            doc["comp_web_adress"]=re.sub(r'\s{2,}', " ", cols[1].string)
        elif keyword=="ISIN:":
            doc["isin"]=list(set([x.group() for x in re.finditer(r'(AT|CA|CH|CN|DE|DK|FI|FR|GB|IL|LU|MT|NL|SE|US|XC|XF|XS)\w{9}\d',re.sub(r'\s{2,}', " ", cols[1].string))]))
            if len(doc["isin"])==1:
                doc["isin"]=doc["isin"][0]
        elif keyword=="WKN:":
            doc["wkn"]=list(set(re.sub(r'\s{2,}', " ", cols[1].string)))
        elif keyword=="Handelsplätze:":
            doc["comp_exchanges"]=re.sub(r'\s{2,}', " ", cols[1].string)
            
    # Parse "Angaben zur Pflichtmitteilung"
    table=table.find_next_sibling('table')
    table_element=table.find("tbody")
    table_element=table_element.find_all("tr")
    for i in range(len(table_element)):
        row=table_element[i]
        cols=row.find_all("p")
        if len(cols)<2:
            continue
        keyword=re.sub(r'\s{2,}', " ", cols[0].get_text()).strip()
        if keyword=="Veröffentlichung in elektronisch betriebenen Informationsverbreitungssystem:":
            doc["source_text"] = re.sub(r'\s{2,}', " ", cols[1].string)
        if keyword=="Pflichtveröffentlichung am:":
            doc["date_text"] = re.sub(r'\s{2,}', " ", cols[1].string)
        if keyword=="Uhrzeit der Veröffentlichung:":
            doc["time_text"] = re.sub(r'\s{2,}', " ", cols[1].string)
        if keyword=="Pflichtveröffentlichung in/über:" and  doc["source_text"]=="":
            doc["source_text"] = re.sub(r'\s{2,}', " ", cols[1].string)
        if keyword=="Sprachen der Veröffentlichung:":
            doc["language"] = re.sub(r'\s{2,}', " ", cols[1].string)
            if doc["language"] == "Deutsch":
                doc["language"] = "de"
            elif doc["language"] == "English":
                doc["language"] == "en"
            
    doc["contains_name"]=any(doc["comp_name"] in paragraph for paragraph in doc["body_text"])
    if doc["title_text"]=="":
        doc["title_text"]=doc["body_text"][0]    
            
    return doc

def extract_strings(soup):
    # This function extacts all strings (NavigableString) in a html tag, no matter how many child this tag might have, separated in a list.
    strings=[]
    if soup.contents:
        for child  in soup.contents:
            if isinstance(child,NavigableString):
                strings.append(re.sub(r'\s{2,}', " ",child.string.strip()))
            else:
                strings=strings+ extract_strings(child)
    return strings

def extract_strings_and_split_at_double_line_break(soup):
    # This function extacts all strings (NavigableString) in a html tag, no matter how many child this tag might have, separated in a list.
    strings=[]
    if soup.contents:
        for child  in soup.contents:
            if isinstance(child,NavigableString):
                parts = re.split('\r?\n\r?\n', child.string.strip())
                strings=strings+[re.sub(r'\s{2,}', " ",x) for x in parts]
            else:
                strings=strings+ extract_strings_and_split_at_double_line_break(child)
    return strings

