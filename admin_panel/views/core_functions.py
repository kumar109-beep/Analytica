from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render
from rolepermissions.checkers import has_permission
import json
import base64
import numpy as np
from django.shortcuts import render
import pandas as pd
import pyarrow.feather as feather
import pyarrow as pa
import pyarrow.feather as pf
import datetime
import numpy as np
import math
# from django.contrib.staticfiles.templatetags.staticfiles import static
from django.templatetags.static import static

import os
from django.conf import settings

import datetime
import re

import requests

from io import BytesIO
from zipfile import ZipFile

from .helper_methods import *

from dhis2 import Api

from pprint import pprint

from dateutil import relativedelta

SESSION_DATE    = ""
SESSION_MONTH   = ""
FRAME_NAME      = ""

# frame_source = {"asha"                          : {"url" : "http://nhm-bcpm.in/mapping/master_data.zip", "key" : "master"}, 
#                 "sangini"                       : {"url" : "http://nhm-bcpm.in/mapping/master_data_sangini.zip", "key" : "master"},
#                 "anm"                           : {"url" : "http://nhm-bcpm.in/mapping/master_data_anm.zip", "key" : "master"},
#                 "asha_payment"                  : {"url" : "http://nhm-bcpm.in/nhm/cron_json/2019-%d-incentive_jsonData.zip", "key" : "incentive"},
#                 "asha_payment_status"           : {"url" : "http://nhm-bcpm.in/nhm/cron_json/2019-%d-incentive_status.zip", "key" : "incentive"},
#                 "sangini_payment"               : {"url" : "http://nhm-bcpm.in/nhm/cron_json/2019-%d-incentive_jsonSangini.zip", "key" : "incentive"},
#                 "sangini_payment_status"        : {"url" : "http://nhm-bcpm.in/nhm/cron_json/2019-%d-sangini_status.zip", "key" : "incentive"},
#                 }

frame_source = {"asha"                          : {"url" : "http://nhm-bcpm.in/mapping/master_data.zip", "key" : "master"}, 
                "sangini"                       : {"url" : "http://nhm-bcpm.in/mapping/master_data_sangini.zip", "key" : "master"},
                "anm"                           : {"url" : "http://nhm-bcpm.in/mapping/master_data_anm.zip", "key" : "master"},
                "asha_payment"                  : {"url" : "http://nhm-bcpm.in/nhm/cron_json/%d-%d-incentive_jsonData.zip", "key" : "incentive"},
                "asha_payment_status"           : {"url" : "http://nhm-bcpm.in/nhm/cron_json/%d-%d-incentive_status.zip", "key" : "incentive"},
                "sangini_payment"               : {"url" : "http://nhm-bcpm.in/nhm/cron_json/%d-%d-incentive_jsonSangini2.zip", "key" : "incentive"},
                "sangini_payment_status"        : {"url" : "http://nhm-bcpm.in/nhm/cron_json/%d-%d-sangini_status.zip", "key" : "incentive"},
                "cho"                           : {"url" : "https://nhm-bcpm.in/cho/cron_json/master_data_cho.zip","key":"master"}
                }
                #CHO Frame added on 30/06/2021
####
## https://nhm-bcpm.in/cho/cron_json/master_data_cho.json
MY_PROGRAMS = []
def download_frame_file(request):
    pass

# calculate Last day of month
def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)

def payment_dataframe(selected_session, url=None):
    global SESSION_DATE
    global SESSION_MONTH
    try:
        SESSION_DATE = datetime.datetime.strptime(selected_session, '%B-%Y')
        SESSION_MONTH = SESSION_DATE.month
    except:
        SESSION_DATE = datetime.date.today()
        if(SESSION_DATE.day > 15):
            SESSION_MONTH = SESSION_DATE.month
        else:
            SESSION_MONTH = SESSION_DATE.month - 1    
        selected_session = datetime.date(SESSION_DATE.year, SESSION_MONTH, 1).strftime("%B-%Y")

    if url:
        url = url %(SESSION_DATE.year, SESSION_MONTH)
    return({"url":url, "selected_session":selected_session})

def NHM_Generation(request, frame_name):
    global FRAME_NAME
    FRAME_NAME = frame_name
    data = ""
    url = frame_source[frame_name]["url"]
    if("_payment" in frame_name):
        session = request.GET.get("session", False)
        response_data = payment_dataframe(session, url)
        url             = response_data["url"]
        save_frame_as   = response_data["selected_session"]
        save_frame_as = frame_name + "_" + save_frame_as
        pass #"S"*50)
        pass #url, save_frame_as)
        pass #"S"*50)
    else:
        save_frame_as = frame_name
    response = requests.get(url)
    # data = dd.read_json(url, compression='zip')
    # pass #data)
    if(response.status_code == 200):
        zipfile = ZipFile(BytesIO(response.content))
        zipfile.namelist()
        for filename in zipfile.namelist():  
            pass #filename)  
            with zipfile.open(filename) as f:  
                data = f.read()  
                data = json.loads(data)
        # with open('asha.json', 'w') as outfile:
        #     json.dump(data[frame_source[frame_name]["key"]], outfile)
        data = pd.DataFrame(data[frame_source[frame_name]["key"]])
        # Start Cleaning of Frame
        function = eval(frame_name+"_data_sanatizer")
        print(function)
        # trim all end spaces
        data = trim_all_columns(data)
        data = function(data)
        store_dataframe(data, save_frame_as)
    else:
        return {"status": "Error Occured"}
    return {"status": "Redis Data Loaded for frame '"+frame_name +"' for session '"+ save_frame_as+ "'" }

def prepare_redis(request, frame_name):
    if(frame_name == "committee"):
        response = NHP_Generation(request, frame_name)

    elif(frame_name == "HRMIS"):
        response = HRMIS_Generation(request, frame_name)

    elif(frame_name == "HMIS"):
        response = HMIS_Generation(request, frame_name)

    elif(frame_name=="NHM"):
        response = NHM_Generation(request, frame_name)
    else:
        response = NHM_Generation(request, frame_name)
    # return JsonResponse(response, safe=False)
    return JsonResponse(response)

def categorize_population_watch(x):
    if x <=999:
        return "0 - 999"
    if( x >= 1000 and x<=1500):
        return "1000 - 1500"
    if( x > 1500 and x<=2500):
        return "1501 - 2500"
    if( x > 2500 and x<=3500):
        return "2501 - 3500"
    if( x > 3500):
        return "3501 - Above"
    return "Invalid"

def categorized_total(x):
    if x <=999:
        return "0 - 999"
    if( x >= 1000 and x<=2000):
        return "1000 - 2000"
    if( x > 2000 and x<=3000):
        return "2001 - 3000"
    if( x > 3000 and x<=4000):
        return "3001 - 4000"
    if( x > 4000 and x<=5000):
        return "4001 - 5000"
    if( x > 5000 and x<=6000):
        return "5001 - 6000"
    if( x > 6000 and x<=8000):
        return "6001 - 8000"
    if( x > 8000 and x<=10000):
        return "8001 - 10,000"
    if( x > 10000 and x<=20000):
        return "10,001 - 20,000"
    if( x > 20000):
        return "20,000 - Above"
    return "Invalid"

def categorized_age(x):
    if x < 25:
        return "24 Yrs or Less"
    if( x >= 25 and x<=29):
        return "25 - 29 Yrs"
    if( x >= 30 and x<=34):
        return "30 - 34 Yrs"
    if( x >= 35 and x<=39):
        return "35 - 39 Yrs"
    if( x >= 40 and x<=44):
        return "40 - 44 Yrs"
    if( x >= 45 and x<=49):
        return "45 - 49 Yrs"
    if( x >= 50 and x<=54):
        return "50 - 54 Yrs"
    if( x >= 55 and x<=59):
        return "55 - 59 Yrs"
    if( x >= 60 and x<=64):
        return "60 - 64 Yrs"
    if( x > 64):
        return "65 - Above"
    return "Invalid"
    
def authority_status(x):
    if(x == "Started" or x == "Not Started" ):
        return x
    else:
        return "Completed"

def working_since_map(df):
    # Modify Working_Since as per standard
    prog_start_date = datetime.date(2006, 1, 1)
    df['working_since'] = pd.to_datetime(df.working_since.astype(str), errors ="coerce").dt.date.fillna(prog_start_date)
    df["working_since"] = np.where( (df['working_since'] < prog_start_date), prog_start_date, df['working_since'])
    df['working_since_year'] = pd.to_datetime(df.working_since.astype(str), errors ="coerce").dt.year
    df['working_since'] = pd.to_datetime(df.working_since.astype(str), errors ="coerce").dt.strftime('%b-%y')
    return df

def working_since_map_anm(df):
    # Modify Working_Since as per standard
    prog_start_date = datetime.date(1980, 1, 1)
    prog_max_date = datetime.date.today()
    df['working_since'] = pd.to_datetime(df.working_since.astype(str), errors ="coerce").dt.date.fillna(prog_start_date)
    df["working_since"] = np.where( (df['working_since'] < prog_start_date), prog_start_date, df['working_since'])
    df["working_since"] = np.where( (df['working_since'] > prog_max_date), prog_max_date, df['working_since'])
    df['working_since_year'] = pd.to_datetime(df.working_since.astype(str), errors ="coerce").dt.year
    df['working_since'] = pd.to_datetime(df.working_since.astype(str), errors ="coerce").dt.strftime('%b-%y')
    return df

def caste_map(df):
    # Change caste code to actual String
    df['caste'] = df['caste'].map({'1': "Gen", '2': "SC", '3': "ST", '4': "OBC"})
    df['caste'] = df['caste'].fillna("N/A")
    return df

def mobile_status(df, col_name):
    pass #df[col_name])
    # Add new column on the basis of the validity of mobile number
    pattern1 = re.compile(r'^(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[6-9]\d{9}$',re.I)
    df[col_name] = np.where(df[col_name].astype(str).str.contains(pattern1), 'Valid', 'Invalid')
    return df

def educational_qualification_map(df):
    # Change education code to actual String
    df['educational_qualification'] = df['educational_qualification'].map({'1': "High School", '2': "Intermediate", '3': "Graduate", '4': "Post Graduate"})
    df['educational_qualification'] = df['educational_qualification'].fillna("N/A")
    return df

def asha_data_sanatizer(df):

    df.drop(["asha_id"], axis=1, inplace=True)
    df = df.rename(columns={"mobile":"mobile_status", "dst_id":"district_id", "blk_id":"block_id", "scmid":"sub_center_id", "vid":"village_id", "caste_code":"caste", "asha_mobile_no":"mobile_status", "name_of_asha" :"name", "asmid": FRAME_NAME+"_id"})
    # specify columns which need to casted into integer
    column_cast_to_int = ["asha_id", "population", "age", "district_id", "block_id", "sub_center_id", "village_id", "sng_id", "district_code_census", "block_code_census"]
    df = caste_to_int(df, column_cast_to_int)
    df["age_category"] = df["age"].apply(lambda x: categorized_age(x))
    df["population_category"] = df["population"].apply(lambda x: categorize_population_watch(x))
    df = educational_qualification_map(df)
    df = working_since_map(df)
    df = caste_map(df)
    df = mobile_status(df, "mobile_status")
    df.drop(["wether_selected_as_asha", "wether_currently_working", "response", "reason", "bank_account", "no_of_adhar_card", "pfms_uid", "name_of_bank", 'name_of_branch', 'other_training', 'percent_marks_fourthphase', 'percentage_of_marks_firstphase', 'percentage_of_marks_secondphase', 'percnt_of_third_phase', 'rbid', 'seven_days_training', 'stid', 'ten_days_training', 'twelve_days_training', 'villagerevenue_id', 'eight_days_training', 'four_days_training'], axis=1, inplace=True)
    pass #"Asha data sanitizer")
    return df

def sangini_data_sanatizer(df):
    pass #df.columns)
    df = asha_data_sanatizer(df)
    asha_data = retrieve_frame("asha")
    asha_data.sng_id = asha_data.sng_id.astype(str)
    asha_data.asha_id = asha_data.asha_id.astype(str)
    asha_data = asha_data.groupby('sng_id').asha_id.agg([('count', 'count'), ('mapped_asha', ', '.join)]).reset_index()
    asha_data = asha_data.rename(columns={"sng_id":"sangini_id", "count":"number_of_asha"})
    df = (pd.merge(df, asha_data, on='sangini_id', how='left'))
    column_cast_to_int = ['sangini_id']
    df["age_category"] = df["age"].apply(lambda x: categorized_age(x))
    df = caste_to_int(df, column_cast_to_int)
    df.number_of_asha = pd.to_numeric(df.number_of_asha, errors='coerce').fillna(0).astype(np.int64)
    df.mapped_asha = df.mapped_asha.fillna("No Asha Mapped")
    return df

def anm_data_sanatizer(df):
    df.drop(["anm_id"], axis=1, inplace=True)
    df = df.rename(columns={"dst_id":"district_id", "blk_id":"block_id", "scmid":"sub_center_id", "vid_id":"village_id", "anm_name":"name", "anm_age":"age", "date_of_joining":"working_since", "anm_mobile":"mobile_status", "anmid":FRAME_NAME+"_id"})
    column_cast_to_int = ["anm_id", "age", "district_id", "block_id", "sub_center_id", "village_id", "district_code_census", "block_code_census"]
    df = caste_to_int(df, column_cast_to_int)
    df = working_since_map_anm(df)
    df = caste_map(df)
    df["age_category"] = df["age"].apply(lambda x: categorized_age(x))
    df['job_type'] = df['job_type'].map({'1': "Permanent", '2': "Contractual"})
    df['job_type'] = df['job_type'].fillna("Not Specified")
    df = mobile_status(df, "mobile_status")
    asha_data = retrieve_frame("asha")
    asha_data.asha_id = asha_data.asha_id.astype(str)
    asha_data = asha_data.groupby('sub_center_id').asha_id.agg([('count', 'count'), ('mapped_asha', ', '.join)]).reset_index()
    asha_data = asha_data.rename(columns={"count":"number_of_asha"})
    df = (pd.merge(df, asha_data, on='sub_center_id', how='left'))
    df.number_of_asha = pd.to_numeric(df.number_of_asha, errors='coerce').fillna(0).astype(np.int64)
    df.mapped_asha = df.mapped_asha.fillna("No Asha Mapped")
    df.drop([ "status", "training_ri", "training_iucd", "training_iycf", "training_nssk", "training_imnci", "training_sba"], axis=1, inplace=True)
    return df

def asha_payment_data_sanatizer(df):
    # pass #df)
    df.drop(["asha_id"], axis=1, inplace=True)
    df = df.rename(columns={"id": "asha_id", "name_of_asha":"name"})
    # specify columns which need to casted into integer
    column_cast_to_int = [col for col in df if col.endswith('total')]
    # column_cast_to_int = ['asha_id', 'year', 'aaa_total', 'addpay_total', 'child_total', 'encep_total', 'family_total', 'hrp_total', 'immu_total', 'jsy_total', 'kalajaar_total', 'leprosy_total', 'lymp_total', 'malaria_total', 'mdr_total', 'niddcp_total', 'rksk_total', 'rntcp_total', 'subtotal',]
    df = caste_to_int(df, column_cast_to_int)
    df["categorized_total"] = df["subtotal"].apply(lambda x: categorized_total(x))
    df.drop(["sno"], axis=1, inplace=True)
    return df

def asha_payment_status_data_sanatizer(df):
    df = handle_bcpm_moic_bam_status_and_performance(df)
    return df
#########################################################################################################
#
#      UTTAR PRADESH: CHO PROFILE
#      DATE: 30 JUNE 2021
#      AUTHOR: ABHISHEK AGRAWAL
#
#########################################################################################################
def cho_data_sanatizer(df):
    import datetime
 
    df = trim_all_columns(df)
    
    df = sanitize_column(df)
    
    df = df.rename(columns={"estimated_population_covered_by_hwc":"population",
                            "sub_center_name":"SUB CENTER",
                            "region_name":"REGION",
                            "state_name":"STATE",
                            "block_name":"BLOCK",
                            "district_name":"DISTRICT",
                            "stid":"state_id",
                            "dst_id":"district_id",
                            "blk_id":"block_id",
                            "scmid":"sub_center_id",
                            "vid":"village_id",
                            "cho_name" :"name",
                            'electricity_supply':'Electricity',
                            'water_supply': 'Water',
                            "user_unique_id":"cho_id",
                            'date_of_joining':'working_since'
                            })
    df = caste_to_int(df,[
                    "dst_id",
                    "blk_id",
                    "alternate_mobile",
                    "anm_as_cho",
                    "mobile"
                    "asha_as_cho",
                    "village_as_cho",
                    "asha_no",
                    "population",
                    "hrmis_id",
                    "nin_no",
                    "user_unique_id",
                    "mobile",
                    "scmid",
                    "blk_id",
                    ])
    df = working_since_map(df)
    df['population'] = df['population'].astype(int)
    now = datetime.datetime.now()
    df['Age'] = pd.to_datetime(df['dob'],errors = 'coerce')
    df['Age'] = (pd.to_datetime(now.date()) - df['Age']).astype('<m8[Y]')
    now = datetime.datetime.now()
    df['Age'] = pd.to_datetime(df['dob'],errors = 'coerce')
    #file["Age"] = (now.date() - file['dob']).astype('<m8[Y]')
    #print(file['dob'])
    df['Age'] = (pd.to_datetime(now.date()) - df['Age']).astype('<m8[Y]')
    try:
        df["Age"].astype(str)
    except:
        pass
        print("-"*20,"Exc","-"*50)
    #df = sanitize_column(df)
    df["Age-Group"] = df["Age"]
    for index,values in enumerate(df["Age"]):
        try:
            if int(values) < 18:
                df["Age-Group"][index] = "DOB Incorrect"
            elif 17 < int(values) and int(values) < 26:
                df["Age-Group"][index] = "18-25"
            elif 25 < int(values) and int(values)< 31:
                df["Age-Group"][index] = "25-30"
            elif 30 < int(values) and int(values) < 36:
                df["Age-Group"][index] = "30-35"
            elif 35 < int(values) and int(values) < 41:
                df["Age-Group"][index] = "36-40"
            elif 40 < int(values)and int(values) < 46:
                df["Age-Group"][index] = "41-45"
            elif 45 < int(values) and int(values)< 51:
                df["Age-Group"][index] = "46-50"
            elif 50 < int(values) and int(values)< 56:
                df["Age-Group"][index] = "50-55"
            elif 55 < int(values) and int(values)< 61:
                df["Age-Group"][index] = "55-60"
            elif 60 < int(values)and int(values) < 80:
                df["Age-Group"][index] = "61 or Older"
        except :
                df["Age-Group"][index] = "No Data" 
    
    df["mobile_status"] = df["mobile"]
    for index,values in enumerate(df["mobile"]):
        if type(values) == float:
            df["mobile_status"][index] = "valid"
            #print(df["mobile_status"][index])
            #     print("#"*100)
        else:
            df["mobile_status"][index] == "invalid"
    for index,value in enumerate(df["REGION"]):
        df["REGION"][index] = value[3:]
    hwc_frame()
    print("HWC_FRAME_CREATED_IN_WHEREHOUSE")
    return df

