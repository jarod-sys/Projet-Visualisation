import sys
sys.path.append("../")



#import streamlit
import json
import string
#import pycountry
import requests
from requests.exceptions import ConnectionError,HTTPError

import http.client as httplib
from urllib.parse import urlparse

import numpy as np
import seaborn as sb
import pandas as pd

from geopy.point import Point
from geopy.geocoders import Nominatim
from sklearn import  preprocessing
from datetime import datetime, date,time,timedelta

import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict,List,Any,Tuple


def extract_period_from_time(time:pd.Series, year_min,year_max, month_min,month_max, day_min,day_max, hour_min,hour_max):
    mask:List=list()
    times:List=list()
    for i in range(len(time)):
        mask.append((year_min<=time.loc[i].year<=year_max) & (month_min<=time.loc[i].month<=month_max) &
                   (day_min<=time.loc[i].day<=day_max) & (hour_min<=time.loc[i].hour<=hour_max))
        if mask[i]:times.append(time.loc[i].time().strftime("%H:%M:%S"))
    return mask,times

def convert_str_to_float(chaine:str=None)->int:
    if type(chaine)==str:
        if chaine=="Missing" or chaine=="Missing":
            x=-1
        else:
            x=float(chaine)
    else:
        x=chaine
    return x

def remove_whitespace(x):
    try:
        x = ''.join(x.split())
    except:
        pass
    return x

def fill_missing_value(data=None):
    for col in list(data.columns):
        data=find_missing_values_per_attribut(data=data,attribut=col)
    data.describe()
    return data

def find_missing_values_per_attribut(data=None,attribut=None):
    df=data.copy()
    variable=data[attribut].values.tolist()
    columns=['Country', 'Area', 'Location','Activity','Injury','Species','Date']
    if attribut in columns:
        pass
    else:
        df[attribut]=df[attribut].apply(remove_whitespace)
    for v,value in enumerate(df[attribut]):
        if value=='' or value==' 'or value=='  'or value=='   ' or value=='unknown' or value=='UNKNOWN':
            df.loc[v,attribut]="Missing"
    return df


def filter_Area(data:pd.DataFrame,*args)->pd.DataFrame:
    df=data.copy()
    for v,value in enumerate(df.Area):
        if value=='' or value==' ':
            df.Area.loc[v]="unknown_Area"
    return df

def filter_Country(data:pd.DataFrame,*args)->pd.DataFrame:
    df=data.copy()
    for v,value in enumerate(df.Country):
        if value=='' or value==' ':
            df.Country.loc[v]="unknown_Country"
    return df

def filter_Location(data:pd.DataFrame,*args)->pd.DataFrame:
    df=data.copy()
    for v,value in enumerate(df.Location):
        if value=='' or value==' ':
            df.Location.loc[v]="unknown_Location"
    return df

def filter_jour(data:pd.DataFrame,*args)->pd.Series:
    jour=[]
    for value in data.Date:
        if value!="Missing":
            data0=''.join(value.replace("Reported","").split())
            if data0.find("-")==-1:
                #print(data0)
                jour.append("Missing")
            else:
                data1=data0.split("-")
                if len(data1[0])>2:
                    #print(data1[0])
                    jour.append("Missing")
                else:
                    #print(data1[0])
                    jour.append(str(int(data1[0])))
        else:
            jour.append(value)

    print(len(jour))
    return pd.Series(jour)


