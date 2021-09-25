from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse

import json

from . models import Geography, GeographyLevel, Survey, SurveyToGeography, Category, Indicator, IndicatorToSurveyToGeography, Attribute, AttributeToIndicatorToSurveyToGeography, Answer
from django.conf import settings
import os

from admin_panel.views.helper_methods import *

from django.core import serializers

def analytics(request, survey_name):
    if(survey_name == "uttar_pradesh_nfhs_4"):
        df = retrieve_frame(survey_name, path=settings.CORE_FILE_PATH+"/survey/")
        template = loader.get_template('survey/analytic.html')
        # context = {"survey_name":survey_name, "json": df.to_json(orient='records') }
        context = {"survey_name":survey_name, "json_data":json.dumps(df.to_dict(orient='records')) }
        response = HttpResponse(template.render(context, request))
        response.set_cookie('active_tab', 'analytics')
        return response
    elif(survey_name == "nagaland_nfhs_4"):
        df = retrieve_frame(survey_name, path=settings.CORE_FILE_PATH+"/survey/")
        print(df)
        template = loader.get_template('survey/analytic.html')
        context = {"survey_name":survey_name, "json_data":json.dumps(df.to_dict(orient='records')) }
        response = HttpResponse(template.render(context, request))
        response.set_cookie('active_tab', 'analytics')
        return response
    else:
        
        template = loader.get_template('survey/master_analytics.html')
        context = { "survey_name": survey_name }
        response = HttpResponse(template.render(context, request))
        response.set_cookie('active_tab', 'analytics')
        return response

def getGeoList(request):
    # parent_geo_id = request.POST.getlist('parent_geo_id[]')
    parent_geo_id = request.POST.get('parent_geo_id')
    # print(parent_geo_id)
    geo = Geography.objects.filter(Geography=Geography.objects.get(pk=parent_geo_id)).values('id', 'name')
    # geo = Geography.objects.filter(Geography__in=Geography.objects.filter(pk__in=parent_geo_id)).values('id', 'name') 
    geo = list(geo)
    return JsonResponse(geo, safe=False)

def getIndicatorList(SurveyToGeography_id=1):
    geo = IndicatorToSurveyToGeography.objects.filter(SurveyToGeography=SurveyToGeography.objects.get(pk=SurveyToGeography_id)).only('Indicator__name')
    qs_json = serializers.serialize('json', geo)
    return qs_json

def getChartData(request):
    Survey.objects.filter()

def records(request, survey_name):
    df = retrieve_frame(survey_name, path=settings.CORE_FILE_PATH+"/survey/")
    template = loader.get_template('survey/record.html')
    context = {"survey_name":survey_name, "json_data":json.dumps(df.to_dict(orient='records')) }
    response = HttpResponse(template.render(context, request))
    response.set_cookie('active_tab', 'gis')
    return response

def gis(request, survey_name):
    template = loader.get_template('survey/survey.html')
    context = {"survey_name":survey_name}
    response = HttpResponse(template.render(context, request))
    response.set_cookie('active_tab', 'gis')
    return response


def ques_answer(ques_dict, **kwargs):
    for one in ques_dict:
        print(kwargs.get('prefix'))
        for attr, val in one.items():
            print(attr+ " ==> "+ val)