#################################################################################
def performance_index(date, std_date):
    try:
        date    = datetime.datetime.strptime(date, "%d/%m/%Y").date()
    except:
        date    = False
    if date:
        # std_date    = datetime.datetime.strptime(std_date, "%d/%m/%Y")
        benchmark   = std_date + datetime.timedelta(days=5)
        if(date < std_date):
            return ("Excellent")
        elif(date == std_date):
            return ("Good")
        elif( (date > std_date) and (date <= benchmark) ):
            return ("Average")
        elif(date > benchmark):
            return ("Below Average")
    else:
        current_date = datetime.date.today()
        if(std_date <= current_date):
            return ("Poor")
        else:
            return ("Pending")
 
def sangini_payment_data_sanatizer(df):
    df.drop(["sno"], axis=1, inplace=True)
    # df = df.rename(columns={"name_of_asha":"name", "asha_sangini_id":"sangini_id", "v_id": "village_id", "routine_refilling": "refilling_of_drug_kit", "asha_sangini_monitor" : "monitoring_of_asha_payment", "asha_sangini_record" : "mother/child_death_registration" , "for_visits" : "asha_visits"})
    df = df.rename(columns={"name_of_asha":"name", "asha_id":"sangini_id", "v_id": "village_id", "routine_refilling": "refilling_of_drug_kit", "asha_sangini_monitor" : "monitoring_of_asha_payment", "asha_sangini_record" : "mother/child_death_registration" , "for_visits" : "asha_visits"})
    column_cast_to_int = ["refilling_of_drug_kit", "monitoring_of_asha_payment", "mother/child_death_registration" , "asha_visits", "cluster_meeting",  "subtotal", "sangini_id", "district_id", "block_id", "sub_center_id", "village_id"]
    df = caste_to_int(df, column_cast_to_int)

    column_cast_to_int = ["refilling_total", "monitoring_total", "death_total", "supportive_total", "block_total"]
    df = caste_to_int(df, column_cast_to_int)
    df["categorized_total"] = df["subtotal"].apply(lambda x: categorized_total(x))
    return df

def sangini_payment_status_data_sanatizer(df):

    df = handle_bcpm_moic_bam_status_and_performance(df)
    return df

def handle_bcpm_moic_bam_status_and_performance(df):
    df["bcpm_status"]           = df["submit"].apply(lambda x: authority_status(x))
    df["moic_status"]           = df["approved"].apply(lambda x: authority_status(x))
    df["bam_status"]            = df["payment"].apply(lambda x: authority_status(x))

    bcpm_std_date               = datetime.date(SESSION_DATE.year, SESSION_MONTH, 25)
    df["bcpm_performance"]      = df["submit"].apply(lambda x: performance_index(x, bcpm_std_date))

    moic_std_date               = datetime.date(SESSION_DATE.year, SESSION_MONTH, 27)
    df["moic_performance"]      = df["approved"].apply(lambda x: performance_index(x, moic_std_date))

    bam_std_date                = last_day_of_month(datetime.date(SESSION_DATE.year, SESSION_MONTH, 1))
    df["bam_performance"]       = df["payment"].apply(lambda x: performance_index(x, bam_std_date))

    df["month"]                 = bam_std_date.strftime("%B")
    df["year"]                  = bam_std_date.strftime("%Y")
    return df

# internal function
def trim_all_columns(df):
    """
    Trim whitespace from ends of each value across all series in dataframe
    """
    trim_strings = lambda x: x.strip() if type(x) is str else x
    return df.applymap(trim_strings)

def caste_to_int(frame, column_list):
    for column in column_list:
        try:
            frame[column] = pd.to_numeric(frame[column], errors='coerce').fillna(0).astype(np.float)
            pass #"Attribute " + column +" casted to Int")
        except Exception as e:
            pass #"Can't Cast " + column + " to Int")
    return frame

# # ========================== NHP Code ========================================

def chnagetoNHPdateFormat(df):
    for col in df.columns: 
        if(df[col].dtype == "object"):
            try:
                df[col]  = pd.to_datetime(df[col]).dt.strftime('%d-%b-%Y')
            except:
                pass #"Can't convert", col)
                df[col] = df[col].astype(str)
    return(df)

# ========================== NHP Code ========================================

def get_data_element_name(api, de_id):
    return api.get("dataElements/"+de_id, params={"fields":"displayFormName"}).json()['displayFormName']

def get_stage_enbale_feilds(api, stage_id):
    r = api.get("programStages/"+stage_id).json()
    enable_feild = {}
    for one_data_element in r["programStageDataElements"]:
        attr_id = one_data_element["dataElement"]["id"]
        attr_name = get_data_element_name(api, attr_id)
        enable_feild[attr_name] = attr_id
    # pass #enable_feild)
    return ({"enable_feild":enable_feild, "display_name": r["displayName"]} )

def get_instace_id(api, orgUnit, program):
    data = api.get('trackedEntityInstances/query', params={"ou":orgUnit, "program":program}).json()["rows"]
    tracker_instaces_set = []
    for one_data in data:
        tracker_instaces_set.append(one_data[0])
    return tracker_instaces_set

def get_tracker_instace_data(api, instace_id, program):

    pass #'trackedEntityInstances/'+instace_id, {"program":program, "fields":"*"})
    data = api.get('trackedEntityInstances/'+instace_id, params={"program":program, "fields":"*"}).json()
    return data

def event_exits(data):
    try:
        if data["enrollments"][0]["events"]:
            pass #len(data["enrollments"]), "Kamil"*20)
            pass #"yes")
            return True
        else:
            pass #"NO ")
            return False
    except Exception as e:
        pass #str(e))
        return False

def dataValue_to_dict(dataValueSet):
    info = {}
    for dataValue in dataValueSet:
        info[dataValue["dataElement"]] = dataValue["value"]
    return info

def get_org_name(api, org_id):
    return api.get("organisationUnits/"+org_id, params={"fields":"name"}).json()['name']

def get_org_group_name(api, org_grp_id):
    # organisationUnitGroups
    return api.get("organisationUnitGroups/"+org_grp_id, params={"fields":"name"}).json()['name']

def get_group_with_org(api, org_id):
    response = api.get("organisationUnits/"+org_id, params={"fields":"name,organisationUnitGroups"}).json()
    # head = get_org_group_name(api, response["organisationUnitGroups"][0]["id"])
    head = response["organisationUnitGroups"][0]["id"]
    return ({head: response["name"]})

def get_relation_dict(api, org_id):
    response = api.get("organisationUnits/"+org_id, params={"fields":"id,ancestors"}).json()
    data = get_group_with_org(api, response["id"])
    for one in response["ancestors"]:
        data = {**data, **get_group_with_org(api, one["id"]) }
        # data.append(get_group_with_org(api, one["id"]))
    return data