def filter_month(data:pd.DataFrame,*args)->pd.Series:
    months={'Jan':1,'Feb':2,'Mar':3,'Apr':4,
            'May':5,'Jun':6,'Jul':7,'Aug':8,
            'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    month=[]
    count=0
    for v,value in enumerate(data.Date):
        if value!="Missing":
            for key in months.keys():
                if value.find(key)!=-1:
                    month.append(key)
                    count+=1
                    break
            if count:
                count=0
            else:
                month.append("Missing")
        else:
            month.append(value)

    print(len(month))
    return pd.Series(month)


def filter_year(data: pd.DataFrame, *args) -> pd.Series:
    annee = []
    count = 0
    YEARS = range(1000, 2022)
    for v, value in enumerate(data.Date):
        if value != "Missing":
            # print(f"date:{value}->")
            for year in YEARS:
                if value.find(f"{year}") != -1:
                    # print(f"year:{year}\n")
                    annee.append(str(int(year)))
                    count += 1
                    break
            if count:
                count = 0
            else:
                # print(f"value:{value}\n")
                for year in YEARS:
                    if data.Year.loc[v].find(f"{year}") != -1:
                        # print(f"year:{year}\n")
                        annee.append(str(int(year)))
                        count += 1
                        break
                if count:
                    count = 0
                else:
                    annee.append("Missing")
        else:
            annee.append(value)

    print(len(annee))
    return pd.Series(annee)


def filter_sex(data:pd.DataFrame,*args)->pd.Series:
    new_SexSeries:List[str]=list()
    for v,value in enumerate(data.Sex):
        if value!="Missing":
            if value.upper()=="M" :
                new_SexSeries.append("Male")
            elif value.upper()=="F":
                new_SexSeries.append("Female")
            else:
                 new_SexSeries.append("Missing")
        else:
              new_SexSeries.append("Missing")
    print(len(new_SexSeries))
    return pd.Series(new_SexSeries)


def filter_fatal(data:pd.DataFrame,*args)->pd.Series:
    new_fatalSeries:List[str]=list()
    for v,value in enumerate(data.fatal):
        if value!="Missing":
            if value.upper()=="N" :
                new_fatalSeries.append("Alive")
            elif value.upper()=="Y":
                new_fatalSeries.append("Dead")
            else:
                 new_fatalSeries.append("Missing")
        else:
              new_fatalSeries.append("Missing")
    print(len(new_fatalSeries))
    return pd.Series(new_fatalSeries)

def filter_Age(data:pd.DataFrame,*args)->pd.Series:
    AGES=range(10,100)
    count=0
    ages=[]
    for value in data.Age:
        if value!="Missing":
            if len(value)>=2:
                for age in AGES:
                    if value.find(f"{age}")!=-1:
                        #print(value)
                        ages.append(str(int(age)))
                        count+=1
                        break
                if count:
                    count=0
                else:
                    #print(value)
                    ages.append("Missing")
            else:
                if value!="X" and value!="F" and value!='':
                    #print(value)
                    ages.append(str(int(value)))
                else:
                    ages.append("Missing")

        else:
            ages.append(value)
    print(len(ages))
    return pd.Series(ages)

def filter_typeAttack(data:pd.DataFrame,*args)->pd.DataFrame:
    df=data
    df.Type=df.Type.apply(remove_whitespace)
    for v,value in enumerate(df.Type):
        if value=='' or value=='\n':
            df.Type.loc[v]="unknown_type"
    return df

def remove_missing_Time(data:pd.DataFrame,*args)->pd.DataFrame:
    count:int=0
    for time in data.Time:
        if time=='' or time=='   ' or time==' 'or time=='  ':
            data=data.drop(index=count)
        count+=1
    data=data.reset_index(drop=True)
    return data


def get_second_from_format_hms(timeSeries: pd.Series):
    def oder_format(time_in_second: Dict):
        formats: Dict = {"Format": [value for value in time_in_second.values() if type(value) == str],
                         "Count": [1 for value in time_in_second.values() if type(value) == str]}
        return pd.DataFrame(formats).groupby(by="Format").sum()

    new_timeSeries: List[str] = list()
    count: int = 0
    time_in_second: Dict[int, Any] = dict()
    for time in timeSeries:
        if type(time)==str and time.find('h') != -1:
            try:
                if len(time) != 4:
                    indice = time.find('h')
                    # print(f"Time brut:{time}\n")
                    # print(f"Heure:{time[indice-2:indice]}, minute:{time[indice+1:indice+2]}\n")
                    second = (int(time[indice - 2:indice]) * 60 * 60) + (int(time[indice + 1:indice + 3]) * 60)
                    time_in_second[count] = second
                    new_timeSeries.append(time[indice - 2:indice + 3])
                else:
                    times = "0" + f"{time}"
                    indice = times.find('h')
                    # print(f"Time brut:{times}\n")
                    # print(f"Heure:{times[indice-2:indice]}, minute:{times[indice+1:indice+2]}\n")
                    second = (int(times[indice - 2:indice]) * 60 * 60) + (int(times[indice + 1:indice + 3]) * 60)
                    time_in_second[count] = second
                    new_timeSeries.append(time[indice - 2:indice + 3])
            except ValueError:
                time_in_second[count] = time
                new_timeSeries.append("Missing")
        else:
            time_in_second[count] = time
            if time == "Missing":
                new_timeSeries.append(time)
            else:
                new_timeSeries.append("Missing")
        count += 1

    return pd.Series(new_timeSeries), time_in_second, oder_format(time_in_second)


def get_hours(Month: pd.Series, Year: pd.Series, Day: pd.Series, Time_in_second: Dict[int, Any]) -> pd.Series:
    months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
              'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
              'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    heure: Dict[int, Any] = dict()

    for v, second in Time_in_second.items():
        if second != "Missing":
            if type(second) == int:

                try:
                    # print(f"Year:{int(Year.iloc[v])}\n")
                    # print(f"Month:{months.get(Month.iloc[v])}\n")
                    # print(f"Day:{int(Day.iloc[v])}\n")
                    heure[v] = datetime(year=int(Year.iloc[v]), month=months.get(Month.iloc[v]),
                                        day=int(Day.iloc[v])) + timedelta(seconds=second)
                except:
                    heure[v] = timedelta(seconds=second)

            else:
                heure[v] = "Missing"
        else:
            heure[v] = "Missing"
    print(len(heure))
    return pd.Series(heure)


def filter_tyte_TimeStamp(data:pd.DataFrame,*args)->pd.DataFrame:
    count:int=0
    for time in data.Hours:
        if  type(time)!=datetime:
            data=data.drop(index=count)
        count+=1
    data=data.reset_index(drop=True)
    return data

def generate_data(name_file=None):
    with open(f'{name_file}.json', encoding='utf8') as f:
        data = pd.DataFrame(json.load(f)).copy()
        data=data.fillna("unknown")
        data["fatal"]=data["Fatal(Y/N)"]
        data=data.drop(columns=["Fatal(Y/N)"])
        columns=data.columns
        print(columns)
    return data
