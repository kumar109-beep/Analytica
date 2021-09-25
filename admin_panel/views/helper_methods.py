import pandas as pd
# import modin.pandas as pd
# import dask.dataframe as dd

from django.conf import settings
import time
# from admin_panel.models import Dataframe
from dataframe.models import Dataframe
import os.path
import re

def retrieve_frame(frame_name, columns=None, path=None):
    if columns:
        columns = list(set(columns))
    print(frame_name, columns)
    frame_source = ["nhm", "survey"]
    start = time.time()
    if path:
        frame_path = path + frame_name + ".feather"
    else:
        for one_dir in frame_source:
            frame_path = settings.CORE_FILE_PATH+"/%s/%s.feather"%(one_dir, frame_name)
            print(frame_path)
            if os.path.isfile(frame_path):
                break
            else:
                frame_path = False
    if frame_path:
        print(frame_path)
        df = pd.read_feather(frame_path, use_threads=4, columns=columns)
        # print(df, frame_path)
        # df = dd.read_parquet(frame_path+".parquet", columns=columns, engine='pyarrow')
        # print(df.name)
        # print (len(df.index))
        # df = pd.read_parquet(frame_path+'.parquet', use_threads=10, engine='pyarrow', columns=columns)
        # df = pd.read_hdf(settings.CORE_FILE_PATH+"/nhm/NHM.h5", frame_name)
        done = time.time()
        elapsed = done - start
        print(elapsed, "*"*20)

        print(get_columns_with_type(df))
        # df['RBF State'] = df['program_status'].apply(lambda x: "Not Completed" if pd.isna(x) else "Completed")
        # df['RBF State'] = df.apply(lambda x: rbf_state_fill(x), axis=1)
        # df[:10]
        return df
    else:
        print("Frame not found")
        # return pd.DataFrame()
        return None

# def rbf_state_fill(row):
#     print(( row['Action_Plan_status'],row['Fund_Status_status'],row['Fund_Status_status'],row['IPR_-_1_status'],row['DVR_-_1_status'],row['IPR_-_2_status'],row['DVR_-_2_status'],row['Six_Monthly_Expenditure_status'] ))
#     if not ( pd.isna(row['Action_Plan']) and pd.isna(row['Fund_Status']) and pd.isna(row['Fund_Status']) and pd.isna(row['IPR_-_1']) and pd.isna(row['DVR_-_1']) and pd.isna(row['IPR_-_2']) and pd.isna(row['DVR_-_2']) and pd.isna(row['Six_Monthly_Expenditure']) ):
#         if pd.isna(row['program_status']):
#             result = "Verified"
#         else:   
#             result = "Completed"
#     else:
#         if not( pd.isna(row['Action_Plan']) or pd.isna(row['Fund_Status']) or pd.isna(row['Fund_Status']) or pd.isna(row['IPR_-_1']) or pd.isna(row['DVR_-_1']) or pd.isna(row['IPR_-_2']) or pd.isna(row['DVR_-_2']) or pd.isna(row['Six_Monthly_Expenditure']) ):
#             result = "Not Completed"
#         else:
#             result = "No Data Entered"
#     return result


def get_columns_with_type(df):
    x = df.dtypes.to_dict()
    # del x["hash"]
    return ({k : {"datatype":str(v), "label":k} for k, v in x.items()})
    # return ([{"name":k, "datatype":str(v), "label":k} for k, v in x.items()])


def store_dataframe(data, frame_name, path=None, **kwargs):

    if kwargs.get("sanitize_column"):
        for column in data.columns:
            data.rename(columns={column: re.sub('[^A-Za-z0-9]+|\s+|\r+|\t+', ' ', column).strip().lower().replace(' ', '_') }, inplace=True)
    # for column in data.columns:
    #     data.rename(columns={column: re.sub('[^A-Za-z0-9]+|\s+|\r+|\t+', ' ', column).strip().lower().replace(' ', '_') }, inplace=True)
    data['hash'] = pd.util.hash_pandas_object(data, index=False).astype(str)
    

    frame_meta = {"columns" : get_columns_with_type(data), "size":len(data.index)}
    person, created = Dataframe.objects.get_or_create(name=frame_name)
    if not created:
        person.meta = frame_meta
        person.save()
    if path:
        path = path + frame_name
    else:
        path = settings.CORE_FILE_PATH+"/nhm/%s"%frame_name
    data.to_feather(path+".feather")
    # data.to_parquet(path+'.parquet', engine='pyarrow')
    # data.to_hdf(settings.CORE_FILE_PATH+"/nhm/NHM.h5", frame_name, format='table')
    # data.to_hdf(settings.CORE_FILE_PATH+"/analytica_data/%s.h5"%frame_name, 'data')

    # data.to_hdf(settings.CORE_FILE_PATH+"/analytica_data/%s.hdf"%frame_name, '/data')
    # df.to_hdf('./store.h5', 'data')