def generate_data_json(api, program):
    programStagesName = {}
    response = api.get("programs/"+program).json()
    program_name = "".join([c for c in response["name"] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    orgUnit_set = response["organisationUnits"]
    program_stages = response["programStages"]
    import csv
    stages_enable_feilds = {}
    for one_stage in program_stages:
        response =  get_stage_enbale_feilds(api, one_stage["id"])
        stages_enable_feilds[one_stage["id"]] = response["enable_feild"]
        stages_enable_feilds[one_stage["id"]+ "_display_name"] = response["display_name"]

    master_data_set = {}
    for org in orgUnit_set:
        # pass #org["id"])
        instance_id_set = get_instace_id(api, org["id"], program)
        for instance_id in instance_id_set:
            data = get_tracker_instace_data(api, instance_id, program)
            program_attr = {}
            for one_attr in data["attributes"]:
                program_attr[one_attr["displayName"]] = one_attr["value"]
            program_attr["core_orgUnit"] = org["id"]
            pass #program_attr)
            if event_exits(data):
                size = len(data["enrollments"])
                if(size > 1):
                    print((org['id'], program, size))
                    pass
                    with open('duplicate_entries.csv','a') as f:
                        writer=csv.writer(f)
                        writer.writerow((org['id'], program, size))
                for one_event in data["enrollments"][0]["events"]:
                    program_attr["enrollmentDate"] = data["enrollments"][0]["enrollmentDate"]
                    program_attr["program_status"] = data["enrollments"][0].get("completedDate", data["enrollments"][0].get("status"))
                    program_attr["lastUpdated"]    = data["lastUpdated"]
                    # program_attr["program_status"] = data["enrollments"][0].get("completedDate", "N/A")
                    # Get enable feilds name for that stage
                    data_feild_set = stages_enable_feilds[one_event["programStage"]]
                    ongoing_stage_name = stages_enable_feilds[one_event["programStage"] + "_display_name"]

                    availbale_data = dataValue_to_dict(one_event["dataValues"])
                    detail_dict = {}
                    pass #"Processing stage " + ongoing_stage_name + " for "+ one_event["orgUnitName"])
                    for attr, attr_id in data_feild_set.items():
                        detail_dict[attr] = availbale_data.get(attr_id, "N/A")
                    
                    # detail_dict["event_status"] = one_event.get("completedDate", "N/A")
                    detail_dict["event_status"] = one_event.get("completedDate", one_event.get("status"))
                    detail_dict = {"event_data": detail_dict, "program_attr" : program_attr, "org_attr": get_relation_dict(api, org["id"]) }
                    if(ongoing_stage_name in master_data_set):
                        master_data_set[ongoing_stage_name].append(detail_dict)
                    else:
                        master_data_set[ongoing_stage_name] = [detail_dict]
                    pass #"Completed stage " + ongoing_stage_name + " for "+ one_event["orgUnitName"])
                    # pass #detail_dict)
                    pass #"===="*20)
    file_name = settings.CORE_FILE_PATH+"/%s/%s.json"%("DHIS_json", program_name)
    with open(file_name, 'w') as fp:
        json.dump(master_data_set, fp)

def align_event_recors(data, headers, default_attr):
    all_info = []
    # pass #headers, "kamil")
    if headers:
        default_attr["event_status"] = data["event_status"]
        for itr in range(1 , 51):
            info = {}
            for head in headers:
                key = head.replace("-", " ").replace("%d", "").strip()
                key = re.sub("\s+|\r+|\t+|\n+" , " ", key)
                try:
                    test_head = key.split(" ")
                    if test_head[0] == test_head[1]:
                        key = key.partition(" ")[2]
                except:
                    pass
                    # pass #"Head is Okay")
                if "%d" in head:
                    info[key] = data.get((head)%itr, "N/A")
                else:
                    info[key] = data.get((head), "N/A")
            if set(info.values()) != set(["N/A"]):
                info = {**info, **default_attr}
                all_info.append(info)
        if all_info:
            return all_info
        else:
            pass #{**info, **default_attr})
            return [{**info, **default_attr}]
        # return all_info
    else:
        return [{**data, **default_attr}]

def load_DHIS_json(api, filename):
    # prepare actula name of org group
    organisationUnitGroups = {}
    org_grp_set = api.get("organisationUnitGroups").json()["organisationUnitGroups"]
    for one_grp in org_grp_set:
        organisationUnitGroups[one_grp["id"]] = one_grp["displayName"]
    organisationUnitGroups_keys = organisationUnitGroups.keys()

    EVENT_HEADER = {"Committee Member Information" : ["Name %d", "Age %d", "Sex %d", "Educational Qualification %d", "Mobile number %d", "Designation %d", "Representative %d"],
                    # "Fund Status" : ["Name %d", "Age %d", "Sex %d", "Educational Qualification %d", "Mobile number %d", "Designation %d", "Representative %d"],
                    "Action Plan" : ['Activity %d - Activity Type','Activity %d - Comments on Activity by Demonstrator','Activity %d - Estimated funds required to conduct this activity','Activity %d - Estimated time taken to conduct this activity','Activity %d - Feedback by State Consultants','Activity %d - How will the activity be conducted?','Activity %d - Planned activities with the funds received / goals to be achieved'],
                    # "IPR - 1" : ["Name %d", "Age %d", "Sex %d", "Educational Qualification %d", "Mobile number %d", "Designation %d", "Representative %d"],
                    # "DVR - 1" : ["Name %d", "Age %d", "Sex %d", "Educational Qualification %d", "Mobile number %d", "Designation %d", "Representative %d"],
                    # "IPR - 2" : ["Name %d", "Age %d", "Sex %d", "Educational Qualification %d", "Mobile number %d", "Designation %d", "Representative %d"],
                    # "DVR - 2" : ["Name %d", "Age %d", "Sex %d", "Educational Qualification %d", "Mobile number %d", "Designation %d", "Representative %d"],
                    "Six Monthly Expenditure" : ["Activity Category %d","Activities (approved in the Action Plan) %d","Approved Budget %d","Six monthly Expenditure (Rs.) %d","Balance in Total %d","Remark %d","Quarter 1 Expenditure -%d","Quarter 2 Expenditure -%d","Activity photograph %d", "Bank charges (G)"],
    }

    file_name = settings.CORE_FILE_PATH+"/%s/%s"%("DHIS_json", filename)
    with open(file_name) as f:
        data = json.load(f)

    global MY_PROGRAMS

    for program_name, program_data in data.items():
        ordered_data_set = []
        for one_row in program_data:
            default_attr = {}
            
            for one_mis_key in list(set(organisationUnitGroups_keys) - set(one_row["org_attr"].keys())):
                one_row["org_attr"][one_mis_key] = "other"

            for org_grp_id, org_name in one_row["org_attr"].items():
                org_grp = organisationUnitGroups.get(org_grp_id, "No group name")
                default_attr[org_grp] = org_name
            default_attr = {**default_attr, **one_row["program_attr"]}

            # default_attr["event_status"] = one_row["event_data"][program_name+"_status"]
            
            ordered_data = align_event_recors(one_row["event_data"], EVENT_HEADER.get(program_name, False), default_attr)
            ordered_data_set = ordered_data_set + ordered_data
            # if default_attr["Name of Committee"] == "PHUYOBA VHC":
            #     pass #one_row)
            #     pass #ordered_data, "danish")
            # pass #ordered_data)

        df = pd.DataFrame(ordered_data_set)
        df.rename(columns={"VILLAGE/TOWN/WARD": "VILLAGE"}, inplace=True)

        program_name = program_name.replace(" ", "_")
        master_frame = (filename.replace(" ", "_").replace(".json", "") + "_" +program_name).replace("-", "_")
        store_dataframe(df, master_frame)
        if program_name in MY_PROGRAMS:
            old_df = retrieve_frame(program_name)
            pass #old_df)
            pass #"old_frame_found")
            df = pd.concat([old_df, df], axis=0, sort=False).reset_index(drop=True)
        else:
            MY_PROGRAMS.append(program_name)

        if program_name == "Six_Monthly_Expenditure":
            df["Activity Category"].replace("Medicines & Equipment", 'Medical Equipment & Instrument',inplace=True)
        if program_name == "Action_Plan":
            df["Activity Type"].replace("Medicines & Equipment", 'Medical Equipment & Instrument',inplace=True)
        #     df["Activity Category"]
        #     "Medicines & Equipment"
        #     "Medical Equipment & Instrument"
        store_dataframe(df, program_name)

def committee_type_generate(df_row):
    if df_row["VILLAGE"] != "other":
        return "VHC"
    elif( (df_row["VILLAGE"] == "other") and df_row["SUB CENTER"] != "other" ):
        return "HSCMC"
    elif( (df_row["VILLAGE"] == "other") and df_row["SUB CENTER"] == "other" ):
        return "HCMC"
    else:
        return "No Type"

def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += datetime.timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

def add_Ctype(df):
    df["ctype"] = df.apply(lambda x: committee_type_generate(x), axis=1)
    df.loc[( (df['ctype'] == "HCMC") & (df['PRIMARY HEALTH CENTER'] == "other") ), ['PRIMARY HEALTH CENTER', 'SUB CENTER','VILLAGE']] = 'N/A'
    df.loc[(df['ctype'] == "HCMC"), ['SUB CENTER','VILLAGE']] = 'N/A'
    df.loc[df['ctype'] == "HSCMC", ['VILLAGE']] = 'N/A'

    return df

def sanitize_frame(stage_name, df):
    # df = df[["core_orgUnit", "program_status", "event_status", "RBF Cycle", "enrollmentDate"]]
    df = df.drop_duplicates(subset=["RBF Cycle", "core_orgUnit"], keep="last")
    df[stage_name] = pd.to_datetime(df["event_status"], errors ="coerce")
    df.rename( columns={"event_status": stage_name + "_status"}, inplace=True)
    df[stage_name + "_status"] = df[stage_name+ "_status"].apply(lambda x: rbf_sub_state_fill(x) )
    # exit()
    return df

def generate_NHP_custom_report():

    stages = [ "Fund_Status", "IPR_-_1", "DVR_-_1", "IPR_-_2", "DVR_-_2", "Six_Monthly_Expenditure"]

    df =  sanitize_frame("Action_Plan", retrieve_frame("Action_Plan", ["core_orgUnit", "program_status", "event_status", "RBF Cycle", "enrollmentDate"]))
    for stage in stages:
            new_df = sanitize_frame(stage, retrieve_frame(stage, ["core_orgUnit", "event_status", "RBF Cycle"]))
            df = pd.merge(df,
                    new_df,
                    on=["RBF Cycle", "core_orgUnit"],
                    how='left'
                )
        # pass #df, "00"*100)

    # pass #df)
    # pass #df.columns)
    # df.drop(["enrollmentDate_y"], axis = 1, inplace = True)

    # df.rename(columns={"enrollmentDate_x": "enrollmentDate"}, inplace=True)

    # df.drop(["program_status_x", "program_status_y"], axis = 1, inplace = True)

    df.rename(columns={"program_status": "program_status_status"}, inplace=True)

    df["program_status"] = pd.to_datetime(df["program_status_status"], errors ="coerce")
    df["enrollmentDate"] = pd.to_datetime(df["enrollmentDate"], errors ="coerce")

    df['RBF State'] = df.apply(lambda x: rbf_state_fill(x), axis=1)

    df['rbf_state'] = ""

    df.rename(columns={"enrollmentDate": "rbf_started_on"}, inplace=True)
    store_dataframe(df, "nhp_report")

def rbf_sub_state_fill(stage):
    
    if not pd.isnull(pd.to_datetime(stage, errors ="coerce")):
        result = "Completed"
    elif stage == "SCHEDULE" :
        result = "No Data Entered"
    else:
        result = "Not Completed"
    return result

def rbf_state_fill(row):
    if ( not pd.isnull(row['Action_Plan']) and  not pd.isnull(row['Fund_Status']) and not pd.isnull(row['IPR_-_1']) and not pd.isnull(row['DVR_-_1']) and not pd.isnull(row['IPR_-_2']) and not pd.isnull(row['DVR_-_2']) and not pd.isnull(row['Six_Monthly_Expenditure']) ):
        if pd.isnull(row['program_status']):
            result = "Completed"
        else:   
            result = "Verified"
    else:
        if not pd.isnull(row["enrollmentDate"]):
            if (datetime.datetime.today() - row["enrollmentDate"]).days <= 184 :
                result = "Ongoing"
            else:
                if ( not pd.isnull(row['Action_Plan']) or  not pd.isnull(row['Fund_Status']) or not pd.isnull(row['IPR_-_1']) or not pd.isnull(row['DVR_-_1']) or not pd.isnull(row['IPR_-_2']) or not pd.isnull(row['DVR_-_2']) or not pd.isnull(row['Six_Monthly_Expenditure']) ):
                    result = "Not Completed"
                else:
                    result = "No Data Entered"
        else:
            result = "Invalid"
    return result

def full_dvr_PDO_calculate(committee_df):

    def_cols = ["Total number of children under age of one year registred for immunisation and growth recorded second time in last six months-M1",
                "Total number of children under age of one year registred for immunisation and growth recorded second time in last six months-M2",
                "Total number of children under age of one year registred for immunisation and growth recorded second time in last six months-M3",
                "Total number of female children under age of one year registred for immunisation-M1 ",
                "Total number of female children under age of one year registred for immunisation-M2 ",
                "Total number of female children under age of one year registred for immunisation-M3",
                "Total number of children under age of one year registred for immunisation-M1",
                "Total number of children under age of one year registred for immunisation-M2",
                "Total number of children under age of one year registred for immunisation-M3",
                "Total number of female children under age of one year registred for immunisation  and growth recorded for second time in last six months-M1",
                "Total number of female children under age of one year registred for immunisation  and growth recorded for second time in last six months-M2",
                "Total number of female children under age of one year registred for immunisation  and growth recorded for second time in last six months-M3",
                "Children aged between 9-11 months registred for immunisation-M1",
                "Children aged between 9-11 months registred for immunisation-M2",
                "Children aged between 9-11 months registred for immunisation-M3",
                "Female children aged between 9-11 months registred for immunisation-M1",
                "Female children aged between 9-11 months registred for immunisation-M2 ",
                "Female children aged between 9-11 months registred for immunisation-M3 ",
                "Children aged between 9-11 months registred for immunisation have received all the recommended vaccines-M1",
                "Children aged between 9-11 months registred for immunisation have received all the recommended vaccines-M2 ",
                "Children aged between 9-11 months registred for immunisation have received all the recommended vaccines-M3",
                "Female children aged between 9-11 months registred for immunisation have reveived all the recommended vaccines-M1 ",
                "Female children aged between 9-11 months registred for immunisation have reveived all the recommended vaccines-M2",
                "Female children aged between 9-11 months registred for immunisation have reveived all the recommended vaccines-M3",
                "Total OPD Per month-M1",
                "Total OPD Per month-M2",
                "Total OPD Per month-M3",
                "Total IPD Per Month-M1",
                "Total IPD Per Month-M2",
                "Total IPD Per Month-M3",
                "Among the total number of the live births in the month in the catchment areas of the SC, the total number of children whose birth was registered-M1",
                "Among the total number of the live births in the month in the catchment areas of the SC, the total number of children whose birth was registered-M2 ",
                "Among the total number of the live births in the month in the catchment areas of the SC, the total number of children whose birth was registered-M3",
                "Among the total number of the Female live births in the month in the catchment areas of the SC, the total number of children whose birth was registered-M1",
                "Among the total number of the Female live births in the month in the catchment areas of the SC, the total number of children whose birth was registered-M2",
                "Among the total number of the Female live births in the month in the catchment areas of the SC, the total number of children whose birth was registered-M3",
                "If birth registration was not done in the same month, please enter birth registration information of female child in this row, under the month that the child’s birth was registered-M1",
                "If birth registration was not done in the same month, please enter birth registration information of female child in this row, under the month that the child’s birth was registered-M2",
                "If birth registration was not done in the same month, please enter birth registration information of female child in this row, under the month that the child’s birth was registered-M3",
                "If birth registration was not done in the same month, please enter birth registration information in this row, under the month that the child’s birth was registered-M1",
                "If birth registration was not done in the same month, please enter birth registration information in this row, under the month that the child’s birth was registered-M2",
                "If birth registration was not done in the same month, please enter birth registration information in this row, under the month that the child’s birth was registered-M3",
                "Electricity supply improved by the Project-M1",
                "Electricity supply improved by the Project-M2",
                "Electricity supply improved by the Project-M3",
                "Children between 9-11 months registred for immunisation -M1",
                "Children between 9-11 months registred for immunisation -M2",
                "Children between 9-11 months registred for immunisation -M3",
                "Female children with age between 9-11 months registered for immunization -M1",
                "Female children with age between 9-11 months registered for immunization -M2",
                "Female children with age between 9-11 months registered for immunization -M3",
                "Children between 9-11 months registred for immunisation have received all the recommended vaccines -M1",
                "Children between 9-11 months registred for immunisation have received all the recommended vaccines -M2",
                "Children between 9-11 months registred for immunisation have received all the recommended vaccines -M3",
                "Female children between 9-11 months registered for immunization have received all the recommended vaccines-M1",
                "Female children between 9-11 months registered for immunization have received all the recommended vaccines-M2",
                "Female children between 9-11 months registered for immunization have received all the recommended vaccines-M3",
                "program_status",
                "core_orgUnit",
                "RBF Cycle",
                ]


    dvr1 = retrieve_frame("DVR_-_1", def_cols)
    dvr1["program_status"] = pd.to_datetime(dvr1["program_status"], errors ="coerce")


    dvr2 = retrieve_frame("DVR_-_2", def_cols)
    dvr2["program_status"] = pd.to_datetime(dvr2["program_status"], errors ="coerce")

    dvr2 = pd.merge(dvr1, 
                    dvr2,
                    on=['core_orgUnit', 'RBF Cycle'],
                    how='left',
                    )

    pass #dvr2)

    pass #dvr2.columns)

    # exit()

    for col in dvr2.columns:
        dvr2.rename(columns={col : col.replace("_x", " DVR-1").replace("_y", " DVR-2")}, inplace=True)


    my_col = list(dvr2.columns)
    my_col.remove("core_orgUnit")
    my_col.remove("program_status DVR-1")
    my_col.remove("program_status DVR-2")
    dvr2 = caste_to_int(dvr2, my_col)


    store_dataframe(dvr2, "PDO", sanitize_column=True)

    dvr2 = retrieve_frame("PDO")

    for one_col in dvr2.columns:
        my_reg = r'_m\d_dvr_\d'
        if re.search(my_reg, one_col):
            col = re.sub(my_reg, '', one_col).strip()
            dvr2[col] = dvr2[col + "_m1_dvr_1"] + dvr2[col + "_m2_dvr_1"] + dvr2[col + "_m3_dvr_1"] + dvr2[col + "_m1_dvr_2"] + dvr2[col + "_m2_dvr_2"] + dvr2[col + "_m3_dvr_2"]
    
    committee_df = committee_df.rename(columns={"core_orgUnit": "core_orgunit"})

    dvr2 = pd.merge(committee_df[['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgunit']], 
                    dvr2,
                    on='core_orgunit', 
                    how='right')

    store_dataframe(dvr2, "PDO", sanitize_column=True)

def sanitize_column(df):
    for column in df.columns:
        df.rename(columns={column: re.sub('[^A-Za-z0-9]+|\s+|\r+|\t+', ' ', column).strip().lower().replace(' ', '_') }, inplace=True)
    return df

def target_indicator_for_vhc(dvr_frame_name, dvr_number, dvr_for):
    string_set = ["no", "one","two","three","four", "five", "six","seven","eight","nine"]
    if dvr_number != "3":
        dvr = retrieve_frame(dvr_frame_name+dvr_number)
        dvr["event_status"] = pd.to_datetime(dvr["event_status"], errors ="coerce")
        dvr.dropna(subset=['event_status'], inplace=True)
        dvr = sanitize_column(dvr)
        pass #"== == "*20)
        for c in dvr.columns:
            pass #c)
        pass #"== == "*20)
    else:
        dvr = retrieve_frame(dvr_frame_name)


    if dvr_for == "VHC":
        PERCENT_BENCHMARK = 79
        dvr.rename(columns={
            "dvr"+dvr_number+"_total_score" : "total_score",
            "ipr_"+dvr_number+"_dvr_"+dvr_number+"_total_number_of_deliveries_in_home" : "total_home_deliveries",
            "ipr_"+dvr_number+"_dvr_"+dvr_number+"_total_number_of_deliveries_in_village" : "total_deliveries",
            "ipr_"+dvr_number+"_dvr_"+dvr_number+"_total_number_of_live_births" : "total_live_births",
        }, inplace=True)

        int_column_cast =   [   
                                "total_live_births",
                                "no_of_behavioural_change_communication_campaigns_on_health_nutrition_sanitation_or_related_issues_total_as_per_indicator_performance_reports_submitted",                            
                                "total_score",                            
                                "no_of_vhnds_total_as_per_indicator_performance_reports_submitted",
                                "total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted",
                                "women_who_had_registered_their_pregnancy_and_had_received_a_mcp_card_total_as_per_indicator_performance_reports_submitted",
                                "the_number_of_women_who_had_received_at_least_4_ancs_from_any_provider_during_their_pregnancy_total_as_per_indicator_performance_reports_submitted",
                                "the_number_of_women_who_have_received_jsy_benefits_total_as_per_indicator_performance_reports_submitted",
                                "the_number_of_women_whose_documents_have_been_submitted_for_jsy_by_the_anm_total_as_per_indicator_performance_reports_submitted",
                                "the_number_of_women_who_had_received_a_visit_from_the_asha_in_the_first_24_hours_of_their_birth_and_had_their_new_born_s_weight_taken_by_her_total_as_per_indicator_performance_reports_submitted",
                                "total_home_deliveries",
                                "total_deliveries",
                                
                            ]
        # setting = {
        #             1 : 'dvr[col_name]/3',
        #             2 : 'dvr[col_name]/9',
        #             3 : 'dvr[col_name]/6',
        #             4 : 'dvr[col_name]/dvr["total_live_births"]',
        #             5 : 'dvr[col_name]/dvr["total_deliveries"]',
        #             6 : 'dvr[col_name]/dvr["total_deliveries"]',
        #             7 : 'dvr[col_name]/dvr["total_deliveries"]',
        #             8 : 'dvr[col_name]/dvr["total_deliveries"]',
        #             9 : 'dvr[col_name]/dvr["total_home_deliveries"]'
        #         }
        setting = {
                    1 : 'dvr[col_name]/3',
                    2 : 'dvr[col_name]/9',
                    3 : 'dvr[col_name]/6',
                    4 : 'dvr[col_name]/dvr["total_live_births"]',
                    5 : 'dvr[col_name]/dvr["total_deliveries"]',
                    6 : 'dvr[col_name]/dvr["total_deliveries"]',
                    7 : 'dvr[col_name]/dvr["total_deliveries"]',
                    8 : 'dvr[col_name]/dvr["total_home_deliveries"]'
                }

    elif dvr_for == "HSCMC":
        PERCENT_BENCHMARK = 69
        dvr.rename(columns={
            "dvr"+dvr_number+"_total_score" : "total_score",

            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "out_of_the_total_number_of_live_births_in_the_review_period_total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted":"total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted",
            "among_the_total_number_of_the_live_births_in_the_month_in_the_catchment_areas_of_the_sc_the_total_number_of_children_whose_birth_was_registered_total":"total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted",
            

            "number_of_women_who_had_received_at_least_4_ancs_from_any_provider_during_their_pregnancy_total_as_per_indicator_performance_reports_submitted":"the_number_of_women_who_had_received_at_least_4_ancs_from_any_provider_during_their_pregnancy_total_as_per_indicator_performance_reports_submitted",

            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "summary_of_records_total_number_of_home_deliveries_catchment_area_for_this_duration_total" : "total_home_deliveries",
            "summary_of_records_total_number_of_home_deliveries_catchment_area_for_this_duration_current_quarter": "total_home_deliveries",
            
            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "summary_of_records_total_number_of_deliveries_catchment_area_for_this_duration_1_2_3_total": "total_deliveries",
            "summary_of_records_total_number_of_deliveries_catchment_area_for_this_duration_1_2_3_current_quarter": "total_deliveries",
            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "summary_of_records_total_number_of_live_births_catchment_area_for_this_duration_total": "total_live_births",
            "summary_of_records_total_number_of_live_births_catchment_area_for_this_duration_current_quarter" : "total_live_births",
        }, inplace=True)

        int_column_cast =   [  
                            "total_live_births", 
                            "no_of_behavioural_change_communication_campaigns_on_health_nutrition_sanitation_or_related_issues_total_as_per_indicator_performance_reports_submitted",                            
                            "total_score",    
                            "anm_attendance_at_vhnds_total_as_per_indicator_performance_reports_submitted",
                            "total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted",
                            "number_of_women_who_had_received_at_least_one_bp_blood_pressure_test_from_the_anm_as_part_of_their_anc_check_up_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_women_who_had_received_at_least_4_ancs_from_any_provider_during_their_pregnancy_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_women_who_have_received_jsy_benefits_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_women_for_whom_the_jsy_documents_have_been_submitted_total_as_per_indicator_performance_reports_submitted",
                            "among_the_children_aged_9_to_11_months_in_the_review_period_in_the_catchment_area_of_the_facility_how_many_are_fully_vaccinated_total_as_per_indicator_performance_reports_submitted",

                            "number_of_children_who_were_between_age_9_to_11_months_in_the_review_period_in_the_catchment_area_of_the_facility_total_as_per_indicator_performance_reports_submitted",
                            "total_home_deliveries",
                            "total_deliveries",
                            
                        ]
        setting = {
                1 : 'dvr[col_name]/3',
                2 : 'dvr[col_name]/20',
                3 : 'dvr[col_name]/6',
                4 : 'dvr[col_name]/dvr["total_live_births"]',
                5 : 'dvr[col_name]/dvr["total_deliveries"]',
                6 : 'dvr[col_name]/dvr["total_deliveries"]',
                # 7 : 'dvr[col_name]/dvr["total_deliveries"]',
                7 : 'dvr[col_name]/dvr["total_deliveries"]',
                8 : 'dvr[col_name]/dvr["number_of_children_who_were_between_age_9_to_11_months_in_the_review_period_in_the_catchment_area_of_the_facility_total_as_per_indicator_performance_reports_submitted"]'
            }

    elif dvr_for == "HCMC":
        PERCENT_BENCHMARK = 69
        dvr.rename(columns={
            "dvr"+dvr_number+"_total_score" : "total_score",
            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "among_the_total_number_of_the_live_births_in_the_month_in_the_catchment_areas_of_the_sc_the_total_number_of_children_whose_birth_was_registered_total_current_quarter":"total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted",
            "among_the_total_number_of_the_live_births_in_the_month_in_the_catchment_areas_of_the_sc_the_total_number_of_children_whose_birth_was_registered_total":"total_number_of_children_whose_birth_is_registered_total_as_per_indicator_performance_reports_submitted",
            
            "the_number_of_women_for_whom_the_jsy_documents_have_been_submitted_total_as_per_indicator_performance_reports_submitted":"the_number_of_women_whose_documents_have_been_submitted_for_jsy_by_the_anm_total_as_per_indicator_performance_reports_submitted",
            
            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "summary_of_records_total_number_of_home_deliveries_catchment_area_for_this_duration_total" : "total_home_deliveries",
            "summary_of_records_total_number_of_home_deliveries_catchment_area_for_this_duration_current_quarter": "total_home_deliveries",
            
            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "summary_of_records_total_number_of_deliveries_catchment_area_for_this_duration_1_2_3_total": "total_deliveries",
            "summary_of_records_total_number_of_deliveries_catchment_area_for_this_duration_1_2_3_current_quarter": "total_deliveries",
            #Diffrent diffrent data elemnt in DVR1 and DVR2
            "summary_of_records_total_number_of_live_births_catchment_area_for_this_duration_total": "total_live_births",
            "summary_of_records_total_number_of_live_births_catchment_area_for_this_duration_current_quarter" : "total_live_births",
        }, inplace=True)

        int_column_cast =   [   
                            "total_score",
                            "women_who_receive_anc_who_receive_an_hiv_test_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_women_who_had_received_at_least_4_ancs_from_any_provider_during_their_pregnancy_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_women_who_have_received_jsy_benefits_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_women_whose_documents_have_been_submitted_for_jsy_by_the_anm_total_as_per_indicator_performance_reports_submitted",
                            "the_number_of_children_who_were_weighed_at_birth_total_as_per_indicator_performance_reports_submitted",

                            "total_home_deliveries",
                            "total_deliveries",
                            "total_live_births",

                            # "toilets_score",
                            # "water_supply_score",
                        ]
        setting = {
                1 : 'dvr[col_name]/40',
                2 : 'dvr[col_name]/dvr["total_deliveries"]',
                3 : 'dvr[col_name]/dvr["total_deliveries"]',
                # 4 : 'dvr[col_name]/dvr["total_deliveries"]',
                4 : 'dvr[col_name]/dvr["total_deliveries"]',
                5 : 'dvr[col_name]/dvr["total_deliveries"]',
            }

    # =======================================================

    dvr = caste_to_int(dvr, int_column_cast)

    dvr["rbf_cycle"] = dvr["rbf_cycle"].astype(int)

    base_columns =    ["core_orgunit", "rbf_cycle"]

    for indicator_number in range(1, len(setting)+1):
        col_name = int_column_cast[indicator_number]
        new_col = "indicator_"+str(indicator_number)
        base_columns.append(new_col)
        try :
            dvr[new_col] = eval(setting[indicator_number])
        except Exception as e:
            for x in dvr.columns:
                pass #x)
            pass #str(e), dvr_frame_name, dvr_number, dvr_for, "danish "*20)
            exit()

    dvr = dvr.reindex(columns=([*dvr.columns.tolist()]+string_set), fill_value=0)

    is_valid_entry = False
    dvr["invalid_entry"] = is_valid_entry
    for index, row in dvr.iterrows():
        is_valid_entry = False
        completed_indicator = 0
        for attr, attr_value in row.items():
            if re.search(r'^indicator_\d$', attr):
                attr_value = attr_value*100
                if attr_value == np.inf or attr_value == np.nan:
                    is_valid_entry = True
                elif attr_value >= PERCENT_BENCHMARK and attr_value <= 100:
                    # attr_value = 1
                    completed_indicator += 1
                elif attr_value >= 100:
                    attr_value = 100
                    completed_indicator += 1
                else:
                    # attr_value = 0
                    pass
                dvr.loc[index, attr] = attr_value

        dvr.loc[index, string_set[completed_indicator]] = 100
        dvr.loc[index, "invalid_entry"] = is_valid_entry
        dvr.loc[index, "total_indicator"] = len(setting)
        dvr.loc[index, "completed_indicator"] = completed_indicator
        dvr.loc[index, "target_met_percent"] = (completed_indicator/len(setting))*100
    
    dvr.fillna(0, inplace=True)   
    dvr["invalid_entry"] = dvr["invalid_entry"].replace(to_replace =[False], value ="Valid")
    dvr["invalid_entry"] = dvr["invalid_entry"].replace(to_replace =[True], value ="Invalid")

    dvr = dvr[int_column_cast + base_columns + string_set + ["invalid_entry", "total_indicator", "completed_indicator", "target_met_percent"]].reset_index(drop=True)

    if dvr_number != "3":
        store_dataframe(dvr, dvr_for+"_dvr_"+dvr_number+"_completed")
    else:
        store_dataframe(dvr, dvr_for+"_target_indicators_joint")

def merge_dvr_target_indicator():
    df = retrieve_frame("HCMC_full_dvr")
    for one_frame in ["HSCMC_full_dvr", "VHC_full_dvr"]:
        df = pd.concat([df, retrieve_frame(one_frame)], ignore_index=True)
    store_dataframe(df, "target_indicator_full_dvr")

def demo_version_data_generate():
    df = retrieve_frame("asha")
    data_list = df["region_name"].unique()
    pass #data_list)

    df.drop(["district_id", "district_code_census", "block_id", "block_code_census", "sub_center_id", "village_id"], axis = 1, inplace = True)

    columns_to_fill_demo = ["state_name", "region_name", "district_name", "block_name", "sub_center_name", "village_name", "name", "husband_name"]
    df.rename(columns={"asha_id": "health_worker_id"}, inplace=True)
    for col in columns_to_fill_demo:
        for idx, attr in enumerate(df[col].unique()):
            df[col].replace([attr], (col.split('_')[0].upper() + " " + str(idx)), inplace=True)
    store_dataframe(df, "health_worker")

def join_target_indicator_with_committee(dvr_for, temp_df):

    # all_rbf_collection_frame = retrieve_frame("nhp_report", ['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgUnit', 'RBF Cycle', 'RBF State'])
    all_rbf_collection_frame = retrieve_frame("rbf_Manager", ['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgUnit', 'RBF Cycle', 'RBF State', 'current_rbf'])
    all_rbf_collection_frame.rename(columns={"core_orgUnit":"core_orgunit", "RBF Cycle":"rbf_cycle"}, inplace=True)
    # remove the verficed and compledted check
    # all_rbf_collection_frame = all_rbf_collection_frame[(all_rbf_collection_frame['RBF State'] == 'Verified') | (all_rbf_collection_frame['RBF State'] == 'Completed')]
            
    dvr = retrieve_frame(dvr_for+ "_target_indicators_joint")

    # all_rbf_collection_frame.rename(columns={"core_orgUnit":"core_orgunit", "RBF Cycle":"rbf_cycle"}, inplace=True)
    dvr_data = pd.merge(all_rbf_collection_frame, 
            dvr,
            on=['rbf_cycle', 'core_orgunit',]
            ).reset_index(drop=True)
    store_dataframe(dvr_data, dvr_for+"_target_indicators_consolidated_mixed" )

    # enable the verficed and compledted check
    dvr_data = dvr_data[(dvr_data['RBF State'] == 'Verified') | (dvr_data['RBF State'] == 'Completed')].reset_index(drop=True)
    store_dataframe(dvr_data, dvr_for+"_target_indicators_consolidated" )

    print(all_rbf_collection_frame.columns)
    exit()

def calculate_target_indicator(ctype):
    extra_info = retrieve_frame("rbf_Manager", ["core_orgUnit", "current_rbf", "expected_rbf_complete"])

    def add_standard_indicator_attr(dvr, PERCENT_BENCHMARK):
        string_set = ("no", "one","two","three","four", "five", "six","seven","eight","nine")
        is_valid_entry = False
        dvr["invalid_entry"] = is_valid_entry
        for index, row in dvr.iterrows():
            is_valid_entry = False
            completed_indicator = 0

            indicator_count = 0
            for attr, attr_value in row.items():
                if re.search(r'^indicator_\d$', attr):
                    indicator_count += 1
                    # attr_value = attr_value*100
                    if attr_value == np.inf or attr_value == np.nan:
                        is_valid_entry = True
                    elif attr_value >= PERCENT_BENCHMARK and attr_value <= 100:
                        # attr_value = 1
                        completed_indicator += 1
                    elif attr_value >= 100:
                        attr_value = 100
                        completed_indicator += 1
                    else:
                        # attr_value = 0
                        pass
                    dvr.loc[index, attr] = attr_value

            dvr.loc[index, string_set[completed_indicator]] = 100
            dvr.loc[index, "invalid_entry"] = is_valid_entry
            dvr.loc[index, "total_indicator"] = indicator_count
            dvr.loc[index, "completed_indicator"] = completed_indicator
            dvr.loc[index, "target_met_percent"] = (completed_indicator/indicator_count)*100

        dvr.fillna(0, inplace=True)   
        dvr["invalid_entry"] = dvr["invalid_entry"].replace(to_replace =[False], value ="Valid")
        dvr["invalid_entry"] = dvr["invalid_entry"].replace(to_replace =[True], value ="Invalid")
        return dvr





    def generate_for_HCMC():
        dvr1 = retrieve_frame("RBF_Result_Based_Funding_Cycle_HCMC_CHCPHC_DVR___1")
        dvr2 = retrieve_frame("RBF_Result_Based_Funding_Cycle_HCMC_CHCPHC_DVR___2")

        merge_on_col = ['core_orgUnit', 'RBF Cycle']
        dvr = pd.merge( dvr1, 
                        dvr2,
                        on=merge_on_col
                        ).reset_index(drop=True)

        for col in dvr.columns:
            if(col.endswith("_x")):
                base_col = re.sub(r'_x$', "",col)
                # dvr[base_col] = dvr[col] + dvr[base_col+"_y"]
                dvr.rename(columns={col:base_col+"_dvr1", base_col+"_y":base_col+"_dvr2"}, inplace=True)

        store_dataframe(dvr, "HCMC_target_indicator_all_attr")

        columns_use =   [
                            "Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Total",
                            "Summary of records - Total number of home deliveries catchment area for this duration -Total",
                            "Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility- Total",
                            "Toilets-Score_dvr1",
                            "women who receive ANC who receive an HIV test-Total based on RCH register/ ICTC Register_dvr1",
                            "the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register_dvr1",
                            "The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr1",
                            "The number of women who have received JSY benefits-Total based on JSY Monthly Report format at the facility_dvr1",
                            "the number of children who were weighed at birth-Total number based on delivery register at health facility_dvr1",
                            "DVR1 Total - Score",
                            "Summary of records - Total number of deliveries in the PHC/CHC in this duration- Total",
                            "Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Current quarter",
                            "Summary of records - Total number of home deliveries catchment area for this duration -Current quarter",
                            "Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility-current quarter",
                            "Toilets-Score_dvr2",
                            "women who receive ANC who receive an HIV test-Total based on RCH register/ ICTC Register_dvr2",
                            "the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register_dvr2",
                            "The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr2",
                            "The number of women who have received JSY benefits-Total based on JSY Monthly Report format at the facility_dvr2",
                            "the number of children who were weighed at birth-Total number based on delivery register at health facility_dvr2",
                            "DVR2 Total - Score",
                            "Summary of records - Total number of deliveries in the PHC/CHC in this duration- Current quarter"
                        ]

        dvr = dvr[(columns_use+merge_on_col)]
        dvr =  caste_to_int(dvr, columns_use+['RBF Cycle'])
        col_indi_name = "indicator_"


        dvr["total_delivery"] = dvr["Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Total"] + dvr["Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Current quarter"]

        dvr["total_delivery_at_center"] = dvr["Summary of records - Total number of deliveries in the PHC/CHC in this duration- Total"] + dvr["Summary of records - Total number of deliveries in the PHC/CHC in this duration- Current quarter"]

        dvr["total_delivery_at_other"]  = dvr["Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility- Total"] + dvr["Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility-current quarter"]

        dvr["total_delivery_at_home"]   = dvr["Summary of records - Total number of home deliveries catchment area for this duration -Total"] + dvr["Summary of records - Total number of home deliveries catchment area for this duration -Current quarter"]


        dvr[col_indi_name+"1"] = (dvr["DVR2 Total - Score"]/40)*100

        dvr[col_indi_name+"2"] = ((dvr["women who receive ANC who receive an HIV test-Total based on RCH register/ ICTC Register_dvr1"]+dvr["women who receive ANC who receive an HIV test-Total based on RCH register/ ICTC Register_dvr2"])/dvr["total_delivery"])*100

        dvr[col_indi_name+"3"] = ((dvr["the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register_dvr1"]+dvr["the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register_dvr2"])/dvr["total_delivery"])*100


        dvr[col_indi_name+"4"] = ((dvr["The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr1"]+dvr["The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr2"])/dvr["total_delivery_at_center"])*100


        dvr[col_indi_name+"5"] = ((dvr["the number of children who were weighed at birth-Total number based on delivery register at health facility_dvr1"]+dvr["the number of children who were weighed at birth-Total number based on delivery register at health facility_dvr2"])/dvr["total_delivery_at_center"])*100



        dvr = add_standard_indicator_attr(dvr, 69)

        all_rbf_collection_frame = retrieve_frame("nhp_report", ['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgUnit', 'RBF Cycle', 'RBF State'])
        dvr = pd.merge(all_rbf_collection_frame, 
                        dvr,
                        on=merge_on_col
                        ).reset_index(drop=True)


        dvr = pd.merge(dvr, 
                        extra_info,
                        on=["core_orgUnit"]
                        ).reset_index(drop=True)

        dvr["is_current_rbf"] = "No"
        dvr.loc[(dvr['RBF Cycle']==dvr['current_rbf']), "is_current_rbf"] = "Yes"

        dvr["avg_completed_percentage"] = (dvr["completed_indicator"]*100/8)

        store_dataframe(dvr, "HCMC_target_indicator_used_attr", sanitize_column=True)



    def generate_for_HSCMC():
        dvr1 = retrieve_frame("RBF_Result_Based_Funding_Cycle_HSCMC_DVR___1")
        dvr2 = retrieve_frame("RBF_Result_Based_Funding_Cycle_HSCMC_DVR___2")

        merge_on_col = ['core_orgUnit', 'RBF Cycle']
        dvr = pd.merge( dvr1, 
                        dvr2,
                        on=merge_on_col
                        ).reset_index(drop=True)

        for col in dvr.columns:
            if(col.endswith("_x")):
                base_col = re.sub(r'_x$', "",col)
                # dvr[base_col] = dvr[col] + dvr[base_col+"_y"]
                dvr.rename(columns={col:base_col+"_dvr1", base_col+"_y":base_col+"_dvr2"}, inplace=True)

        store_dataframe(dvr, "HSCMC_target_indicator_all_attr")

        columns_use =   [
                            "ANM attendance at VHNDs-Total as per indicator performance reports submitted_dvr1",
                            "Out of the total number of live births in the review period, total number of children whose birth is registered-Total  number of birth certificate copies with the committee_dvr1",
                            "Number of women who had received at least one BP (blood pressure) test from the ANM as part of their ANC check-up-Total based on RCH register_dvr1",
                            "Number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register",
                            "The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr1",
                            "Number of children who were between age 9 to 11 months in the review period in the catchment area of the facility-Total based on RCH register_dvr1",
                            "Among the children aged  9 to 11 months in the review period, in the catchment area of the Facility, how many are fully vaccinated-Total based on RCH register_dvr1",
                            "Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility- Total",
                            "Summary of records -Total number of institutional deliveries catchment area for this duration - At the center- Total",
                            "Summary of records - Total number of home deliveries catchment area for this duration -Total",
                            "Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Total",
                            "Summary of records - Total number of live births catchment area for this duration - Total",
                            "No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr1",
                            "Toilets-Score_dvr1",
                            "Water Supply-Score_dvr1",
                            "DVR1 Total - Score",
                            "ANM attendance at VHNDs-Total as per indicator performance reports submitted_dvr2",
                            "Out of the total number of live births in the review period, total number of children whose birth is registered-Total  number of birth certificate copies with the committee_dvr2",
                            "Number of women who had received at least one BP (blood pressure) test from the ANM as part of their ANC check-up-Total based on RCH register_dvr2",
                            "The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr2",
                            "Number of children who were between age 9 to 11 months in the review period in the catchment area of the facility-Total based on RCH register_dvr2",
                            "Among the children aged  9 to 11 months in the review period, in the catchment area of the Facility, how many are fully vaccinated-Total based on RCH register_dvr2",
                            "Water Supply-Score_dvr2",
                            "Toilets-Score_dvr2",
                            "DVR2 Total - Score",
                            "Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Current quarter",
                            "Summary of records - Total number of home deliveries catchment area for this duration -Current quarter",
                            "Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility-current quarter",
                            "Summary of records -Total number of institutional deliveries catchment area for this duration - At the center- Current quarter",
                            "Summary of records - Total number of live births catchment area for this duration -Current quarter",
                            "No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr2",
                            "the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register"
                        ]

        dvr = dvr[(columns_use+merge_on_col)]
        dvr =  caste_to_int(dvr, columns_use+['RBF Cycle'])
        col_indi_name = "indicator_"


        dvr["total_live_birth_at_sc"] = dvr["Summary of records - Total number of live births catchment area for this duration - Total"] + dvr["Summary of records - Total number of live births catchment area for this duration -Current quarter"]


        dvr["total_delivery_at_sc"] = dvr["Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Total"] + dvr["Summary of records - Total number of deliveries catchment area for this duration (=1+2+3)- Current quarter"]
        
        dvr["total_institutional_delivery_at_sc"] = dvr["Summary of records -Total number of institutional deliveries catchment area for this duration - At the center- Total"] + dvr["Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility- Total"] + dvr["Summary of records -Total number of institutional deliveries catchment area for this duration - At the center- Current quarter"] + dvr["Summary of records -Total number of institutional deliveries catchment area for this duration - At other facility-current quarter"]


        dvr["total_delivery_at_home"] = dvr["Summary of records - Total number of home deliveries catchment area for this duration -Total"] + dvr["Summary of records - Total number of home deliveries catchment area for this duration -Current quarter"]

        dvr["child_at_sc_age_9_11t"] = dvr["Number of children who were between age 9 to 11 months in the review period in the catchment area of the facility-Total based on RCH register_dvr1"] + dvr["Number of children who were between age 9 to 11 months in the review period in the catchment area of the facility-Total based on RCH register_dvr2"]

        dvr[col_indi_name+"1"] = ((dvr["No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr1"] + dvr["No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr2"])/3)*100

        dvr[col_indi_name+"2"] = (dvr["DVR2 Total - Score"]/20)*100


        dvr[col_indi_name+"3"] = ((dvr["ANM attendance at VHNDs-Total as per indicator performance reports submitted_dvr1"]+dvr["ANM attendance at VHNDs-Total as per indicator performance reports submitted_dvr2"])/24)*100


        dvr[col_indi_name+"4"] = ((dvr["Out of the total number of live births in the review period, total number of children whose birth is registered-Total  number of birth certificate copies with the committee_dvr1"]+dvr["Out of the total number of live births in the review period, total number of children whose birth is registered-Total  number of birth certificate copies with the committee_dvr2"])/dvr["total_delivery_at_sc"])*100


        dvr[col_indi_name+"5"] = ((dvr["Number of women who had received at least one BP (blood pressure) test from the ANM as part of their ANC check-up-Total based on RCH register_dvr1"]+dvr["Number of women who had received at least one BP (blood pressure) test from the ANM as part of their ANC check-up-Total based on RCH register_dvr2"])/dvr["total_delivery_at_sc"])*100



        dvr[col_indi_name+"6"] = ((dvr["Number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register"]+dvr["the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on RCH register"])/dvr["total_live_birth_at_sc"])*100



        dvr[col_indi_name+"7"] = ((dvr["The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr1"]+dvr["The number of women for whom the JSY documents have been submitted-Total based on JSY Monthly Report format at the facility_dvr2"])/dvr["total_institutional_delivery_at_sc"])*100



        dvr[col_indi_name+"8"] = ((dvr["Among the children aged  9 to 11 months in the review period, in the catchment area of the Facility, how many are fully vaccinated-Total based on RCH register_dvr1"]+dvr["Among the children aged  9 to 11 months in the review period, in the catchment area of the Facility, how many are fully vaccinated-Total based on RCH register_dvr2"])/dvr["child_at_sc_age_9_11t"])*100


        dvr = add_standard_indicator_attr(dvr, 69)


        all_rbf_collection_frame = retrieve_frame("nhp_report", ['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgUnit', 'RBF Cycle', 'RBF State'])
        
        dvr = pd.merge(all_rbf_collection_frame, 
                        dvr,
                        on=merge_on_col
                        ).reset_index(drop=True)


        dvr = pd.merge(dvr, 
                        extra_info,
                        on=["core_orgUnit"]
                        ).reset_index(drop=True)

        dvr["is_current_rbf"] = "No"
        dvr.loc[(dvr['RBF Cycle']==dvr['current_rbf']), "is_current_rbf"] = "Yes"
        dvr["avg_completed_percentage"] = (dvr["completed_indicator"]*100/5)

        store_dataframe(dvr, "HSCMC_target_indicator_used_attr", sanitize_column=True)






    def generate_for_VHC():
        dvr1 = retrieve_frame("RBF_Result_Based_Funding_Cycle_VHC_DVR___1")
        dvr2 = retrieve_frame("RBF_Result_Based_Funding_Cycle_VHC_DVR___2")

        merge_on_col = ['core_orgUnit', 'RBF Cycle']
        dvr = pd.merge( dvr1, 
                        dvr2,
                        on=merge_on_col
                        ).reset_index(drop=True)

        for col in dvr.columns:
            if(col.endswith("_x")):
                base_col = re.sub(r'_x$', "",col)
                # dvr[base_col] = dvr[col] + dvr[base_col+"_y"]
                dvr.rename(columns={col:base_col+"_dvr1", base_col+"_y":base_col+"_dvr2"}, inplace=True)

        store_dataframe(dvr, "VHC_target_indicator_all_attr")

        columns_use =   [
                            "Designation of Verifier_dvr1",
                            "Name of Verifier_dvr1",
                            "Date of visit_dvr1",
                            "No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr1",
                            "No. of VHNDs-Total as per indicator performance reports submitted _dvr1",
                            "total number of children whose birth is registered-Total as per indicator performance reports submitted_dvr1",
                            "women who had registered their pregnancy and had received a MCP card-Total number of MCP Card/Spot Checks during verification_dvr1",
                            "the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on MCP card/Spot Checks during verification_dvr1",
                            "the number of women whose documents have been submitted for JSY by the ANM-Total based on JSY register at the  facility level_dvr1",
                            "the number of women who had received a visit from the ASHA in the first 24 hours of their birth and had their new-born’s weight taken by her-Total number based on MCP card/spot checks_dvr1",
                            "IPR 1 - DVR 1 - Total number of deliveries in home",
                            "IPR 1 - DVR 1 - Total number of deliveries in institution",
                            "IPR 1 - DVR 1 - Total number of deliveries in village",
                            "IPR 1 - DVR 1 - Total number of live births",
                            "DVR1 Total - Score",
                            "No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr2",
                            "No. of VHNDs-Total as per indicator performance reports submitted _dvr2",
                            "total number of children whose birth is registered-Total as per indicator performance reports submitted_dvr2",
                            "women who had registered their pregnancy and had received a MCP card-Total number of MCP Card/Spot Checks during verification_dvr2",
                            "the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on MCP card/Spot Checks during verification_dvr2",
                            "the number of women whose documents have been submitted for JSY by the ANM-Total based on JSY register at the  facility level_dvr2",
                            "the number of women who had received a visit from the ASHA in the first 24 hours of their birth and had their new-born’s weight taken by her-Total number based on MCP card/spot checks_dvr2",
                            "IPR 2 DVR 2 - Total number of deliveries in home",
                            "IPR 2 DVR 2 - Total number of deliveries in institution",
                            "IPR 2 DVR 2 - Total number of deliveries in village",
                            "IPR 2 DVR 2 - Total number of live births",
                            "DVR2 Total - Score"
                        ]

        dvr = dvr[(columns_use+merge_on_col)]
        dvr =  caste_to_int(dvr, columns_use+['RBF Cycle'])
        col_indi_name = "indicator_"
        

        dvr["total_delivery_at_vhc"] = dvr["IPR 1 - DVR 1 - Total number of deliveries in village"] + dvr["IPR 2 DVR 2 - Total number of deliveries in village"]

        dvr["total_live_birth"] = dvr["IPR 1 - DVR 1 - Total number of live births"] + dvr["IPR 2 DVR 2 - Total number of live births"]

        dvr["total_institutional_delivery_at_vhc"] = dvr["IPR 1 - DVR 1 - Total number of deliveries in institution"] + dvr["IPR 2 DVR 2 - Total number of deliveries in institution"]


        dvr["total_delivery_at_home"] = dvr["IPR 1 - DVR 1 - Total number of deliveries in home"] + dvr["IPR 2 DVR 2 - Total number of deliveries in home"]


      
        dvr[col_indi_name+"1"] = ((dvr["No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr1"] + dvr["No. of Behavioural Change Communication Campaigns on health, nutrition, sanitation or related issues-Total as per indicator performance reports submitted_dvr2"])/3)*100

        dvr[col_indi_name+"2"] = (dvr["DVR2 Total - Score"]/9)*100


        dvr[col_indi_name+"3"] = ((dvr["No. of VHNDs-Total as per indicator performance reports submitted _dvr1"]+dvr["No. of VHNDs-Total as per indicator performance reports submitted _dvr2"])/6)*100


        dvr[col_indi_name+"4"] = ((dvr["total number of children whose birth is registered-Total as per indicator performance reports submitted_dvr1"]+dvr["total number of children whose birth is registered-Total as per indicator performance reports submitted_dvr2"])/dvr["total_live_birth"])*100


        dvr[col_indi_name+"5"] = ((dvr["women who had registered their pregnancy and had received a MCP card-Total number of MCP Card/Spot Checks during verification_dvr1"]+dvr["women who had registered their pregnancy and had received a MCP card-Total number of MCP Card/Spot Checks during verification_dvr2"])/dvr["total_delivery_at_vhc"])*100


        dvr[col_indi_name+"6"] = ((dvr["the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on MCP card/Spot Checks during verification_dvr1"]+dvr["the number of women who had received at least 4 ANCs from any provider during their pregnancy-Total based on MCP card/Spot Checks during verification_dvr2"])/dvr["total_delivery_at_vhc"])*100



        dvr[col_indi_name+"7"] = ((dvr["the number of women whose documents have been submitted for JSY by the ANM-Total based on JSY register at the  facility level_dvr1"]+dvr["the number of women whose documents have been submitted for JSY by the ANM-Total based on JSY register at the  facility level_dvr2"])/dvr["total_institutional_delivery_at_vhc"])*100


        dvr[col_indi_name+"8"] = ((dvr["the number of women who had received a visit from the ASHA in the first 24 hours of their birth and had their new-born’s weight taken by her-Total number based on MCP card/spot checks_dvr1"]+dvr["the number of women who had received a visit from the ASHA in the first 24 hours of their birth and had their new-born’s weight taken by her-Total number based on MCP card/spot checks_dvr2"])/dvr["total_delivery_at_home"])*100



        for index, row in dvr.iterrows():
            if (row["total_delivery_at_home"] == 0 and row["total_institutional_delivery_at_vhc"] == 0):
                dvr.loc[index, col_indi_name+"8"] = 0
            elif row["total_delivery_at_home"] == 0:
                dvr.loc[index, col_indi_name+"8"] = 100


        dvr = add_standard_indicator_attr(dvr, 79)

        all_rbf_collection_frame = retrieve_frame("nhp_report", ['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgUnit', 'RBF Cycle', 'RBF State'])
        dvr = pd.merge(all_rbf_collection_frame, 
                        dvr,
                        on=merge_on_col
                        ).reset_index(drop=True)

        dvr = pd.merge(dvr, 
                        extra_info,
                        on=["core_orgUnit"]
                        ).reset_index(drop=True)

        dvr["is_current_rbf"] = "No"
        dvr.loc[(dvr['RBF Cycle']==dvr['current_rbf']), "is_current_rbf"] = "Yes"
        dvr["avg_completed_percentage"] = (dvr["completed_indicator"]*100/8)

        store_dataframe(dvr, "VHC_target_indicator_used_attr", sanitize_column=True)

        
    eval("generate_for_"+ctype+"()")

def join_target_indicator(temp_df, dvr_for):
    main_columns = {
                        "HCMC"  : 11,
                        "HSCMC" : 15,
                        "VHC"   : 14,
                    }
    dvr1 = retrieve_frame(dvr_for+"_dvr_1_completed")
    columns = list(dvr1.columns)[:main_columns[dvr_for]]
    dvr1 = dvr1[columns]
    dvr2 = retrieve_frame(dvr_for+"_dvr_2_completed", columns=columns)

    dvr = pd.merge(dvr1, 
                    dvr2,
                    on=['core_orgunit', 'rbf_cycle']
                    ).reset_index(drop=True)


    store_dataframe(dvr, dvr_for+"_TARGET_INDICATOR_MERGED")


    del dvr1
    del dvr2

    for col in dvr.columns:
        if(col.endswith("_x")):
            base_col = re.sub(r'_x$', "",col)
            dvr[base_col] = dvr[col] + dvr[base_col+"_y"]
            dvr.rename(columns={col:base_col+"_dvr1", base_col+"_y":base_col+"_dvr2"}, inplace=True)
    
    temp_df = temp_df.rename(columns={"core_orgUnit":"core_orgunit"})
    dvr = pd.merge(temp_df[['Name of Committee', 'ctype', "Committee Category", 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgunit']], 
            dvr,
            on='core_orgunit', 
            )

    store_dataframe(dvr, dvr_for+"_target_indicators" )

def NHP_frame_manage():

    # demo_version_data_generate()
    generate_NHP_custom_report()
    # ============= Start Generating Frame for Commettees and Members ========================
    df = retrieve_frame("Committee_Member_Information")
    df = mobile_status(df, "Mobile number")

    df = caste_to_int(df, ["Population Covered", "Age", "OTG Amount"])

    df = add_Ctype(df)

    df["chairman"] = "N/A"
    df["co_chairman"] = "N/A"
    for index, df_row in df.iterrows():
       
        if(df_row["Designation"] == "Chairman" ):
            if((df_row["Sex"] == "F")):
                df.loc[(df['core_orgUnit'] == df_row["core_orgUnit"]), ['chairman']] = 'Women'
            else:
                df.loc[(df['core_orgUnit'] == df_row["core_orgUnit"]), ['chairman']] = 'Men'
        elif( (df_row["Designation"] == "Co- Chair") or (df_row["Designation"] == "Co-Chair") ):
            if((df_row["Sex"] == "F")):
                df.loc[(df['core_orgUnit'] == df_row["core_orgUnit"]), ['co_chairman']] = 'Women'
            else:
                df.loc[(df['core_orgUnit'] == df_row["core_orgUnit"]), ['co_chairman']] = 'Men'
    
    # temp_df = df
    temp_df = df[['Name', 'Designation', 'Representative', 'Age', 'Sex', 'Mobile number', 'Educational Qualification', 'Name of Committee', 'ctype', "Committee Category", 'Date of MOU', 'OTG Amount', 'OTG Date', 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'core_orgUnit', 'chairman', 'co_chairman']]
    store_dataframe(temp_df, "members")
    
    # df = temp_df
    col = 'Date of MOU'
    df[col] = pd.to_datetime(df[col])
    # df[col]  = df[col].fillna(pd.to_datetime( datetime.date.today() ))

    df['mou_year'] = df[col].dt.year
    df['mou_month'] = df[col].dt.month
    df['mou_day'] = df[col].dt.day

    # df[col]  = df[col].dt.date

    df = df.drop_duplicates(subset='core_orgUnit', keep = "last").reset_index(drop=True)
    default_order = ['Name of Committee', 'ctype', "Committee Category", 'Date of MOU', 'OTG Amount', 'OTG Date', 'STATE', 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE', 'Bank Name', 'IFSC Code',  'Bank A/C Number', 'Population Covered', 'Date of Training', 'mou_year', 'mou_month', 'mou_day', 'core_orgUnit', 'chairman', 'co_chairman']
    temp_df = df[default_order]


    df = retrieve_frame("nhp_report")

    df = caste_to_int(df, ['RBF Cycle'])

    x = temp_df
    x = x.append([x]*10, ignore_index=True)
    cycles = [0,1,2,3,4,5,6,7,8,9,10]
    x = x.join(pd.DataFrame(cycles * int(len(x)/len(cycles)+1), columns=['RBF Cycle']))

    df = pd.merge(x, 
                    df,
                    on=['core_orgUnit','RBF Cycle'],
                    how='left')

    df.loc[( (df['Action_Plan_status'].isna()) &  (df['Fund_Status_status'].isna()) & (df['IPR_-_1_status'].isna()) & (df['DVR_-_1_status'].isna()) & (df['IPR_-_2_status'].isna()) & (df['DVR_-_2_status'].isna()) & (df['Six_Monthly_Expenditure_status'].isna()) ), ['RBF State']] = 'Not Filled Any RBF'

    
    total_committee_counts = temp_df.groupby(["ctype"])[["ctype"]].count().to_dict()
    

    frame_count_json = df.groupby(["ctype", "RBF Cycle", "RBF State"])[["ctype", "RBF Cycle", "RBF State"]].count().to_dict()


    for rbf_cycle in range(11):
        for ctype in ["HCMC", "HSCMC", "VHC"]:
            my_key = (ctype, rbf_cycle, "Not Filled Any RBF")
            if frame_count_json["ctype"].get(my_key) == total_committee_counts["ctype"][ctype]:
                df = df.drop(df[ (df["RBF Cycle"] == rbf_cycle) & (df["RBF State"] == "Not Filled Any RBF") ].index).reset_index(drop=True)


    df.loc[( (df['RBF State'] == "No Data Entered") | (df['RBF State'] == "Not Filled Any RBF") ), ['rbf_state']] = 'No Data Entered'

    df.loc[( (df['RBF State'] == "Ongoing") | (df['RBF State'] == "Not Completed") ), ['rbf_state']] = 'Ongoing'

    df.loc[( (df['RBF State'] == "Verified") | (df['RBF State'] == "Completed") ), ['rbf_state']] = 'Completed'


    col_list = ["Action_Plan_status", "Fund_Status_status", "IPR_-_1_status", "DVR_-_1_status", "IPR_-_2_status", "DVR_-_2_status", "Six_Monthly_Expenditure_status"]
    # df.loc[:, col_list] = df[col_list].fillna("danish", inplace=True)
    for col in col_list:
        df[col].fillna("No Data Entered", inplace=True)

    store_dataframe(df, "nhp_report")
    calculate_target_indicator("HCMC")
    calculate_target_indicator("HSCMC")
    calculate_target_indicator("VHC")

    health_index_data_set = []
    for i in range(1,2):
        for j in range(1,10):
            for k in range(1,20):
                health_index_data_set.append(   
                                                {
                                                    "input_indicator"       : f"Input Indicator - {k}",
                                                    "intermediate_outcome"  : f"Intermediate outcome - {j}",
                                                    "outcome"               : f"Outcome - {i}"
                                                }
                                            )

    health_index_data_set = pd.DataFrame(health_index_data_set)
    store_dataframe(health_index_data_set, "health_index_data_set")


    temp_df = add_committee_audit(temp_df).reset_index()

    store_dataframe(temp_df, "committees")

    full_dvr_PDO_calculate(temp_df)

    # ============= End Generating Frame for Commettees and Members ========================

    # ============= Start Generating Frame for Action Plan ========================
    df = retrieve_frame("Action_Plan")

    df = caste_to_int(df, ["Activity Estimated funds required to conduct this activity", "RBF Cycle"])

    col = 'enrollmentDate'
    df = df[df[col].notna()].reset_index()
    
    df[col] = pd.to_datetime(df[col])

    df['otg_year'] = df[col].dt.year
    df['otg_month'] = df[col].dt.month
    df['otg_day'] = df[col].dt.day

    # df[col]  = df[col].dt.date

    df["rbf_state"] = "Completed"

    idx = df.groupby(['core_orgUnit'])['RBF Cycle'].transform(max) == df['RBF Cycle']
    # x = df.groupby(['core_orgUnit'], sort=False)['RBF Cycle'].max()
    pass #df[idx]["rbf_state"])
    # df[idx]["rbf_state"] = "Ongoing"

    df.at[idx, "rbf_state"] = "Ongoing"

    pass #"***********", df[idx]["rbf_state"])

    temp_df.drop(['VILLAGE', 'STATE', 'COMMUNITY HEALTH CENTER', 'BLOCK', 'PRIMARY HEALTH CENTER', 'DISTRICT', 'SUB CENTER'], axis = 1, inplace = True)

    df = pd.merge(temp_df, 
                    df,
                    on='core_orgUnit', 
                    how='inner')
    df = add_Ctype(df)              
    store_dataframe(df, "action_plan")


    # df_csv = pd.read_csv(r'C:\Users\TATTVA\Downloads\nagaland_nfhs4.csv')
    # df_csv.fillna(0, inplace=True)
    # store_dataframe(df_csv, "nagaland_nfhs4")


    df = add_Ctype(df)

    df = retrieve_frame("Fund_Status")

    col = 'enrollmentDate'
    df = df[df[col].notna()].reset_index()
    
    df[col] = pd.to_datetime(df[col])

    # df[col]  = df[col].fillna(pd.to_datetime( datetime.date.today() ))

    df['otg_year'] = df[col].dt.year
    df['otg_month'] = df[col].dt.month
    df['otg_day'] = df[col].dt.day

    # df[col]  = df[col].dt.date

    unique_df = df.drop_duplicates(subset ="core_orgUnit", keep = "last").reset_index(drop = True)

    for index, row in unique_df.iterrows():
        temp_df1 = df[df["core_orgUnit"] == row["core_orgUnit"]]
        from_rbf  = 0

        completed_rbf, ongoing_rbf = 0, 0
        for c_index, c_row in temp_df1.iterrows():
            rbf_cycle = int(c_row["RBF Cycle"])
            from_rbf = rbf_cycle if (from_rbf < rbf_cycle) else from_rbf
            pass #c_row["RBF Cycle"], "Filled", c_row["enrollmentDate"])
            col_name = "rbf_" + c_row["RBF Cycle"]
            unique_df.at[index, col_name] = c_row["enrollmentDate"]
            unique_df.at[index, col_name+"_status"] = c_row["program_status"]

            # if c_row["program_status"] is pd.Timestamp:
            if not pd.isnull( pd.to_datetime(c_row["program_status"], errors='coerce') ):
                completed_rbf += 1
            elif c_row["program_status"] == "ACTIVE":
                ongoing_rbf += 1

        unique_df.at[index, "completed_rbf"] = completed_rbf
        unique_df.at[index, "ongoing_rbf"] = ongoing_rbf


        for cycle in range(from_rbf+1, 16):
            col_name = "rbf_" + str(cycle)
            prev_rbf = "rbf_" + str(cycle-1)
            unique_df.at[index, col_name] = unique_df.at[index, prev_rbf] + datetime.timedelta(days=184)
            unique_df.at[index, col_name+"_status"] = "N/A"
        unique_df.at[index, "RBF Cycle"] = from_rbf

        unique_df.at[index, "current_rbf"] = from_rbf
        current_rbf_start_date = unique_df.at[index, ("rbf_" + str(from_rbf))]

        # pass #current_rbf_start_date, "Danish"*300)
        diff = (datetime.datetime.today() - current_rbf_start_date)
        
        unique_df.at[index, "current_month"] = int(diff.days/30)
        unique_df.at[index, "current_day"] = diff.days

    df = unique_df

    # temp_df.drop(['VILLAGE', 'STATE', 'COMMUNITY HEALTH CENTER', 'BLOCK', 'PRIMARY HEALTH CENTER', 'DISTRICT', 'SUB CENTER'], axis = 1, inplace = True)
    
    # df = add_Ctype(df)

    df.drop(['VILLAGE', 'STATE', 'COMMUNITY HEALTH CENTER', 'BLOCK', 'PRIMARY HEALTH CENTER', 'DISTRICT', 'SUB CENTER'], axis = 1, inplace = True)
    committee_frame = retrieve_frame("committees", default_order)

    df = pd.merge(committee_frame, 
                    df,
                    on='core_orgUnit', 
                    how='left')

    del committee_frame
    rbf_heads = []
    for i in range(0,16):
        rbf_heads.extend(["rbf_%s" %i, "rbf_%s_status" %i])

    df = df[default_order + ['otg_year', 'otg_month', 'otg_day', "current_rbf", "current_day", "current_month", "completed_rbf", "ongoing_rbf"] + rbf_heads]
    # df = df[default_order + ['otg_year', 'otg_month', 'otg_day', "current_rbf", "current_day", "current_month"] + ["rbf_%s" %i for i in range(0,11) ] + ["rbf_%s_status" %i for i in range(0,11) ] ]
    # df = add_Ctype(df)
    # df[""] = df["rbf_0"]

    verticle_rbf_manager = []

    verticle_rbf_array_set = default_order + ['otg_year', 'otg_month', 'otg_day', "current_rbf", "current_day", "current_month", "completed_rbf", "ongoing_rbf"]
    for index, row in df.iterrows():
        for i in range (0, 16):
            col_name        = f"rbf_{i}"
            col_status      = f"rbf_{i}_status"
            temp_info = {}
            for attr  in verticle_rbf_array_set:
                temp_info[attr] = row[attr]

            temp_info["rbf_cycle"] = i
            temp_info["rbf_cycle_date"] = row[col_name]
            temp_info["rbf_cycle_status"] = row[col_status]

            verticle_rbf_manager.append(temp_info)

    verticle_rbf_manager = pd.DataFrame(verticle_rbf_manager)
    pass #verticle_rbf_manager)
    store_dataframe(verticle_rbf_manager, "verticle_rbf_Manager")


    # df['OTG Date']
    df["expected_rbf_complete"] = datetime.datetime.today()

    date_diff = (df['expected_rbf_complete'] - df['rbf_0']).dt.days/184

    df['expected_rbf_complete'] = np.floor(date_diff)
    df['expected_rbf_registered'] = np.ceil(date_diff)
    df['actual_rbf_complete']   = df['current_rbf'] + 1


    df['is_lagging'] = df['expected_rbf_complete'] - df['actual_rbf_complete']


    for index, row in df.iterrows():
        info = "On Time"
        if row["is_lagging"] > 0:
            info = "Lagging"

        df.loc[index, "is_lagging"] = info

    # df['is_lagging']=df['is_lagging'].mask(df['is_lagging'].gt(0), "Lagging")

    # df['is_lagging']=df['is_lagging'].mask(df['is_lagging'].lt(0), "On Time")

    # df['is_lagging']=df['is_lagging'].mask(df['is_lagging'].eq(0), "On Time")












    store_dataframe(df, "rbf_Manager")
    # Six Month Expense
    df = retrieve_frame("Six_Monthly_Expenditure")

    df = caste_to_int(df, ["Approved Budget","Six monthly Expenditure (Rs.)","Balance in Total","Quarter 1 Expenditure","Quarter 2 Expenditure","RBF Cycle"])
    # pass #df.dtypes)

    # df = add_Ctype(df)
    # df["ctype"] = df.apply(lambda x: committee_type_generate(x), axis=1)

    df = pd.merge(temp_df[['Name of Committee', 'ctype', 'core_orgUnit']], 
                    df,
                    on='core_orgUnit', 
                    how='inner')

    df["activity_type"] = df.apply(lambda x: "Not Approved" if (x["Approved Budget"] == 0) else "Approved" , axis=1)

    df.rename( columns={"Six monthly Expenditure (Rs.)": "Six monthly Expenditure (Rs)"}, inplace=True)
    store_dataframe(df, "six_monthly_expenditure")


    fund_status_frame(temp_df[['Name of Committee', 'ctype', 'core_orgUnit']])

    df = retrieve_frame("fund_status_and_siz_month_joint")

    # date filter on rbf
    # df = df[(df['RBF Amount Date'] <= "2020-03-01")]

    # df = df[(df['RBF Amount Date'] > "2020-03-31")]

    df.drop(['DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE'], axis=1, inplace=True)

    df = pd.merge(  x[['Name of Committee', 'ctype', 'core_orgUnit', 'RBF Cycle' , 'DISTRICT', 'BLOCK', 'COMMUNITY HEALTH CENTER', 'PRIMARY HEALTH CENTER', 'SUB CENTER', 'VILLAGE']], 
                    df,
                    on=['core_orgUnit','RBF Cycle'],
                    how='left'
                    )

    x = df.groupby(["RBF Cycle"])[["event_status"]].count().to_dict()
    for rbf_cycle, rbf_count in x["event_status"].items():
        if rbf_count == 0:
            df = df.drop(df[(df["RBF Cycle"] == rbf_cycle)].index).reset_index(drop=True)

    df = df.drop_duplicates(subset=["RBF Cycle", "core_orgUnit"], keep="last").reset_index(drop=True)
    store_dataframe(df, "fund_status_report")
    # Function call of report specific frames
    rbf_wise_fund_and_expense()
    activity_cat_wise_fund_and_expense()
    ctype_wise_fund_and_expense()
    rbf_stage_complition_counts_frame()
 
def rbf_wise_fund_and_expense():
    fund_status = retrieve_frame("fund_status_report")
    nhp_report = retrieve_frame("nhp_report")
    df = pd.merge(fund_status,nhp_report,on=['core_orgUnit',"RBF Cycle"])
    # df = df[(df['RBF Amount Date'] <= "2020-03-01")]
    
    rbf_wise_fund_and_expense_df = pd.DataFrame()
    for rbf_cycle in range((df['RBF Cycle'].max())+1):
        instant_df = (df[df['RBF Cycle'] == rbf_cycle][["core_orgUnit","RBF Amount","rbf_started_on", "RBF Amount Date", "Six monthly Expenditure (Rs)"]].rename(columns={"RBF Amount": "RBF " + str(rbf_cycle) + " Fund Released","rbf_started_on" : "RBF " +str(rbf_cycle) + " Cycle Start Date","RBF Amount Date": "RBF " + str(rbf_cycle)  + " Amount Date", "Six monthly Expenditure (Rs)": "RBF "+ str(rbf_cycle) + " Utilization"}))
        if rbf_wise_fund_and_expense_df.empty:
            rbf_wise_fund_and_expense_df = instant_df
        else:
            rbf_wise_fund_and_expense_df = pd.merge(rbf_wise_fund_and_expense_df, instant_df, on=['core_orgUnit'])

    rbf_manager = retrieve_frame("rbf_Manager", ["Name of Committee","ctype","DISTRICT", "BLOCK","current_rbf", "core_orgUnit"])
    rbf_wise_fund_and_expense_df = pd.merge(rbf_manager, rbf_wise_fund_and_expense_df, on=['core_orgUnit'])
    store_dataframe(rbf_wise_fund_and_expense_df.reset_index(drop=True), "rbf_wise_fund_and_expense")

def activity_cat_wise_fund_and_expense():
    df = retrieve_frame("fund_status_report")

    def rename(col):
        if isinstance(col, tuple):
            col = '_'.join(str(c) for c in col)
        return col

    x = pd.pivot_table(df.rename(columns={"Approved Budget": "Planned", "Six monthly Expenditure (Rs)":"Utilization"}), values=['Planned', 'Utilization'], index=["Name of Committee","ctype","core_orgUnit","RBF Cycle", "RBF Amount", "RBF Amount Date","DISTRICT","BLOCK","COMMUNITY HEALTH CENTER","PRIMARY HEALTH CENTER","SUB CENTER","VILLAGE"],

                    columns=['Activity Category'], aggfunc=np.sum, fill_value=0)
    x.columns = map(rename, x.columns)
    store_dataframe(x.reset_index(), "activity_cat_wise_fund_and_expense")

def ctype_wise_fund_and_expense():
    df = retrieve_frame("fund_status_report")
    df = df.groupby(["DISTRICT", 'ctype'])[["RBF Amount", "Six monthly Expenditure (Rs)"]].sum().reset_index()

    district_wise_fund_and_expense_df = pd.DataFrame()
    for ctype in ["VHC", "HSCMC", "HCMC"]:
        instant_df = df[df['ctype'] == ctype][["DISTRICT", "RBF Amount", "Six monthly Expenditure (Rs)"]].rename(columns={"RBF Amount": ctype + " Fund Released", "Six monthly Expenditure (Rs)": ctype + " Utilization"})

        if district_wise_fund_and_expense_df.empty:
            district_wise_fund_and_expense_df = instant_df
        else:
            district_wise_fund_and_expense_df = pd.merge(district_wise_fund_and_expense_df, instant_df, on=['DISTRICT'])

        pass #instant_df)
        pass #district_wise_fund_and_expense_df)

    store_dataframe(district_wise_fund_and_expense_df.reset_index(drop=True), "district_wise_fund_and_expense")  

def rbf_stage_complition_counts_frame():
    df = retrieve_frame("nhp_report")
    stages = [
                "Action_Plan",
                "Fund_Status",
                "IPR_-_1",
                "DVR_-_1",
                "IPR_-_2",
                "DVR_-_2",
                "Six_Monthly_Expenditure"
                ]
    rbf_stage_complition_counts_df = pd.DataFrame()
    for rbf_cycle in range((df['RBF Cycle'].max())+1):
        instant_df = (df[df['RBF Cycle'] == rbf_cycle][ (["core_orgUnit",] + stages) ])
        for index, row in instant_df.iterrows():
            completed = 0
            for stage in stages:
                if not pd.isna(row[stage]):
                    completed += 1
            attr_name = "RBF " + str(rbf_cycle) + " Completed"      
            instant_df.loc[index, attr_name] = completed
        instant_df = instant_df[["core_orgUnit", attr_name]]

        if rbf_stage_complition_counts_df.empty:
            rbf_stage_complition_counts_df = instant_df
        else:
            rbf_stage_complition_counts_df = pd.merge(rbf_stage_complition_counts_df, instant_df, on=['core_orgUnit'])

    rbf_manager = retrieve_frame("rbf_Manager", ["Name of Committee","ctype","DISTRICT","rbf_0", "core_orgUnit"])
    # committee_df = retrieve_frame("committees", ["Name of Committee","ctype","DISTRICT","core_orgUnit"])
    rbf_stage_complition_counts_df = pd.merge(rbf_manager, rbf_stage_complition_counts_df, on=['core_orgUnit'])
    rbf_stage_complition_counts_df.rename(columns={"rbf_0":"rbf_strat_date"})
    store_dataframe(rbf_stage_complition_counts_df.reset_index(drop=True), "rbf_stage_complition_counts")

def fund_status_frame(committee_df):
    fund_status_frame = retrieve_frame("Fund_Status")
    integer_col = ["RBF Amount", "Interest Credited from Bank - Amount", "Interest Credited from Bank Q2 - Amount", "Previous balance - Amount", "Community Contribution Amount", "Total Fund - Amount" ,"RBF Cycle"]
    fund_status_frame = caste_to_int(fund_status_frame, integer_col)

    fund_status_frame["RBF Amount"].replace(0, np.nan, inplace=True)
    six_monthly_expenditure_frame = retrieve_frame("Six_Monthly_Expenditure")

    six_monthly_expenditure_frame.rename(columns={"Bank charges (G)":"Bank charges"}, inplace=True)

    # pass #six_monthly_expenditure_frame.columns)
    # exit()

    integer_col = ["Approved Budget","Six monthly Expenditure (Rs.)","Balance in Total","Quarter 1 Expenditure","Quarter 2 Expenditure", "Bank charges", "RBF Cycle"]
    six_monthly_expenditure_frame = caste_to_int(six_monthly_expenditure_frame, integer_col)
    six_monthly_expenditure_frame.rename( columns={"Six monthly Expenditure (Rs.)": "Six monthly Expenditure (Rs)"}, inplace=True)
    # six_monthly_expenditure_frame = six_monthly_expenditure_frame.groupby(["core_orgUnit", "RBF Cycle"])["Approved Budget","Six monthly Expenditure (Rs)","Balance in Total","Quarter 1 Expenditure","Quarter 2 Expenditure"].sum().reset_index()
    
    f = {"Approved Budget":"sum","Six monthly Expenditure (Rs)":"sum","Balance in Total":"sum","Quarter 1 Expenditure":"sum","Quarter 2 Expenditure":"sum" ,'Bank charges': 'first', "Activity Category": 'first', "Activities (approved in the Action Plan)":'first'}
    
    # temp = six_monthly_expenditure_frame.groupby(["core_orgUnit", "RBF Cycle"], as_index=False).agg(f).reset_index(drop=True)
    
    temp = pd.merge(fund_status_frame, 
                                six_monthly_expenditure_frame[list(f.keys()) + ["core_orgUnit", "RBF Cycle"]],
                                # six_monthly_expenditure_frame[list(f.keys())],
                                on=['core_orgUnit', 'RBF Cycle'], 
                                how='left'
                                ).reset_index(drop=True)

    temp["activity_type"] = temp.apply(lambda x: "Not Approved" if (x["Approved Budget"] == 0) else "Approved" , axis=1)
    temp = pd.merge(committee_df, 
                    temp,
                    on=['core_orgUnit'], 
                    how='left'
                    ).reset_index(drop=True)


    temp["count"] = temp.groupby(['core_orgUnit', 'RBF Cycle']).core_orgUnit.transform("size")

    temp["NHP Fund"] = temp["RBF Amount"]/temp["count"]


    temp["total_fund_amount_parted"] = temp["Total Fund - Amount"]/temp["count"]

    # temp = temp.groupby(['core_orgUnit', 'RBF Cycle'])['core_orgUnit'].transform("count").reset_index(drop=True)
                                
    store_dataframe(temp, "fund_status_with_six_month_expenditure")

    # f = {"Approved Budget":"sum","Six monthly Expenditure (Rs)":"sum","Balance in Total":"sum","Quarter 1 Expenditure":"sum","Quarter 2 Expenditure":"sum" ,'Bank charges': 'first'}
    six_monthly_expenditure_frame = six_monthly_expenditure_frame.groupby(["core_orgUnit", "RBF Cycle"], as_index=False).agg(f).reset_index(drop=True)


    fund_status_frame = pd.merge(fund_status_frame, 
                                six_monthly_expenditure_frame,
                                on=['core_orgUnit', 'RBF Cycle'], 
                                how='left'
                                )

    # fund_status_frame = pd.merge(committee_df,
    #                                 fund_status_frame,
    #                                 on=['core_orgUnit'],
    #                                 )

    # fund_status_frame = sanitize_column(fund_status_frame) 

    store_dataframe(fund_status_frame, "fund_status_and_siz_month_joint")

def add_committee_audit(committee_frame):
    r = requests.get("https://www.nagalandhealthproject.org/nhpcms-test/getcommittee.php")
    # pass # r.status_code, r.json() )
    results = []
    for one_row in r.json():
        # pass #one_row["dhis_id"])
        final_row = {}
        final_row["dhis_id"]        = one_row["dhis_id"]
        final_row["audit_info"]     = json.dumps(one_row["cycle"], indent=4)

        for f_cycle_name, comments in one_row["cycle"].items():
            for col in ["plan_start_date", "plan_end_date", "actual_start_date", "actual_end_date"]:
                final_row[f_cycle_name + "_" + col] = comments[col]

            for idx, cmt in enumerate(comments["comment"]):
                for cmt_col in ["comment", "category_type", "compliance"]:
                    final_row[f_cycle_name + "_" + cmt_col + "_" + str(idx)] = cmt[cmt_col]
        results.append(final_row)

    df = pd.DataFrame(results).rename(columns={"dhis_id":"core_orgUnit"})

    df = df.set_index('core_orgUnit')
    committee_frame = committee_frame.set_index('core_orgUnit')
    result = pd.merge(committee_frame, df, how="left", on="core_orgUnit").reset_index()
    # result = pd.concat([committee_frame, df], axis=1).reset_index()
    # result = pd.concat([committee_frame, df], axis=1).reindex(committee_frame.index)
    return result
    # pass #df)
    # with open("danish.json", 'w') as wrt:
    #     wrt.write(json.dumps(results, indent=4))
    # pass #results)



        # for idx, one_cycle in enumerate(one_row["cycle"]):
        #     for col in ["plan_start_date", "plan_end_date", "actual_start_date", "actual_end_date"]:
        #         final_row["cycle_" + str(idx) + "_" + col ] = one_cycle[col]

        #     for idx, comment in enumerate(one_cycle["comment"]):
        #         for cmt_col in ["comment", "catetype_id", "compliance"]:
        #             final_row["cycle_" + str(idx) + "_" + cmt_col ] = comment[cmt_col]
        #     pass #one_cycle)
        #     pass #"= = ="*20)

def split_date_to_frame(df, cols):
    # col = 'dob'
    for col in cols:
        df[col] = pd.to_datetime(df[col], errors='ignore')
        # df[col]  = df[col].fillna(pd.to_datetime( datetime.date.today() ))
        df[col+'_year'] = df[col].dt.year
        df[col+'_month'] = df[col].dt.month
        df[col+'_day'] = df[col].dt.day

def HRMIS_Generation(request, profile):
    # pass
    hr_data     = get_data_from_hrmis("https://nagalandhealthproject.org/hrmis-stage/hrmis_data")
    hr_data     = hr_data["data"]
    df          = pd.DataFrame(hr_data).astype(str)

    df.replace(r'^\s*$', "N/A", regex=True, inplace=True)

    column_cast_to_int = []
    for col in df.columns:
        df[col] = df[col].str.strip()
        df.rename(columns={col: col.replace("_name", "")}, inplace=True)
        if "_id" in col:
            column_cast_to_int.append(col)

    # df.rename(columns={"district": "DISTRICT", "block": "BLOCK"}, inplace=True)

    df = caste_to_int(df, column_cast_to_int)

    df.loc[df['facility_type'] == "N/A", ["facility_type"]] = "Directorate"
    # df = split_date_to_frame(df, ['dob', 'joining_date'])

    facility_gis = requests.get("https://nagalandhealthproject.org/nhp/cron_json/geo_facility.php").json()
    
    new_facility_gis = []
    for id, row in facility_gis.items():
        # pass #id, row)    
        # print(row["facility_type"], row["certificate_type"])
        new_facility_gis.append({
            "facility_id"       :   row["facility_id"],
            "latitude"          :   row["latitude"],
            "longitude"         :   row["longitude"],
            "facility_type_id"  :   row["facility_type_id"],

            "facility_type"     :   row["facility_type"],
            "certificate_type"  :   row["certificate_type"],

        })

    gis_df = pd.DataFrame(new_facility_gis)
    gis_df = caste_to_int(gis_df, ['facility_type_id', 'facility_id'])
    
    df = pd.merge(df, gis_df, on=['facility_type_id', 'facility_id'], how='left')

    df = caste_to_int(df, ["certificate_type"])
    # df["certificate_type"].fillna("", inplace=True)

    store_dataframe(df, "employees")
    df.drop_duplicates(subset=["facility_type_id", "facility_id" ], inplace=True)

    df.drop(columns=[ "employee_code", "departmental_employee_code", "employee", "certificate_type" ], inplace=True )
    store_dataframe(df.reset_index(drop=True) , "facilities")


    df = pd.DataFrame( facility_gis.values() )

    store_dataframe(df.reset_index(drop=True) , "facilities_next")

    return {}
    
def get_data_from_hrmis(url, payload={}):
    payload     =   {}
    usrPass     = "nhp:nhp@2021"
    b64Val      = base64.b64encode(usrPass.encode("utf-8")).decode("utf-8")
    # b64Val      = "bmhwOm5ocEAyMDIx"
    pass #b64Val, "==========")
    r=requests.post(url, headers={"Authorization": "Bearer %s" % b64Val, "content-type": "application/json"}, data=payload)
    return  r.json()

def get_data_from_hmis(url, payload):
    params     =   {
                        'api_token'         :   'Fpv3HHYR6MrVWv3dG',
                    }
    payload.update(params)

    # print(payload)
    # r = requests.get('https://nagalandhealthproject.org/hmis/data_entry/hmis_import_data.php', params=payload)
    r = requests.get(url, params=payload)
    # print(r.url)
    return r.json()

def prepare_get_hmis_geo():

    params     =   {
                        'api_token'         :   'Fpv3HHYR6MrVWv3dG',
                    }
    r = requests.get('https://nagalandhealthproject.org/hmis/data_entry/dst_block_master.php', params=params)
    records = r.json()["master_data"]
    result = []
    for record  in records:
        temp = {
            "district_id"   : record["id"],
            "district"      : record["name"],
            }
        for r in record["block_list"]:
            x = {**temp, **{}}
            x["block_id"]    = r["id"]
            x["block"]       = r["name"]

            result.append(x)
    df = pd.DataFrame(result)

    df_block_population = pd.read_excel(settings.CORE_FILE_PATH + "/Block Population.xls", header =0)
    df_block_population.rename(columns={"District":"district", "Block Name": "block"}, inplace=True)
    df_block_population.drop(columns=['Sl.No.'], inplace=True)
    df_block_population = caste_to_int(df_block_population, ["Population"])


    df = pd.merge(df, df_block_population, on=['district', 'block'], how='left').reset_index(drop=True)

    # df["state"] = "Nagaland"

    store_dataframe(df, "health_index_geo")

def get_hmis_category():
    params     =   {
                        'api_token'         :   'Fpv3HHYR6MrVWv3dG',
                    }
    r = requests.get('https://nagalandhealthproject.org/hmis/data_entry/hmis_category_master.php', params=params)
    return r.json()

def prepare_frame_hmis(category_info):
    facility_level  =   {
            '1' : 'district',
            '2' : 'block'
        }
    for f_level, f_name in facility_level.items():

        s_date = datetime.datetime.strptime("2019-01-01", "%Y-%m-%d").date()
        e_date = datetime.datetime.now().date()

        facility_level_data_set = []
        while(s_date <= e_date):
            a_month = relativedelta.relativedelta(months=1)
            s_date = s_date + a_month
            category_id = int(category_info.get("id", 0))
            payload     =   {
                                'facility_level'    :   f_level,
                                'year'              :   s_date.year,
                                'month'             :   s_date.month,
                            }
            if category_id:
                payload["category_id"] = category_id
            data = get_data_from_hmis('https://nagalandhealthproject.org/hmis/data_entry/hmis_import_data.php', payload)
            for idx, geo_data in data["hmis"].items():

                row_info = { f_name : geo_data["name"]}

                if geo_data["count"]:
                    for one_attr in geo_data["hmis_data"]:
                        row_info[one_attr["item_name"]] = int(one_attr["value"])

                    row_info["month"] = s_date.month
                    row_info["year"]  = s_date.year
                    row_info["time"]  = s_date

                    facility_level_data_set.append(row_info)
        df = pd.DataFrame(facility_level_data_set)
        if df.empty:
            print('DataFrame is empty!')
        else:
            try:
                df["time"] = pd.to_datetime(df["time"], errors ="coerce")
            except:
                pass
            category_name = ""
            if category_id:
                category_name = re.sub(r"[^a-zA-Z0-9]","_",category_info["name"])
            store_dataframe(df, "hmis_"+ f_name + "_" + category_name )

def prepare_frame_hmis_plhiv():
    data = get_data_from_hmis("https://nagalandhealthproject.org/hmis/data_entry/hmis_plhiv_data.php", {})

    df = pd.DataFrame(data["response_data"])

    df = caste_to_int(df, ["male","female","child_male","child_female","ts_tg","total", "month", "year"])

    df.rename(columns={"district_name": "district", "block_name": "block"}, inplace=True)

    
    df[["district", "block"]] = df[["district", "block"]].fillna("")



    gb = ["district", "block", "year", "month"]
    cols = set(list(df.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if df[c].dtype == "float64":
            operations[c] = "sum"
    df = df.groupby(gb).agg(operations).reset_index(drop=True)

    df_block = df[df["block"] != ""]




    gb = ["district", "year", "month"]
    cols = set(list(df.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if df[c].dtype == "float64":
            operations[c] = "sum"
    df_district = df.groupby(gb).agg(operations).reset_index(drop=True)




    gb = ["year", "month"]
    cols = set(list(df.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if df[c].dtype == "float64":
            operations[c] = "sum"
    df_state = df.groupby(gb).agg(operations).reset_index(drop=True)


    df  = df_block.append(df_district, ignore_index=True).append(df_state, ignore_index=True)

    # gb = ["district", "block", "year", "month"]
    # cols = set(list(df.columns))-set(gb)
    # operations = {}
    # for g in gb:
    #     operations[g] = "first"
    # for c in cols:
    #     if df[c].dtype == "float64":
    #         operations[c] = "sum"
    # df = df.groupby(gb).agg(operations).reset_index(drop=True)
    # # print(df)


    # gb = ["year", "month"]
    # cols = set(list(df.columns))-set(gb)
    # operations = {}
    # for g in gb:
    #     operations[g] = "first"
    # for c in cols:
    #     if df[c].dtype == "float64":
    #         operations[c] = "sum"
    # df_state = df.groupby(gb).agg(operations).reset_index(drop=True)

    # df = df_state.append(df, ignore_index = True)

    df[["district", "block"]] = df[["district", "block"]].fillna("")

    store_dataframe(df, "hmis_plhiv_data")

def prepare_frame_hmis_tb_notify():
    data = get_data_from_hmis("https://nagalandhealthproject.org/hmis/data_entry/hmis_tb_notify.php", {})

    df = pd.DataFrame(data["response_data"])
    df = caste_to_int(df, ["total_notified", "total_outcome", "total_cured", "total_died", "treatment_complete", "treatment_failure", "year", "month"])
    
    df.rename(columns={"district_name":"district", "block_name": "block"}, inplace=True)

    df[["district", "block"]] = df[["district", "block"]].fillna("")

    gb = ["district", "block", "year", "month"]
    cols = set(list(df.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if df[c].dtype == "float64":
            operations[c] = "sum"
    df = df.groupby(gb).agg(operations).reset_index(drop=True)

    df_block = df[df["block"] != ""]




    gb = ["district", "year", "month"]
    cols = set(list(df.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if df[c].dtype == "float64":
            operations[c] = "sum"
    df_district = df.groupby(gb).agg(operations).reset_index(drop=True)




    gb = ["year", "month"]
    cols = set(list(df.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if df[c].dtype == "float64":
            operations[c] = "sum"
    df_state = df.groupby(gb).agg(operations).reset_index(drop=True)


    df  = df_block.append(df_district, ignore_index=True).append(df_state, ignore_index=True)
    
    # df = df.append(df_district, ignore_index=True)
    # df = df_state.append(df, ignore_index = True)

    df[["district", "block"]] = df[["district", "block"]].fillna("")



    store_dataframe(df, "hmis_tb_notify_data")

def prepare_frame_hmis_infra(category_info):
    facility_level  =   {
            '1' : 'District_Hospital',
            '2' : 'CHC',
            '3' : 'PHC',
            '4' : 'SC'
        }
    for f_level, f_name in facility_level.items():

        s_date = datetime.datetime.strptime("2019-01-01", "%Y-%m-%d").date()
        e_date = datetime.datetime.now().date()

        facility_level_data_set = []
        while(s_date <= e_date):
            a_month = relativedelta.relativedelta(months=1)
            s_date = s_date + a_month
            category_id = int(category_info.get("id", 0))
            payload     =   {
                                # 'facility_level'    :   f_level,
                                'facility_type'     :   f_level,
                                'year'              :   s_date.year,
                                'month'             :   s_date.month,
                            }
            if category_id:
                payload["category_id"] = category_id
            data = get_data_from_hmis("https://nagalandhealthproject.org/hmis/data_entry/hmis_facility_data.php", payload)

            if not data["hmis"]:
                continue

            for idx, geo_data in data["hmis"].items():

                # row_info = { f_name : geo_data["name"]}

                row_info = { "district" : geo_data["district_name"], "block": geo_data["block_name"], "facility_name": geo_data["facility_name"] }

                if geo_data["count"]:
                    for one_attr in geo_data["hmis_data"]:
                        row_info[str(one_attr["item_name"])] = one_attr["value"]

                    row_info["month"] = s_date.month
                    row_info["year"]  = s_date.year
                    row_info["time"]  = s_date

                    # print(row_info, "a a a a  aa  a")
                    facility_level_data_set.append(row_info)
        df = pd.DataFrame(facility_level_data_set)
        if df.empty:
            print('DataFrame is empty!')
        else:
            try:
                df["time"] = pd.to_datetime(df["time"], errors ="coerce")
            except:
                pass
            category_name = ""
            if category_id:
                category_name = re.sub(r"[^a-zA-Z0-9]","_",category_info["name"])
            store_dataframe(df, "hmis_infra_"+ f_name + "_" + category_name )

def generate_frame_health_index_dashboard():

    district_population = {
        "Dimapur " :     378811,
        "Kohima" :      267988,
        "Mon" :         250260,
        "Tuensang" :    196596,
        "Mokokchung" :  194622,
        "Wokha" :       166343,
        "Phek" :        163418,
        "Zunheboto" :   140757,
        "Peren" :       95219,
        "Kiphire" :     74004,
        "Longleng" :    50484
    }


    additional_col = [

        "Number of newborns having weight less than 2.5 kg",


        "Number of Maternal Deaths due to Bleeding",
        "Number of Maternal Deaths due to High fever",
        "Number of Maternal Deaths due to Abortion",
        "Number of Maternal Deaths due to Obstructed/prolonged labour",
        "Number of Maternal Deaths due to Severe hypertension/fits",
        "Number of Maternal Deaths due to Other Causes (including causes not known)"
    ]








    hmis_district_frame = retrieve_frame("hmis_district_")
    # hmis_district_frame["state"] = "Nagaland"



    # ============ Add missing Columns Start (District) ======================

    # hmis_block_frame["Number of newborns having weight less than 2.5 kg"] = 0
    availble_cols_district = hmis_district_frame.columns
    for c in additional_col:
        if c not in availble_cols_district:
            hmis_district_frame[c] = 0

    # ============ Add missing Columns End (District)  ======================


    # gb = ["district", "state", "time", "month", "year", "hash"]
    # cols = set(list(hmis_district_frame.columns))-set(gb)
    # operations = {}
    # for g in gb:
    #     operations[g] = "first"
    # for c in cols:
    #     operations[c] = "sum"
    # hmis_state_frame = hmis_district_frame.groupby(["time"]).agg(operations).reset_index(drop=True)


    # hmis_state_frame["district"] = ""

    # hmis_district_frame = hmis_state_frame.append(hmis_district_frame, ignore_index = True) 




    # df = pd.read_excel(settings.CORE_FILE_PATH + "/State Dashboard Indicators.xls", header =1)
    # df = (df[df["Data source"] == "HMIS Data"])

    # def check_columns_exist(col_set):
    #     all_col = hmis_district_frame.columns
    #     for col in col_set:
    #         if col in all_col:
    #             # print(col + " Found")
    #             pass
    #         else:
    #             # print(col + " Not Found")
    #             return False
    #     return True
    
    # Index(['S. No.', 'Domain', 'Sub-Domain', 'Indicator id', 'Indicator name',
    #        'Data source', 'Denominator', 'Numerator', 'Calculation'],
    #       dtype='object')

    # print(df.columns)
    # dynamic_df = hmis_district_frame
    # evaluate_indicators(hmis_district_frame)

    def evaluate_indicators(dynamic_df, geo_level):

        def check_columns_exist(col_set):
            all_col = dynamic_df.columns
            for col in col_set:
                if col in all_col:
                    # print(col + " Found")
                    pass
                else:
                    print(col + " X-X-X Not Found X-X-X")
                    # for c in all_col:
                    #     print(c)
                    return False
            return True



        df = pd.read_excel(settings.CORE_FILE_PATH + "/State Dashboard Indicators.xls", header =1)
        


        # indicator_definition = {}
        # for index, row in df.iterrows():
        #     indicator_definition[row["Indicator name"]] = row["Definition"]

        # print(indicator_definition)



        # df = (df[df["Data source"] == "HMIS Data"])

        result = dynamic_df[[ "state", "district", "district_id", "block", "block_id", "month", "time", "year"]]
        # result = dynamic_df[["month", "time", "year"]]
        unique_col = []


        # print(df[["Indicator name", "Definition"]])

        for index, row in df.iterrows():

            if str(row["Calculation"]) != "nan":
                # print(index, row)
                # unique_col.extend(row["Numerator"].split("{}"))
                # unique_col.extend(row["Denominator"].split("{}"))
                # print(row["Indicator name"])
                # print(row["Denominator"])
                # print(row["Numerator"])
                # print(re.split('\/|\+|\*', row["Calculation"]))

                N = row["Numerator"].split("{}")
                D = row["Denominator"].split("{}")
                if check_columns_exist(N) and check_columns_exist(D):
                    for i in range(len(N)):
                        row["Calculation"] = row["Calculation"].replace("##N["+str(i)+"]", 'dynamic_df["'+N[i]+'"]')

                    for i in range(len(D)):
                        row["Calculation"] = row["Calculation"].replace("##D["+str(i)+"]", 'dynamic_df["'+D[i]+'"]')
                    
                    # print(row["Calculation"], "=============")
                    result[row["Indicator name"]] = eval(row["Calculation"])
                    # print(result[row["Indicator name"]])
                    print(row["Indicator name"], "= == ="*10)
        # print(result)
        # store_dataframe(result, geo_level+"_health_index_dashboard")
        return result


    hmis_geo = retrieve_frame("health_index_geo")

    # hmis_district_frame = (pd.merge(hmis_district_frame, hmis_geo, on=['district'], how='left'))
    # hmis_district_frame[["district", "district_id"]] = hmis_district_frame[["district", "district_id"]].fillna("")
    # hmis_district_frame["block"] = ""
    # hmis_district_frame["block_id"] = ""



    

    # evaluate_hmis_district_frame = evaluate_indicators(hmis_district_frame, "district")
    # hmis_district_frame = (pd.merge(hmis_district_frame, hmis_geo, on=['district'], how='left'))
    # hmis_district_frame[["district", "district_id"]] = hmis_district_frame[["district", "district_id"]].fillna("")
    # hmis_district_frame["block"] = ""
    # hmis_district_frame["block_id"] = ""
    store_dataframe(hmis_district_frame, "district_health_index_dashboard")

    
    
    
    
    
    hmis_block_frame = retrieve_frame("hmis_block_")
    # hmis_block_frame["state"] = "Nagaland"
    # hmis_block_frame = (pd.merge(hmis_block_frame, hmis_geo, on=['block'], how='left'))


    # ============ Add missing Columns Start (Block)  ======================

    # hmis_block_frame["Number of newborns having weight less than 2.5 kg"] = 0
    availble_cols_block = hmis_block_frame.columns
    for c in additional_col:
        if c not in availble_cols_block:
            hmis_block_frame[c] = 0

    # ============ Add missing Columns End (Block)  ======================




    # evaluate_hmis_block_frame = evaluate_indicators(hmis_block_frame, "block")



    # hmis_block_frame = (pd.merge(hmis_block_frame, hmis_geo, on=['block'], how='left'))
    store_dataframe(hmis_block_frame, "block_health_index_dashboard")


    # cols = ["state", "district", "block", "time", "month", "year", "district_id", "block_id"]
    final_frame = hmis_district_frame.append(hmis_block_frame, ignore_index = True) 
    # for col in final_frame.columns:
    #     if col not in cols:
    #         cols.append(col)
    # final_frame = final_frame.reindex(cols, axis=1)


    # district_population = hmis_geo.groupby(["district"]).agg({"district":"first",  "Population": "sum"}).reset_index(drop=True)

    # print(district_population)

    # print(final_frame)
    

    final_frame = (pd.merge(final_frame, hmis_geo, on=['block'], how='left'))


    # gb = ["district", "state", "time", "month", "year", "hash"]
    # cols = set(list(hmis_district_frame.columns))-set(gb)
    # operations = {}
    # for g in gb:
    #     operations[g] = "first"
    # for c in cols:
    #     operations[c] = "sum"
    # hmis_state_frame = hmis_district_frame.groupby(["time"]).agg(operations).reset_index(drop=True)



    # print(final_frame[final_frame["district_id"].isnull()])

    final_frame["FRU"] = 0

    for index, row in final_frame.iterrows():

        if isinstance(row["district_id"], float):
            final_frame.loc[index, "district_y"] = row["district_x"]
            final_frame.loc[index, "Population"] = district_population[row["district_x"]]

        if row["block"]:
            if row["Total C -Section deliveries performed"] >= 3:
                final_frame.loc[index, "FRU"] = 1
        else:
            if row["Total C -Section deliveries performed"] >= 6:
                final_frame.loc[index, "FRU"] = 1


    final_frame.rename(columns={"district_y":"district"}, inplace=True)

    final_frame.drop(columns=["district_x", "hash_x", "hash_y"], inplace=True)

    # final_frame[["district", "block"]] = final_frame[["district", "block"]].fillna("")


    store_dataframe(final_frame, "health_index_dashboard_values")


    # final_frame = evaluate_hmis_district_frame.append(evaluate_hmis_block_frame, ignore_index = True)

    final_frame["state"] = "Nagaland"


    gb = ["state", "time", "month", "year", "hash"]
    cols = set(list(final_frame.columns))-set(gb)
    operations = {}
    for g in gb:
        operations[g] = "first"
    for c in cols:
        if final_frame[c].dtype == "float64":
            operations[c] = "sum"
    hmis_state_frame = final_frame.groupby(["time"]).agg(operations).reset_index(drop=True)

    
    final_frame = final_frame.append(hmis_state_frame, ignore_index = True) 

    final_frame[["district", "block"]] = final_frame[["district", "block"]].fillna("")


    final_frame["Total number of children 9-11 months"] = (((final_frame["Population"]*14.8)/1000)/12)*3
    final_frame["Number of Estimated PLHIVs who need ART treatment"] = (final_frame["Population"]*.0145)

    
    # =========================== Adding Block which is missing start===========================
    tmp = final_frame[(final_frame["district"] != "") & (final_frame["block"] != "")]
    availble_block = list(tmp["block"].values)
    tmp = hmis_geo[~hmis_geo["block"].isin(availble_block)].reset_index(drop=True)
    tmp.drop(columns=["Population", "hash"], inplace=True)
    tmp["state"] = "Nagaland"

    print(tmp, "a a a"*20, type(availble_block))

    final_frame = final_frame.append(tmp, ignore_index=True)

    # =========================== Adding Block which is missing end ===========================

    

    

    # =========================== PLHIVE Data INTEGERATION start ===========================
    temp_frame = retrieve_frame("hmis_plhiv_data")
    temp_frame.drop(columns=["hash"], inplace=True)
    gb = ["district", "block", "year", "month"]

    for c in temp_frame.columns:
        if c not in gb:
            temp_frame.rename(columns={c:"plhiv_"+c}, inplace=True)

    final_frame =  pd.merge(    
                                final_frame,
                                temp_frame,
                                on=gb,
                                how='left'
                            ).reset_index(drop=True)

    final_frame.rename(columns={ "plhiv_total": "Total number of PLHIVs are on ART treatment"}, inplace=True)
    # =========================== PLHIVE Data INTEGERATION end ===========================



    # =========================== hmis_tb_notify Data INTEGERATION start ===========================
    temp_frame = retrieve_frame("hmis_tb_notify_data")

    temp_frame.drop(columns=["hash"], inplace=True)
    gb = ["district", "block", "year", "month"]

    for c in temp_frame.columns:
        if c not in gb:
            temp_frame.rename(columns={c:"tb_notify_"+c}, inplace=True)

    # "tb_notify_total_cured", "tb_notify_treatment_failure", "tb_notify_treatment_complete", "tb_notify_total_died", "tb_notify_total_outcome", "tb_notify_total_notified"
    
    final_frame =  pd.merge(    
                                final_frame,
                                temp_frame,
                                on=gb,
                                how='left'
                            ).reset_index(drop=True)

    # =========================== hmis_tb_notify Data INTEGERATION end ===========================




    # =========================== PHC INFRA Data INTEGERATION start ===========================

    hmis_infra_PHC = retrieve_frame("hmis_infra_PHC_", ["block", "month", "year", "Emergency services (24 Hours) (Yes/No)"])

    hmis_infra_PHC['Emergency services (24 Hours) (Yes/No)'] = hmis_infra_PHC['Emergency services (24 Hours) (Yes/No)'].replace(['Yes'], 1)
    hmis_infra_PHC['Emergency services (24 Hours) (Yes/No)'] = hmis_infra_PHC['Emergency services (24 Hours) (Yes/No)'].replace(['No'], 0)

    hmis_infra_PHC = (pd.merge(hmis_infra_PHC, hmis_geo[["district", "block"]], on=['block'], how='left'))
    hmis_infra_PHC["state"] = "Nagaland"

    hmis_infra_PHC["Total PHCs"] = 0

    state_df = hmis_infra_PHC.groupby(["state", "month", "year"]).agg({    
                                    "Emergency services (24 Hours) (Yes/No)" : "sum",
                                    "Total PHCs" : "size"
                                    }).reset_index()

    district_df = hmis_infra_PHC.groupby(["district", "month", "year"]).agg({
                                    "Emergency services (24 Hours) (Yes/No)" : "sum",
                                    "Total PHCs" : "size"
                                    }).reset_index()


    block_df = hmis_infra_PHC.groupby(["block", "month", "year"]).agg({
                                    "district" : "first",
                                    "Emergency services (24 Hours) (Yes/No)" : "sum",
                                    "Total PHCs" : "size"
                                    }).reset_index()

    # print(block_df)

    state_df = state_df.append(district_df, ignore_index = True)

    state_df = state_df.append(block_df, ignore_index = True)

    state_df["state"] = "Nagaland"

    hmis_infra_PHC = state_df

    # hmis_infra_PHC = hmis_infra_PHC.append(state_df, ignore_index = True)

    hmis_infra_PHC[["district", "block"]] = hmis_infra_PHC[["district", "block"]].fillna("")

    store_dataframe(hmis_infra_PHC, "hmis_infra_PHC")

    
    

    final_frame =  pd.merge(    
                                final_frame,
                                hmis_infra_PHC,
                                on=["state", "district", "block", "month", "year"],
                                how='left'
                            ).reset_index(drop=True)


    # =========================== PHC INFRA Data INTEGERATION end ===========================




    # =========================== DH/CHC/PHC INTEGERATION start ===========================

    # def __generate_frame_for(frame_name, fru_columns):
    #     temp_frame = retrieve_frame(frame_name, ["district", "block", "month", "year", fru_columns])

    #     temp_frame.rename(columns={fru_columns: "FRU"}, inplace=True)

    #     temp_frame['FRU'] = temp_frame['FRU'].replace(['Yes'], 1)
    #     temp_frame['FRU'] = temp_frame['FRU'].replace(['No'], 0)
    #     return temp_frame

    
    # temp_frame = __generate_frame_for("hmis_infra_District_Hospital_", "Emergency (Accident & other emergency) (Casualty 24X7 basis)")
    # temp_frame = temp_frame.append(__generate_frame_for("hmis_infra_CHC_", "24 - hour delivery services including normal and assisted deliveries (Yes/No)"), ignore_index=True)
    # temp_frame = temp_frame.append(__generate_frame_for("hmis_infra_PHC_", "Emergency services (24 Hours) (Yes/No)"), ignore_index=True)

    
    # final_frame["Total C -Section deliveries performed"]

    # =========================== DH/CHC/PHC INTEGERATION end ===========================

    




    # =========================== PHC INFRA Data INTEGERATION start ===========================

    temp_framem = retrieve_frame("hmis_infra_District_Hospital_", ["district", "month", "year", "CARDIAC INVESTIGATIONS (Yes/No)" ])

    temp_col =  "CARDIAC INVESTIGATIONS (Yes/No)"

    temp_framem.loc[~temp_framem[temp_col].isnull(), [temp_col]] = 1  # not nan
    temp_framem.loc[temp_framem[temp_col].isnull(), [temp_col]] = 0   # nan

    temp_framem["state"] = "Nagaland"

    temp_framem["Total number of districts"] = 1


    state_temp_framem = temp_framem.groupby(["state", "month", "year"]).agg({
                                    "CARDIAC INVESTIGATIONS (Yes/No)" : "sum",
                                    "Total number of districts" : "size"
                                    }).reset_index()

    temp_framem = state_temp_framem.append(temp_framem, ignore_index=True)

    temp_framem["block"] = ""
    temp_framem["state"] = "Nagaland"

    temp_framem[["district", "block"]] = temp_framem[["district", "block"]].fillna("")

    print(temp_framem)
    
    final_frame =  pd.merge(    
                                final_frame,
                                temp_framem,
                                on=["state", "district", "block", "month", "year"],
                                how='left'
                            ).reset_index(drop=True)

    temp_framem["Total number of districts"].fillna("")

    final_frame.rename(columns={"CARDIAC INVESTIGATIONS (Yes/No)": "Total number of district Hospitals with functional CCU"}, inplace=True)

    

    # =========== End ===================================




    # ============================== Start =====================================


    temp_col =  "certificate_type"

    temp_framem = retrieve_frame("facilities_next", ["district", "block", temp_col])

    temp_framem = caste_to_int(temp_framem, [temp_col])
    temp_framem[temp_framem[temp_col] > 0][temp_col] = 1

    # temp_framem.loc[~[temp_framem[temp_col] != 0 ], [temp_col]] = 1  # not nan
    # temp_framem.loc[temp_framem[temp_col].isnull(), [temp_col]] = 0   # nan


    print(temp_framem[temp_col])
    temp_framem["state"] = "Nagaland"

    temp_framem["Total number of health facilities"] = 1


    state_temp_framem = temp_framem.groupby(["state"]).agg({
                                    temp_col : "sum",
                                    "Total number of health facilities" : "size"
                                    }).reset_index()


    district_temp_framem = temp_framem.groupby(["state", "district"]).agg({
                                    temp_col : "sum",
                                    "Total number of health facilities" : "size"
                                    }).reset_index()

                    
    block_temp_framem = temp_framem.groupby(["state", "district", "block"]).agg({
                                    temp_col : "sum",
                                    "Total number of health facilities" : "size"
                                    }).reset_index()

    # temp_framem = state_temp_framem.append(temp_framem, ignore_index=True)

    block_temp_framem = district_temp_framem.append(block_temp_framem, ignore_index=True)

    block_temp_framem = state_temp_framem.append(block_temp_framem, ignore_index=True)

    temp_frame = block_temp_framem

    temp_framem["block"] = ""
    temp_framem["state"] = "Nagaland"

    temp_framem[["district", "block"]] = temp_framem[["district", "block"]].fillna("")

    # temp_framem["Total number of health facilities"].fillna()
    temp_frame["certificate_type"].fillna(0)

    print(temp_frame, "aaaaaaaaaaaaa")

    temp_framem[["district", "block"]] = temp_framem[["district", "block"]].fillna("")
    
    final_frame =  pd.merge(    
                                final_frame,
                                temp_framem,
                                on=["state", "district", "block"],
                                how='left'
                            ).reset_index(drop=True)

    final_frame.rename(columns={"certificate_type":"Total number of health facilities with accreditation certificate"}, inplace=True)

    # ================================== End===================================


    # ========================= Start CHC grading ====================================
    numberic_cols   =        [
                                "Paediatrics",
                                "Anesthetist",
                                "Public Health Nurse",
                                "Staff Nurse",
                                "Eye Surgeon",
                                "Lab. Technician",
                                "Physician",
                                "Obstetrician / Gynaecologist",
                                "General Duty Medical Officer",
                                "ANM",
                                "General Surgeon"
                            ]

    boolean_col     =       [
                                "Separate public utilities for males and females (Yes/No)",
                                "Stand by facility (generator) available (Yes/No)",
                                "Operation Theatre available (Yes/No)",

                                "Whether two months supply of essential drugs available? (Available/Partially Available/Not Available)",
                                "Whether two months supply of essential vaccines available? (Available/Partially Available/Not Available)",
                                "Whether two months supply of essential contraceptives available? (Available/Partially Available/Not Available)",


                                "24 - hour delivery services including normal and assisted deliveries (Yes/No)",
                                "Emergency care of sick children (Yes/No)",
                                "Full range of family planning services including Laproscopic Services (Yes/No)",


                                "Is there a publicly displayed mechanism, whereby a complaint/grievance can be registered? (Yes/No)",
                                "Citizen's charter (Yes/No)",
                                "Constitution of Rogi Kalyan Samiti (Yes/No)",
                            ]               

    temp_frame = retrieve_frame("hmis_infra_CHC_")
    all_cols = temp_frame.columns

    temp_frame.fillna("No", inplace=True)

    for c in numberic_cols:
        if c not in all_cols:
            temp_frame[c] = 0

    temp_frame = caste_to_int(temp_frame, numberic_cols)

    # for c in boolean_col:
    #     if c not in all_cols:
    #         temp_frame[c] = 0
    #     else:
    #         temp_frame[c].fillna(0)
    #         print("danish")
    #         # print(temp_frame[temp_frame[c].str.contains("Yes")])
            
    #         # temp_frame[~temp_frame[c].str.contains("Yes")][c] = 1
    #         # temp_frame[temp_frame[c].str.contains("Yes")][c] = 1

    #         # temp_frame.loc[ [temp_frame[c].str.contains("Yes")].index, [c]] = 0
    #         temp_frame.loc[ ([temp_frame[c] != "Yes"]), [c]] = 0
    #         temp_frame.loc[ ([temp_frame[c] == "Yes"]), [c]] = 1


    # temp_frame = temp_frame[numberic_cols+boolean_col]

    store_dataframe(temp_frame, "temp")


    # ========================= End CHC grading ====================================










    store_dataframe(final_frame, "health_index_dashboard_values")




    final_frame = evaluate_indicators(final_frame, "district")





    final_frame["Total Fertility Rate (TFR)"] = 2.7
    final_frame["Under-five Mortality Rate (U5MR)"] = 33
    final_frame["Neonatal Mortality Rate (NMR)"] = 10.2


    final_frame["Proportion of specified type of facilities functioning as First Referral Unites (FRUs)"] = final_frame["Full immunization coverage (%)"]*3

    final_frame["Average number of days for transfer of Central National Health Mission (NHM) fund from State Treasury to implementation agency (Department/Society) based on all tranches of the last financial year"] = 52.4
    
    final_frame["Proportion of NHM funds utilized by the end of 3rd quarter"] = 225.47





    final_frame["Proportion of CHCs with grading above 3 points"] = 0

    for index, row in final_frame.iterrows():
        if row["district"] == "" and row["block"] == "":
            final_frame.loc[index, "Proportion of CHCs with grading above 3 points"]= 12.7
        elif row["district"] == "Kohima":
            final_frame.loc[index, "Proportion of CHCs with grading above 3 points"]= 55.4

    store_dataframe(final_frame, "health_index_dashboard")

def prepare_hmis_fund_status():
    data = get_data_from_hmis("https://nagalandhealthproject.org/hmis/data_entry/hmis_fund_status.php", {})
    df = pd.DataFrame(data["response_data"])
    store_dataframe(df, "hmis_fund_status")

def HMIS_Generation(request, profile):
    # prepare_frame_hmis({})
    # for category_info in get_hmis_category()["master_data"]:
    #     prepare_frame_hmis(category_info)

    # prepare_frame_hmis_infra({})

    # prepare_frame_hmis_plhiv()
    # prepare_frame_hmis_tb_notify()

    prepare_hmis_fund_status()
    prepare_get_hmis_geo()




    generate_frame_health_index_dashboard()
    return  {}
###################################################################################################################
###
###
### FRAMES FOR CAHN REPORTS 
### AUTHOR ABHISHEK AGRAWAL 
### DATE   1 JUNE 2021
###################################################################################################################

## frame used in 
def merged_nhp_rbf_manager():#Current RBF Status Frame 
    frame_path1 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "rbf_Manager")
    frame_path2 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "nhp_report")
    manager = pd.read_feather(frame_path1, use_threads=4, columns=None)
    report = pd.read_feather(frame_path2, use_threads=4, columns=None)
    manager = manager.merge(report,on='core_orgUnit',how="left")
    dropList=[]
    for cols in manager:
        if cols[-2:] == '_y':
            dropList.append(cols)
    manager.drop(columns=dropList[:], axis = 1,inplace=True)
    manager.drop(["RBF Cycle"],axis = 1,inplace=True)
    manager.columns = manager.columns.str.rstrip('_x')
    manager.drop_duplicates(subset ="core_orgUnit",keep = "first", inplace = True)
    #print("Merger 1")
    store_dataframe(manager.reset_index(),"merged_nhp_rbf_manager")
##############################################
def merged_fund_status_rbf_manager():# Actual vs Ecpected disbrushment
    frame_path1 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "fund_status_report")
    frame_path2 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "rbf_Manager")
    fund_status = pd.read_feather(frame_path1, use_threads=4, columns=None)
    rbf_manager = pd.read_feather(frame_path2, use_threads=4, columns=None)
    for cols in rbf_manager:
        if '_status' in cols or 'covered' in cols or 'Date' in cols or 'month' in cols or 'day' in cols or 'MOU' in cols or 'chairman' in cols or 'Bank' in cols or 'OTG' in cols:
            rbf_manager.drop([cols],axis = 1,inplace=True)
    for cols in rbf_manager:
        if 'rbf_' in cols:
            l = cols.split('_')
            for strungs in l:
                for i in range(16):
                    try:
                        if int(l[-1]) == int(i):
                                rbf_manager.drop(cols,axis=1,inplace=True)
                    except :
                        pass
    rbf_manager.drop(['hash','is_lagging','Population Covered'] ,axis=1,inplace=True)
    actual_disbrushment=fund_status.groupby(['core_orgUnit','Name of Committee','ctype'])['RBF Amount'].agg('sum')
    rbf_manager = rbf_manager.merge(actual_disbrushment,on='core_orgUnit',how="left")
    rbf_manager["Expected_Disbrushment_Amount"] = rbf_manager["expected_rbf_registered"]
    for index, ctypes in enumerate(rbf_manager["ctype"]):
        if ctypes == 'VHC':
            rbf_manager["Expected_Disbrushment_Amount"][index] = (rbf_manager["expected_rbf_registered"][index])*80000
        elif ctypes == 'HSCMC':
            rbf_manager["Expected_Disbrushment_Amount"][index] = (rbf_manager["expected_rbf_registered"][index])*240000
        elif ctypes == 'HCMC':
            rbf_manager["Expected_Disbrushment_Amount"][index]= (rbf_manager["expected_rbf_registered"][index])*500000       
    rbf_manager["Gap in Disbrushment"] = rbf_manager["Expected_Disbrushment_Amount"]-rbf_manager["RBF Amount"]
    rbf_manager["Gap Percentage"] = rbf_manager["Gap in Disbrushment"]/rbf_manager["Expected_Disbrushment_Amount"] *100

    store_dataframe(rbf_manager,"expected_vs_actual_disbrushment")


######################################################################

def time_delta():#day gap report
    frame_path1 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "fund_status_report")
    frame_path2 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "nhp_report")
    fund_status = pd.read_feather(frame_path1, use_threads=4, columns=None)
    nhp_report = pd.read_feather(frame_path2, use_threads=4, columns=None)
    fund_status_merged = fund_status.merge(nhp_report,on=["core_orgUnit","RBF Cycle"],how="left")
    drop_list = []
    for cols in fund_status_merged:
        if "_y" in cols or "IPR" in cols or "DVR" in cols: 
            drop_list.append(cols)
    fund_status_merged.drop(drop_list,inplace=True,axis=1)
    fund_status_merged.columns = fund_status_merged.columns.str.rstrip('_x')
    fund_status_merged['RBF Start Date'] = pd.to_datetime(fund_status_merged['rbf_started_on'])
    fund_status_merged['Fund Released Date'] = pd.to_datetime(fund_status_merged['RBF Amount Date'],errors="coerce")
    fund_status_merged['Gap'] = fund_status_merged['Fund Released Date'] - fund_status_merged['RBF Start Date']
    #fund_status_merged['Gap1'] =fund_status_merged['Gap']
    for index,date in enumerate(fund_status_merged['Gap']):
        try:
            fund_status_merged['Gap'][index] =  str(fund_status_merged['Gap'][index])[:-9]             #fund_status_merged['Gap1'][index].astype(dt.timedelta).map(lambda x: np.nan if pd.isnull(x)  else x.days)
        except :
            fund_status_merged['Gap'][index] = "________"
    try:
        fund_status_merged['rbf_started_on'] = pd.to_datetime(fund_status_merged['rbf_started_on']).dt.strftime('%Y-%m-%d')
        fund_status_merged['RBF Amount Date'] = pd.to_datetime(fund_status_merged['RBF Amount Date']).dt.strftime('%Y-%m-%d')
    except:
        pass
    l1 = len(fund_status_merged['rbf_started_on'])      
    for i,date in enumerate(fund_status_merged["rbf_started_on"]):
        print("index: ",index,"Date: ",date,"type: ",type(date))
        if type(date) == float:
            fund_status_merged = fund_status_merged.drop(index = i,axis = 0)
    l2 = len(fund_status_merged['rbf_started_on'])    
    print(l2-l1) 
    fund_status_merged = fund_status_merged.reset_index(level=None, drop=False, inplace=False)       
    store_dataframe(fund_status_merged,"fund_status_nhp_report_merged")

def day_gap(): #Frame for widget RBF gap(fund released Gap)
    frame_path1 = settings.CORE_FILE_PATH+"/%s/%s.feather"%("nhm", "fund_status_nhp_report_merged")
    file= pd.read_feather(frame_path1, use_threads=4, columns=None)
    file["Day Gap Catogorie"] = file["Gap"]
    for index,days in enumerate(file["Gap"]):
        dayList = days.split(" ")
        if dayList[0] == "" :
            file["Day Gap Catogorie"][index] = "No Date"
        elif dayList[0] == "N/A":
            file["Day Gap Catogorie"][index]="No Date"
        elif int(dayList[0]) < 0:
            file["Day Gap Catogorie"][index]="Before"
        elif int(dayList[0]) > 0 and int(dayList[0]) < 31:
            file["Day Gap Catogorie"][index]="0-30 Days"
        # elif int(dayList[0]) > 15 and int(dayList[0]) < 31:
        #     file["Day Gap Catogorie"][index]="0 - 30 Days"
        elif int(dayList[0]) > 30 and int(dayList[0]) < 46:
            file["Day Gap Catogorie"][index]="31 - 45 Days"
        elif int(dayList[0]) > 45 and int(dayList[0]) < 61:
            file["Day Gap Catogorie"][index]="45 - 60 Days"
        else:
            file["Day Gap Catogorie"][index]="After 60 Days"
    print(file["Day Gap Catogorie"])
    file.sort_values(by=['Name of Committee',"RBF Cycle"],inplace=True)
    file = file.reset_index(drop=True)
    store_dataframe(file,"day_gap_status")
###################################################################################################################
###
###
### FRAMES FOR CAHN REPORTS 
### AUTHOR ABHISHEK AGRAWAL 
### DATE   3 JUNE 2021
###################################################################################################################
####################################################################
#
#
# 
#
#
def hwc_frame():
    df = retrieve_frame("cho")
    df = df.groupby(["sub_center_id"])
    df = df.first().reset_index()
    store_dataframe(df,"hwc_profile")




     
    































def NHP_Generation(request, profile):

    api = Api('http://45.114.143.40/dhis', 'mohsin', 'Mike@1234')
    # api = Api('aaa', 'aaa', 'aaa')
    # Make JSON through API
    merged_nhp_rbf_manager()
    merged_fund_status_rbf_manager()
    time_delta()
    day_gap()
   
    if(request.GET.get('skip') != '1'):
        merged_nhp_rbf_manager()
        merged_fund_status_rbf_manager()
        time_delta()
        exit("danish")

        programs = ["uJkqL2bYTsF", "YH6qvDzzmov", "mb3P804sihn", "cnus0KAZI5B"]
        for program in programs:
            generate_data_json(api, program)
            
    survey_df = pd.read_csv(settings.CORE_FILE_PATH + "/survey/NFHS-5_sort4.csv")
    store_dataframe(survey_df, "NFHS", (settings.CORE_FILE_PATH + "/survey/"))
    file_path = settings.CORE_FILE_PATH+"/%s/"%("DHIS_json")
    directory = os.fsencode(file_path)
    global MY_PROGRAMS
    MY_PROGRAMS = []
    for file in os.listdir(directory):  
        filename = os.fsdecode(file)
        pass #"Processing "+ filename)
        load_DHIS_json(api, filename)

    NHP_frame_manage()

    import glob

    files = glob.glob(settings.CORE_FILE_PATH+'/analytica_cache_ajax_data/*')
    for f in files:
        os.remove(f)

    return {}


    # Execute second console till 2935