def load_survey(request):
    geoname = "Lucknow"
    geo_type = "District"

    surveygeo = SurveyToGeography.objects.get(geography=Geography.objects.get(name=geoname, g_type=GeographyLevel.objects.get(name=geo_type)))

    data = IndicatorToSurveyToGeography.objects.filter(surveygeo=surveygeo)

    for x in data:
        print(x.indicator.name)
        for y in AttributeToIndicatorToSurveyToGeography.objects.filter(indicatorsurveygeo=x):
            ans = Answer.objects.get(attrindicatorsurveygeo=y)
            if(y.attribute.name == "Total"):
                print(y.attribute.name + " = " + ans.value)
    

    # df_main = pd.read_csv(r'C:\Users\TATTVA\Desktop\nfhs4-district-level.csv', skiprows=2)
    # df_main = df_main.iloc[:, : 6]
    # df = pd.read_csv(r'C:\Users\TATTVA\Desktop\nfhs4-district-level.csv')
    # df = df.iloc[:, -279:]
    # final_frame = pd.DataFrame()
    # temp_main_frame = df_main
    # for one_column in df.columns:
    #     print(one_column)
    #     temp_main_frame["dataType"] = one_column
    #     temp_main_frame["category"] = df[one_column][0]
    #     temp_main_frame["qestion"] = df[one_column][1]
    #     myx = df.iloc[2:][one_column].reset_index(drop=True)
    #   )
    #     temp_main_frame["value"] = myx    
    #     final_frame = pd.concat([final_frame, temp_main_frame])
    # final_frame.to_csv(r'C:\Users\TATTVA\Desktop\final.csv',index=False)

    # geoname = "Lucknow"
    # geo_type = "District"

    # surveygeo = SurveyToGeography.objects.get(geography=Geography.objects.get(name=geoname, g_type=GeographyLevel.objects.get(name=geo_type)))

    # data = IndicatorToSurveyToGeography.objects.filter(surveygeo=surveygeo)

    # for x in data:
    #     print(x.indicator.name)
    #     for y in AttributeToIndicatorToSurveyToGeography.objects.filter(indicatorsurveygeo=x):
    #         ans = Answer.objects.get(attrindicatorsurveygeo=y)
    #         if(y.attribute.name == "Total"):
    #             print(y.attribute.name + " = " + ans.value)




    #=========== Code Feed NFHS Distrcit Data to System Start ===========================

    # df = pd.read_csv(r'C:\Users\TATTVA\Desktop\combine.csv')
    # df.fillna('',inplace=True)

    # for index, one_row in df.iterrows():

    #     geoObj  =   Geography.objects.get(
    #                     GeographyLevel=GeographyLevel.objects.get(name='State'),
    #                     census_code=one_row.State
    #                 )

    #     surveyGeoObj, created       =  SurveyToGeography.objects.get_or_create(
    #                                         Geography=geoObj,
    #                                         Survey=Survey.objects.get(name='Census'),
    #                                     )                        

    #     for one_attr in df:
    #         if(one_attr not in ['State','District','Level','Name','TRU']):

    #             indiObj, created        =  Indicator.objects.get_or_create(
    #                                         name=one_attr,
    #                                     )


    #             indisurveyGeoObj, created       =   IndicatorToSurveyToGeography.objects.get_or_create(
    #                                                     Category=None,
    #                                                     SurveyToGeography=surveyGeoObj,
    #                                                     Indicator=indiObj,
    #                                                 )

    #             attrObj, created        =  Attribute.objects.get_or_create(
    #                                             name=one_row.TRU,
    #                                         )


    #             attrindicatorsurveygeoObj, created          =   AttributeToIndicatorToSurveyToGeography.objects.get_or_create(
    #                                                                 Attribute=attrObj,
    #                                                                 IndicatorToSurveyToGeography=indisurveyGeoObj,
    #                                                             )

    #             attrObj, created        =  Answer.objects.get_or_create(
    #                                             value=one_row[one_attr],
    #                                             AttributeToIndicatorToSurveyToGeography=attrindicatorsurveygeoObj
    #                                         )
    #     print(one_row.Name + " Done")


        #=========== Code Feed NFHS Distrcit Data to System End ===========================






        # Surveygeo





        # geoLevelObj, created        =  Geography.objects.get_or_create(
        #                                     name="NA State",
        #                                     related_to=Geography.objects.get(name='India'),
        #                                     g_type=GeographyLevel.objects.get(name='State'),
        #                                     census_code=one_row.State
        #                                 )

        # geoObj, created    =    Geography.objects.get_or_create(
        #                             name=one_row.Name,
        #                             g_type=GeographyLevel.objects.get(name='District'),
        #                             related_to=geoLevelObj,
        #                             census_code=one_row.District
        #                         )

    # df = pd.read_csv(r'C:\Users\TATTVA\Desktop\cencus_state.csv')
    
    # for index, one_row in df.iterrows():
    #     geoObj    =    Geography.objects.get(
    #                                 name="NA State",
    #                                 g_type=GeographyLevel.objects.get(name='State'),
    #                                 related_to=Geography.objects.get(name='India'),
    #                                 census_code=one_row.Code
    #                             )
    #     geoObj.name =   one_row.Name

    #     geoObj.save()

        # print(one_row)

    # print(df)





    # from pprint import pprint
    # import json
    # with open(r"C:\Users\TATTVA\Desktop\UP_NFHS_4.json") as json_file:
    #     data = json.load(json_file)
    # indicators = []
    # final_data = []
    # for one_attr in data["fields"]:
    #     indicators.append(one_attr["label"])
    # indicators[0] = "Indicator"
    # for one_row in data["data"]:
    #     final_data.append(dict(zip(indicators,one_row)))

    # with open(r'D:\result.json', 'w') as fp:
    #     json.dump(final_data, fp)

    # df = pd.read_json(r"D:\result.json", orient='record')
    # df = df[df.columns[~df.columns.str.startswith('Note of ')]]
    # print(df.columns)
    # print(df)

    # store_dataframe(df, "nfhs_4", settings.CORE_FILE_PATH+"/survey/")
    return JsonResponse({"a":"b"})
