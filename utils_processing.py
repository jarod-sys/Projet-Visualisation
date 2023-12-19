import sys
sys.path.append("../")


import json
import string
import requests

import http.client as httplib
from urllib.parse import urlparse

import numpy as np
import seaborn as sb
import pandas as pd

from geopy.point import Point
from geopy.geocoders import Nominatim
from sklearn import  preprocessing
from datetime import datetime, date,time,timedelta

import matplotlib.pyplot as plt
from typing import Dict,List,Any


def convert_float_to_str(number:Any=None)->str:
    if type(number)==float or type(number)==int:
        chaine=str(number)
    elif type(number)==str:
        chaine=number
    else:
        raise NotImplemented
    return chaine


def dfFloat_to_dfStr(df:Any=None)->pd.DataFrame:
    for col in list(df.columns):
        df[col]=df[col].apply(convert_float_to_str)
    return df




# 'pdf_directory2014.01.04-Riano.pdf '
class FillgeoLoc(object):
    def __init__(self, *vargs):
        self.__Data_geoLocation: pd.DataFrame

    def build_json(self, name_file):
        # Load Data
        with open(f"data/{name_file}.json", encoding="utf8") as f:
            data = json.load(f)
        self.__Data_geoLocation = pd.DataFrame(data)

    # Removing Punctuation from Column Contents
    def remove_punctuation(self, x):
        exclude = set(string.punctuation)
        try:
            x = ''.join(ch for ch in x if ch not in exclude)
        except:
            pass
        return x

    def describe(self, name: str):
        print(self.__Data_geoLocation[name].describe())

    def remove_whitespace(self, x):
        try:
            x = ''.join(x.split())
        except:
            pass
        return x

    def convert_string_in_int(self, chaine: str):
        return int(chaine)

    def fill_geoLocation(self, Data_geoLocation: pd.DataFrame):
        location_agent = Nominatim(user_agent="GetLoc")
        for i in range(len(Data_geoLocation)):
            if (str(Data_geoLocation.latitude[i]).upper() == 'NAN') or (
                    str(Data_geoLocation.longitude[i]).upper() == 'NAN') or (str(Data_geoLocation.longitude[i]) == ''):
                # entering the location name
                print(f"->{i}: {Data_geoLocation.Location[i]}")
                # getting latitude and longitude
                try:
                    geoLoc = location_agent.geocode(Data_geoLocation.Location[i])
                    print(f"geoloc:{geoLoc.latitude},{geoLoc.longitude}")
                    Data_geoLocation.loc[i, "latitude"] = geoLoc.latitude
                    Data_geoLocation.loc[i, "longitude"] = geoLoc.longitude
                except:
                    Data_geoLocation.loc[i, "latitude"] = "Missing"
                    Data_geoLocation.loc[i, "longitude"] = "Missing"
                    print(f"Not find geoloc\n")
                    pass

            else:
                continue
        return Data_geoLocation

    def fill_Location(self, Data_geoLocation: pd.DataFrame):
        location_agent = Nominatim(user_agent="GetLoc")
        for i in range(len(Data_geoLocation)):
            if (Data_geoLocation.Location[i].isspace()) or (str(Data_geoLocation.Location[i]).upper() == 'NAN') or (
                    Data_geoLocation.Location[i] == ''):
                print(f"{i}: Data_geoLocation {Data_geoLocation.Location[i]}")
                try:
                    # passing the coordinates
                    point = Point(Data_geoLocation.latitude[i], Data_geoLocation.longitude[i])
                    geoname = location_agent.reverse(point)
                    if geoname is not None:
                        print(f"adress:{geoname.address}\n")
                        Data_geoLocation.loc[i, "Location"] = geoname.address
                    else:
                        Data_geoLocation.loc[i, "Location"] = "Missing"
                        print(f"Not find adress\n")
                        pass
                except:
                    pass
            else:
                continue
        return Data_geoLocation

    @property
    def Data_geoLocation(self):
        return self.__Data_geoLocation

    @Data_geoLocation.setter
    def Data_geoLocation(self, df: pd.DataFrame):
        self.__Data_geoLocation = df
