from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.template import loader
from django.shortcuts import render
import json
import numpy as np
from django.shortcuts import render
import datetime

from .helper_methods import *

from rolepermissions.checkers import has_permission

# from admin_panel.models import Frame_edit_request, Dataframe
from dataframe.models import Frame_edit_request, Dataframe

from dataframe.serializers import Frame_edit_requestSerializer

from django.utils import timezone

allow_last_selected_session = ""

from django.urls import reverse_lazy 


def index(request):
    return redirect('analytics', profile="asha")

def request_edit(request):
    data = request.GET
    serializer = Frame_edit_requestSerializer.get_or_create(data)
    print(serializer)

    # obj, created = Frame_edit_request.objects.update_or_create(
    #     user=request.user, frame=data['frame'], col_name=data['edit_col'], old_val=data['edit_old_val'], new_val=data['edit_new_val'], hash_code=data['hash'], defaults={'updated_at': timezone.now()},
    # )
    # print(obj, created)
    return JsonResponse(data)

def asha_not_paid_frame(selected_df):
    df2 = retrieve_frame("asha")
    df = df2[~df2.asha_id.isin(selected_df.asha_id)]

    # x = selected_df[~selected_df.asha_id.isin(df2.asha_id)]
    # print(x.asha_id)
    return df

def sangini_not_paid_frame(selected_df):
    df2 = retrieve_frame("sangini")
    df = df2[~df2.sangini_id.isin(selected_df.sangini_id)]
    return df

def get_actual_profile(request, profile):
    global allow_last_selected_session
    import dateutil.relativedelta

    if("payment" in profile):
        allow_last_selected_session = onGoing_session(False)
        get_frame_as = []
        cookies_start_date, cookies_end_date = request.COOKIES.get('session_start_date') , request.COOKIES.get('session_end_date')
        if cookies_start_date and cookies_end_date:
            cookies_start_date = datetime.datetime.strptime(cookies_start_date, "%B-%Y").date()
            cookies_end_date   = datetime.datetime.strptime(cookies_end_date, "%B-%Y").date()
            
            while(cookies_start_date <= cookies_end_date):
                get_frame_as.append(profile + "_" + cookies_start_date.strftime("%B-%Y") )
                cookies_start_date += dateutil.relativedelta.relativedelta(months=1)
                print(get_frame_as)
        else:
            get_frame_as = [profile + "_" + allow_last_selected_session]
    else:
        get_frame_as = [profile]
    request.COOKIES['real_frame'] = get_frame_as[0]
    print(get_frame_as[-1])
    return get_frame_as


def prepare_data_frame(request, profile, columns=None):
    get_frame_as = get_actual_profile(request, profile)
    df = []
    print(get_frame_as, "x"*50)
    for one_frame in get_frame_as:
        df.append(retrieve_frame(one_frame, columns))
    df = pd.concat(df)
    return df


def handle_chart_hash(file_name, content=False):
    cache_path = settings.CORE_FILE_PATH+"/analytica_cache_ajax_data/%s"%file_name
    if content:
        with open(cache_path, 'w') as f:
            f.write(content)
            # json.dump(content, f)
        return True
    else:
        import os
        exists = os.path.isfile(cache_path)
        if exists:
            with open(cache_path) as f:
                data = f.read()
                # data = json.load(f)
            return data
        else:
            return False



def filter_frame(df, filters):
    for filter in filters:
        # print(filter, "$"*30)
        print("\n" +"###"*10)
        try:
            query = '`{0}` {1} "{2}"'.format(filter["attr"], filter["operator"], filter["value"])
            df = df.query(query)
            print(query, "Filter Applied")
        except Exception as e:
            # query = "`{0}` {1} {2}".format(filter["attr"], filter["operator"], filter["value"])
            # query = filter["attr"] + filter["operator"] + "%s" %filter["value"]
            
            print(query, "Unable to Apply FIlter")
            print("Error : " +str(e))
            # df = df.query(query)
        print("###"*10 + "\n")
    return df

def make_charts_ui(request):
    context = {}
    template = loader.get_template('admin_panel/make_charts_ui.html')
    response = HttpResponse(template.render(context, request))
    # response.set_cookie('active_tab', 'analytics')    
    return response


# Generate Chart Data API
def generate_chart_data(request, profile):
    import traceback
    import hashlib
    try:
        # hash_str = get_actual_profile(request, profile)[0]
        hash_str = '-'.join(get_actual_profile(request, profile))
        identifier_string = (hash_str + str(request.GET)).encode('utf-8')
        request_hash_of_chart = hashlib.sha256(identifier_string).hexdigest()
        data = handle_chart_hash(request_hash_of_chart)
        
        # if(data):
        if(False):
            pass
        else:
            get_data_frame_function             = request.GET.get('get_data_frame_function')
            head                                = request.GET.getlist('head[]')
            data_type                           = request.GET.getlist('data_type[]')
            unique_by_columns                   = request.GET.getlist('unique_by_columns[]')
            regex_match_count                   = request.GET.getlist('regex_match_count[]')
            group_by                            = request.GET.getlist('group_by[]')
            filters                             = json.loads(request.GET.get('filters', "[]"))
            sort_by                             = request.GET.get('sort_by', group_by[0])
            sort_type                           = request.GET.get('sort_type')
            sort_order                          = request.GET.getlist('sort_order[]', [])
            select_heads                        = request.GET.get('select_heads[]')
            # start, end, random (three value like start:20)
            summray        = request.GET.get('summray')
            new_heads      = group_by


            retrive_head = group_by + head + unique_by_columns

           
            print(filters, "99999")
            if(filters):
                for filter in filters:
                    retrive_head.append(filter["attr"])

            print(retrive_head, "*"*50)
            if get_data_frame_function:
                if("_not_paid_frame" in get_data_frame_function):
                    df = prepare_data_frame(request, profile)
                    # df = retrieve_frame(profile)
                    df = eval(get_data_frame_function)(df)
            else:
                df = prepare_data_frame(request, profile)
                # df = retrieve_frame(profile, retrive_head)

            # df = df.fillna("others")
            if(unique_by_columns):
                df.drop_duplicates(subset=unique_by_columns, keep="last", inplace=True)

            # for one_head in group_by:
            #     query = "`{0}` {1} '{2}'".format(one_head, "!=", "N/A")
            #     try:
            #         df = df.query(query)
            #     except:
            #         pass

            df = filter_frame(df, filters)
            
            try:
                f = {}
                for idx, one_head in enumerate(head):
                    f[one_head] = [ ((data_type[idx]) , data_type[idx]) ]
                    # f[one_head] = {(data_type[idx]) : data_type[idx]}
                
                df = df.groupby(group_by).agg(f)
                # df = df.groupby(group_by).agg(f).unstack(fill_value=0).stack().reset_index()
                

                # print(df)
                new_cols = []
                for one_col in df.columns:
                    if (one_col[1]==""):
                        new_cols.append(one_col[0])
                    else:
                        new_cols.append(one_col[1] + "_of_" +one_col[0])

                df.columns = new_cols

                df = df.reset_index()

                if(select_heads):
                    df = df[select_heads]
                # else:
                #     df = df[new_heads]

                if("working_since" == sort_by):
                    df[sort_by] = pd.to_datetime(df[sort_by], format='%b-%y')

                if("working_since" == sort_by):
                    df[sort_by] = df[sort_by].dt.strftime('%b-%y')

                sort_attr = []
                sort_attr_type = []
                for one_key in sort_order:
                    temp = one_key.split(":")
                    sort_attr.append((temp[0].lower().strip()))
                    sort_attr_type.append( False if temp[1] == "desc" else True )

                print(sort_attr, sort_attr_type)
                if sort_attr:
                    # df = df.sort_values(["mean_of_population"], ascending=[False]).reset_index(drop=True)
                    df = df.sort_values(sort_attr, ascending=sort_attr_type).reset_index(drop=True)
                # print(sort_attr, sort_attr_type)
            except Exception as e:
                print("Found Error = "+str(e))


            df = df.round(2)
            if(summray):
                try:
                    summray = summray.split(':')
                    position = summray[0]
                    count = int(summray[1])
                    if(position == "first"):
                        df = df.head(count)
                    elif(position == "last"):
                        df = df.tail(count)
                    elif(position == "random"):
                        df = df.sample(n=count)
                except:
                    pass
            
            # print(df)
            if request.GET.get('report_data', False):
                # for datatable
                data = df.to_json(orient='records')
            else:
                data = df.to_json(orient='columns')

            handle_chart_hash(request_hash_of_chart, data)
        return HttpResponse(data, content_type="application/json")
        # return JsonResponse(data)
    except Exception:
        return JsonResponse({"api_status":500, "error":str(traceback.format_exc())})


def render_permission_denied(request):
    latest_question_list = ""
    template = loader.get_template('admin_panel/access_permission_denied.html')
    context = {
        'latest_question_list': latest_question_list
    }
    return HttpResponse(template.render(context, request))



# Current active fucntion for analytcs
def payment(request, profile):
    # if not has_permission(request.user, 'view_payment'):
    #     # render_permission_denied(request)
    #     print("da"*60)
    context = {}
    template = loader.get_template('admin_panel/master_analytics.html')
    response = HttpResponse(template.render(context, request))
    response.set_cookie('active_tab', 'analytics')
    return response

def worker_payment_status(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    base_drill = []

    total_row = len(df.index)

    bcpm_count = df[df.submit.str.contains("/")].submit.count()
    if bcpm_count < 3:
        bcpm_count = df[df.submit == "Started"].submit.count()
        bcpm_text = "Blocks Started their Work"
        bcpm_tag_line = "Ongoing process BCPM working on it"
    else:
        bcpm_text = "% Blocks Submitted Claim"
        bcpm_tag_line = "BCPM Processed Vouchers to MOIC"

    bcpm_count = (bcpm_count/total_row) * 100
    widget_chart_list.append(widget_chart([], "bcpm_status", [bcpm_count], [bcpm_text], bcpm_tag_line))

    moic_count = df[df.approved.str.contains("/")].approved.count()
    if moic_count < 3:
        moic_count = df[df.approved == "Started"].approved.count()
        moic_text = "MOIC Started their Work"
        moic_tag_line = "Ongoing process MOIC working on it"
    else:
        moic_text = "% Blocks Completed Verification"
        moic_tag_line = "MOIC Processed Data for BAM"

    moic_count = (moic_count/total_row) * 100
    widget_chart_list.append(widget_chart([], "moic_status", [moic_count], [moic_text], moic_tag_line))


    bam_count = df[df.payment.str.contains("/")].payment.count()
    if bam_count < 3:
        bam_count = df[df.payment == "Started"].payment.count()
        bam_text = "BAM Started their Work"
        bam_tag_line = "Ongoing process BAM working on it"
    else:
        bam_text = "% Blocks Made Payment"
        bam_tag_line = "BAM Processed Payement"

    bam_count = (bam_count/total_row) * 100
    widget_chart_list.append(widget_chart([], "bam_status", [bam_count], [bam_text], bam_tag_line))


    
    excellent_bcpm = df[df.bcpm_performance == "Excellent"].bcpm_performance.count()
    excellent_bcpm = (excellent_bcpm/total_row) * 100
    widget_chart_list.append(widget_chart(base_drill, "bcpm_performance",  [excellent_bcpm], ["% Best Performers"], "BCPM Performance"))

    
    
    excellent_moic = df[df.moic_performance == "Excellent"].moic_performance.count()
    excellent_moic = (excellent_moic/total_row) * 100
    widget_chart_list.append(widget_chart(base_drill, "moic_performance",  [excellent_moic], ["% Best Performers"], "MOIC Performance"))

    
    excellent_bam = df[df.bam_performance == "Excellent"].bam_performance.count()
    excellent_bam = (excellent_bam/total_row) * 100
    widget_chart_list.append(widget_chart(base_drill, "bam_performance",  [excellent_bam], ["% Best Performers"], "BAM Performance"))

    statistics = {}
    statistics["worker"] = worker.lower()
    return (statistics, widget_chart_list)

def worker_payment_keypoint(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    base_drill = []

    number_of_worker =  df[worker.lower()+"_id"].nunique()

    payment_head = [col for col in df if col.endswith('_total')]
    if "asha" in profile:
        # heads = 16
        heads = len(payment_head)
    else:
        heads = 5
    widget_chart_list.append(widget_chart([], "head_payment_distribution", [number_of_worker/1000, heads], [ "k " +worker + " claimed under", "Heads"], "Headwise Amount Distribution"))
    widget_chart_list.append(widget_chart(base_drill, "current_payment",  [df.subtotal.sum()], ["₹"], "Amount Claimed"))

    not_paid_worker_function = worker.lower() + "_not_paid_frame(df)"
    widget_chart_list.append(widget_chart(base_drill, "current_not_paid",  [eval(not_paid_worker_function)[worker.lower()+"_id"].count()], [worker], "Not Claimed"))


    widget_chart_list.append(widget_chart(base_drill, "avg_current_payment",  [df.subtotal.sum()/df[worker.lower()+"_id"].count()], ["₹ / "+ worker  ], "Average Incentive"))
    
    categorized_total_amount = "5001 - 6000"
    categorized_total_amount_count = len(df[df["categorized_total"]==categorized_total_amount].index)
    widget_chart_list.append(widget_chart(["categorized_total"], "amount_distribution_in_worker", [categorized_total_amount_count ], ["Earned around " + categorized_total_amount], "Received Incentive"))
    # widget_chart_list.append(widget_chart(["categorized_total"], "amount_distribution_in_worker", [df.subtotal.max() ], ["₹ Maximum"], "Received Incentive"))
    # widget_chart_list.append(widget_chart(base_drill, "worker_claimed_current",  [df.subtotal.count()], [ worker + ""], "Claimed"))
    widget_chart_list.append(widget_chart(base_drill, "worker_claimed_current",  [number_of_worker], [ worker + ""], "Claimed"))
    
    
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)

def worker_profile_keypoint(df, profile):
    worker = profile.upper()
    widget_chart_list = []
    base_drill = []
    statistics = {}
    
    widget_chart_list.append(widget_chart(base_drill, "worker_count",  [df[profile+"_id"].count()], [""], "Working "+worker))
    
    statistics["worker"] = worker.lower()

    statistics["total_worker"] = df[profile+"_id"].count()
    statistics["worker_selection"] = df.working_since_year.mode()[0]
    if(profile in ["asha", "health_worker"]):
        statistics["total_population"] = df["population"].sum()
        widget_chart_list.append(widget_chart(base_drill, "asha_avarage_distribution",  [int(statistics["total_population"]/statistics["total_worker"])], ["People/"+worker], "Population Distribution"))
        widget_chart_list.append(widget_chart(base_drill, "asha_on_population",  [statistics["total_worker"], statistics["total_population"]  ], ["Serving" , ""], worker +" by Population"))
        statistics["over_load_worker"] = df[df.population > 1500][profile+"_id"].count()
        widget_chart_list.append(widget_chart(["population_category"], "worker_vs_population",  [statistics["over_load_worker"]], ["Overloaded "], worker +" vs Population"))
    widget_chart_list.append(widget_chart(base_drill, "worker_caste",  [4], ["Castes"], "Caste Distribution"))
    if(profile in ["asha", "sangini", "health_worker"]):
        statistics["total_pg"] = df[df.educational_qualification == "Post Graduate"][profile+"_id"].count()
        widget_chart_list.append(widget_chart(base_drill, "educational_overview",  [statistics["total_pg"]], ["with PG"], "Educational Profile"))
    if(profile in ["anm", "sangini"]):
        statistics["total_asha"] = df["number_of_asha"].sum()
        widget_chart_list.append(widget_chart(["number_of_asha"], "asha_per_worker",  [ int(statistics["total_asha"]/statistics["total_worker"]) ], ["ASHA/ "+worker], ""))
    if(profile in ["anm"]):
        __temp_holder1 = (df[df.job_type.astype(str).str.match("Contractual")]["job_type"].count() * 100)/statistics["total_worker"]
        __temp_holder2 = (df[df.job_type.astype(str).str.match("Permanent")]["job_type"].count() * 100)/statistics["total_worker"]
        widget_chart_list.append(widget_chart(base_drill, "job_type",  [ __temp_holder1 ], ["% Contractual"], "Job Type"))

        __temp_holder1 = df[df.sub_center_name.astype(str).str.match("At PHC")]["sub_center_name"].count()
        widget_chart_list.append(widget_chart(base_drill, "anm_at_phc",  [ __temp_holder1 ], [" ANM"], "ANM at PHC"))
        __temp_holder1 = df[df.sub_center_name.astype(str).str.match("At CHC")]["sub_center_name"].count()
        widget_chart_list.append(widget_chart(base_drill, "anm_at_chc",  [ __temp_holder1 ], ["ANM"], "ANM at CHC"))
    widget_chart_list.append(widget_chart(["age_category", "age"], "age_distribution",  [25, 60], ["to", "Years"], "Age Distribution"))
    
    __temp_holder1 = df[df.mobile_status.astype(str).str.match("Valid")]["mobile_status"].count()
    __temp_holder2 = df["mobile_status"].count()
    statistics["mobile_number"] = { "valid_number" : __temp_holder1, "invalid__number": (__temp_holder2 - __temp_holder1) }
    widget_chart_list.append(widget_chart(base_drill, "available_mobile",  [__temp_holder1], [worker], "Active Mobile"))
    if(profile in ["asha", "anm", "health_worker"]):
        widget_chart_list.append(widget_chart(["working_since_year", "working_since"], "asha_engagement",  [statistics["worker_selection"]], ["Maximum"], worker + " Selection"))
    
    
    return (statistics, widget_chart_list)

def widget_chart(filters, chartfor, counts, count_text, count_tagline):
    widget = {}
    widget["filters"] = filters
    widget["chartfor"] = chartfor
    widget["counts"] = counts
    widget["count_text"] = count_text
    widget["count_tagline"] =count_tagline
    return widget


# Return ongoing session in form of tuple (month, year) as per the current date
def onGoing_session(selected_session):
    if selected_session:
        # print(selected_session)
        return(selected_session)
    else:
        current_date = datetime.date.today()
        if(current_date.day > 15):
            month = current_date.month
        else:
            month = current_date.month - 1
        if month:
            year = current_date.year
        else:
            month = 12
            year = current_date.year - 1

        current_date = datetime.date(year, month, 1).strftime('%B-%Y')
        return(current_date)

def get_last_synced(request):
    try:
        date = Dataframe.objects.filter(name=request.COOKIES['real_frame']).get().updated_at.strftime('%d-%b-%Y at %H:%M')
    except:
        date = None
    return date


def get_columns_with_type(df):
    x = df.dtypes.to_dict()
    del x["hash"]
    return dict([(k, str(v)) for k, v in x.items()])
    # return x

# Current active fucntion for analytcs
def analytics(request, profile):
    if request.method == "POST":
        statistics = {}
        df = prepare_data_frame(request, profile)
        base_drill = ["state_name", "region_name", "district_name", "block_name", "sub_center_name", "village_name"]
        if("payment_status" in profile):
            if not has_permission(request.user, 'view_performance_analytic'):
                return render_permission_denied(request)
            del base_drill[-2:]
            statistics = worker_payment_status(df, profile)

        elif("payment" in profile):
            if not has_permission(request.user, 'view_payment_analytic'):
                return render_permission_denied(request)
            statistics = worker_payment_keypoint(df, profile)

        elif(profile in ["asha", "sangini", "anm", "health_worker"]):
            if not has_permission(request.user, 'view_profile_analytic'):
                
                return render_permission_denied(request)
            statistics = worker_profile_keypoint(df, profile)

        elif(profile in ["committees"]):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_keypoints(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']
                            
        elif(profile in ["members"]):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_member_keypoints(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']
                            
        elif(profile in "rbf_Manager"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_rbf_manager(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']

        elif(profile in "action_plan"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_action_plan(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']

        elif(profile in "nhp_report"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_nhp_report(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']

        elif(profile in "six_monthly_expenditure"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_six_monthly_expenditure(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']
        
        elif(profile in "fund_status_with_six_month_expenditure"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = committee_six_monthly_expenditure(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']

        elif(profile == "VHC_target_indicators_consolidated"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = vhc_target_indicators_consolidated(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']

        elif(profile == "HSCMC_target_indicators_consolidated"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = vhc_target_indicators_consolidated(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']

        elif(profile == "HCMC_target_indicators_consolidated"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = vhc_target_indicators_consolidated(df, profile)
            base_drill = [  'STATE',
                            'DISTRICT',
                            'BLOCK',
                            'COMMUNITY HEALTH CENTER',
                            'PRIMARY HEALTH CENTER',
                            'SUB CENTER',
                            'VILLAGE']
# 
        elif(profile == "cho"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = cho_profile(df,profile)
            base_drill = [  'STATE',
                            'REGION'
                            'DISTRICT',
                            'BLOCK',
                            'SUB CENTER',
                            ]
        elif(profile == "HCMC_target_indicators_consolidated"):
            if not has_permission(request.user, 'view_nhp_profile_analytic'):
                return render_permission_denied(request)
            statistics = hwc_profile(df,profile)
            base_drill = [  'STATE',
                            'REGION'
                            'DISTRICT',
                            'BLOCK',
                            'SUB CENTER',
                            ]
                            
                            
        last_synced = get_last_synced(request)
        widget_charts = statistics[1]
        statistics = statistics[0]

        headers_with_type = get_columns_with_type(df)
        # headers_with_type = dict([(k, str(v)) for k, v in headers_with_type.items()])
        #print(statistics)
        context = {  
            'last_synced':last_synced,
            'widget_charts' : str(widget_charts),
            # 'statistics': statistics,
            'profile' : profile,
            'base_drill' : str(base_drill),
            'headers_with_type':headers_with_type,
        }

    if request.method == "POST":
        return JsonResponse(context)

    template = loader.get_template('admin_panel/master_analytics.html')
    response = HttpResponse(template.render({'profile' : profile, 'allow_last_selected_session':allow_last_selected_session}, request))
    response.set_cookie('active_tab', 'analytics')
    return response


def master_reports(request):

    # df = retrieve_frame("nhp_report")

    # df = df.groupby('ctype').hash.count().reset_index(name="count")
    # df = df[df["program_status"].isnull()].groupby(['ctype', 'RBF Cycle']).hash.count().reset_index(name="count")

    # df = df[df["program_status"].notnull()].groupby(['ctype', 'RBF Cycle']).hash.count().reset_index(name="count")

    # print(df)

    df = retrieve_frame("rbf_wise_fund_and_expense", ["current_rbf"])
    

    template = loader.get_template('admin_panel/master_reports.html')
    context = {  
        "CURRENT_CYCLE" : df["current_rbf"].max()
	}
    response = HttpResponse(template.render(context, request))
    response.set_cookie('active_tab', 'records')
    return response



# Function to render datatable
def master_record(request, profile):
    worker = profile.split("_")[0]
    df = prepare_data_frame(request, profile)
    default_attr = [worker+"_id", "name", "village_name", "sub_center_name", "block_name", "district_name"]
    hidden_fields = []
    if("payment_status" in profile):
        if not has_permission(request.user, 'view_performance_record'):
            return render_permission_denied(request)

    elif("payment" in profile):
        if not has_permission(request.user, 'view_payment_record'):
            return render_permission_denied(request)

    elif(profile in ["asha", "sangini", "anm"]):
        if not has_permission(request.user, 'view_profile_record'):
            return render_permission_denied(request)

    elif(profile in ["committee"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = ["Name of Committee", "Date of MOU", "DISTRICT", "BLOCK", "COMMUNITY HEALTH CENTER", "PRIMARY HEALTH CENTER", "SUB CENTER", "VILLAGE"]

    elif(profile in ["members"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = ["Name", "Designation", "Sex", "DISTRICT", "BLOCK", "COMMUNITY HEALTH CENTER", "PRIMARY HEALTH CENTER", "SUB CENTER", "VILLAGE"]

    elif(profile in ["rbf_Manager"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = ["Name of Committee","ctype", "current_rbf"] + ["rbf_%s" %i for i in range(0,11) ]
        hidden_fields = ["rbf_%s_status" %i for i in range(0,11) ]
    elif(profile in ["nhp_report"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = ["Action_Plan", "Fund_Status", "IPR_-_1", "DVR_-_1", "IPR_-_2", "DVR_-_2", "Six_Monthly_Expenditure"]
        hidden_fields = []
    
    elif(profile in ["six_monthly_expenditure"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = [ "Activity Category", "Activities (approved in the Action Plan)", "Approved Budget", "Quarter 1 Expenditure", "Quarter 2 Expenditure", "ctype", "activity_type" ]
    elif(profile in ["cho"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = [ "REGION","DISTRICT",  "BLOCK", "SUB CENTER",'cho_id','name',"mobile", "gender", "email",'ELECTRICITY','WATER','working_since_year','dob','population' ]
    elif(profile in ["hwc_profile"]):
        if not has_permission(request.user, 'view_nhp_profile_record'):
            return render_permission_denied(request)
        default_attr = [ "REGION","DISTRICT",  "BLOCK", "SUB CENTER",'cho_id','name',"mobile", "gender", "email",'ELECTRICITY','WATER','working_since_year','dob','population' ]


    template = loader.get_template('admin_panel/master_record.html')
    columns = df.columns.tolist()
    # print(columns)

    headers_with_type = get_columns_with_type(df)

    # Remove hidden column from select box attrbite
    for one_key in hidden_fields:
        del headers_with_type[one_key]
    # headers_with_type = dict([(k, str(v)) for k, v in headers_with_type.items()])

    # print(headers_with_type)


    last_synced = get_last_synced(request)

    if(default_attr[0] not in columns):
        default_attr = columns[0:3]
    context = {  
    'last_synced':last_synced,
    'headers': columns,
    'headers_with_type' : headers_with_type,
    'default_attr' : default_attr,
    'hidden_fields': hidden_fields,
    'profile' : profile,
    'worker': worker,
    'allow_last_selected_session':allow_last_selected_session
	}
    response = HttpResponse(template.render(context, request))
    response.set_cookie('active_tab', 'records')
    return response

def get_geojson(request, profile):
    geo_file = request.GET.get('geo_file')
    data = open(settings.CORE_FILE_PATH+'/shape_files/'+ geo_file +'.json').read() #opens the json file and saves the raw contents
    # data = open(settings.CORE_FILE_PATH+'/shape_files/DISTRICT_BOUNDARY_UTTAR_PRADESH.geojson').read() #opens the json file and saves the raw contents
    jsonData = json.loads(data)
    return JsonResponse(jsonData)

# def get_geojson(request, profile):
#     import geopandas as gpd
#     # import os
#     # os.environ['PROJ_LIB']=r"C:\ProgramData\Miniconda3\Library\share"

#     level = request.GET.get('level')
#     gis_filter = json.loads(request.GET.get('filter'))
    
#     level_shape = {
#         "district": settings.CORE_FILE_PATH+'/shape_files/DISTRICT_BOUNDARY_UTTAR_PRADESH.shp',
#         "block"   : settings.CORE_FILE_PATH+'/shape_files/BLOCK_BOUNDARY_UTTAR_PRADESH.shp',
#     }

#     tracts = gpd.read_file(level_shape[level])
   
#     print(tracts)

#     df = prepare_data_frame(request, profile, ["district_code_census", "block_code_census"])

#     for filter in gis_filter:
#         query = filter["attr"] + filter["operator"] + "'%s'" %filter["value"]

#     df = df.rename(columns={"district_code_census" : "DT_CODE", "block_code_census" : "CD_Block"})

#     if(gis_filter):  
#         tracts = tracts.query(query)
#         df = df.query(query)

#     if("DT_NAME" in tracts.columns):
#         df["count"] = df.groupby("DT_CODE").DT_CODE.transform("size")
#         df = df[["DT_CODE", "count"]]
#     else:
#         df["count"] = df.groupby("CD_Block").CD_Block.transform("size")
#         df = df[["DT_CODE", "CD_Block", "count"]]

#     tracts = tracts.rename(columns={"DT_Name":"DT_NAME"})

#     df=df.drop_duplicates()
#     if("CD_Block" in tracts.columns):
#         tracts = tracts.merge(df, on='CD_Block', how='left')
#     else:
#         tracts = tracts.merge(df, on='DT_CODE', how='left')

#     tracts = tracts.rename(columns={"DT_CODE_x":"DT_CODE", "CD_Block_x":"CD_Block"})

#     # tracts.geometry = tracts.geometry.simplify(0.05)
#     # print
    

#     # print(tracts.columns)
#     gdf_wgs84 = tracts.to_crs({'init': 'epsg:4326'})
#     response = gdf_wgs84.to_json()
#     return HttpResponse(response, content_type="application/json")

def master_gis(request, profile):
    worker = profile.split("_")[0]
    df = prepare_data_frame(request, profile)

    if("payment_status" in profile):
        if not has_permission(request.user, 'view_performance_gis'):
            return render_permission_denied(request)

    elif("payment" in profile):
        if not has_permission(request.user, 'view_payment_gis'):
            return render_permission_denied(request)
    else:
        if not (has_permission(request.user, 'view_profile_gis') or has_permission(request.user, 'view_nhp_profile_gis')):
            return render_permission_denied(request)
    

    last_synced = get_last_synced(request)

    headers_with_type = get_columns_with_type(df)
    # headers_with_type = dict([(k, str(v)) for k, v in headers_with_type.items()])

    template = loader.get_template('admin_panel/master_gis.html')
    columns = df.columns.tolist()
    context = {  
    'last_synced': last_synced,
    'headers_with_type':headers_with_type,
    'profile' : profile,
    'worker': worker,
    'map': ''
	}
    response = HttpResponse(template.render(context, request))
    response.set_cookie('active_tab', 'gis')
    return response

def process_mysql_filter(df, sql_query):
    from pandasql import sqldf
    query = "SELECT * FROM df WHERE %s;" %sql_query
    print(query)
    pysqldf = sqldf(query, {'df':df})
    # print(pysqldf)
    return pysqldf

def process_advance_filter(df, advance_filter_params):
    try:
        print(advance_filter_params)
        # advance_filter = json.loads(advance_filter_params)
        advance_filter = advance_filter_params
        advance_operator = ['in', 'contains', 'startswith', 'endswith']
        advance_filter = list(advance_filter.values())
        print("x"*50)
        print(len(advance_filter))
        for idx in range( 0, len(advance_filter), 3):
            attribute = advance_filter[idx]
            operator = advance_filter[idx+1]
            value =  advance_filter[idx+2]
            print(attribute, operator, value)
            print("x"*50)

            print(advance_operator)
            if(operator not in advance_operator):
                #print(attribute + " " + operator + " " + value)
                if str(value).isdigit():
                    query = "`{0}` {1} {2}".format(attribute, operator, value)
                    print(query)
                    df.query(query, inplace=True)
                    # df.query(attribute + " " + operator + " " + str(value) , inplace = True)
                else:
                    query = "`{0}` {1} '{2}'".format(attribute, operator, value)
                    print(query)
                    df.query(query, inplace=True)
                    # df.query(attribute + " " + operator + " '" + value + "'", inplace = True)
                # #print(df.district_name)
            else:
                if(operator == "in"):
                    value = value.split(',')
                    #print("*********", value)
                    df = df[df[attribute].isin(value)]
                elif(operator == "contains"):
                    df = df[df[attribute].str.contains(value, case=False)]
                elif(operator == "startswith"):
                    df = df[df[attribute].str.startswith(value)]
                elif(operator == "endswith"):
                    df = df[df[attribute].str.endswith(value)]
    except Exception as e :
        print(str(e), "danish")
        pass
    return df


# Ajax based Function to render datatable by applying filter


def master_record_ajax(request, profile):
    col = 0
    headers = []
    while(True):
        data = request.POST.get('columns['+str(col)+'][data]', None)
        if(data):
            headers.append(data)
            col += 1
        else:
            break
    advance_filter = json.loads(request.POST.get('filters', "[]"))
    print(advance_filter, "danish")

    if(advance_filter):
        for filter in advance_filter:
            headers.append(filter["attr"])
    # if(advance_filter):
    #     print(advance_filter)
    #     xadvance_filter = list(json.loads(advance_filter).values())
    #     for idx in range( 0, len(xadvance_filter), 3):
    #         headers.append(xadvance_filter[idx])

            
    df = prepare_data_frame(request, profile, headers)

    

    get_data_frame_function = request.POST.get('get_data_frame_function')
    print(get_data_frame_function)
    if get_data_frame_function:
        if get_data_frame_function :
            if("_not_paid_frame" in get_data_frame_function):
                df = eval(get_data_frame_function)(df)
                
    if(advance_filter):
        print("Advance filter present")
        df = filter_frame(df, advance_filter)
        # df = process_advance_filter(df, advance_filter)
    else:
        print("No advance filter")
    
    
    
    # f = {"RBF Amount": "mean"}

    # df = df.groupby(["core_orgUnit", "RBF Cycle"], as_index=False).agg(f).reset_index(drop=True)

    # print(df["RBF Amount"])

    # ratios = df.groupby(['core_orgUnit', 'RBF Cycle']).apply(lambda x: (x['RBF Amount'].mode() / x['RBF Amount'].count()) ).to_dict()

    # df['ctype'] = df['RBF Amount'].map(ratios)

    # df = df.groupby(['core_orgUnit', 'RBF Cycle']).apply(lambda x: x['RBF Amount'].sum()/5000000000).reset_index(drop=True)


    # df = df.groupby(['core_orgUnit', 'RBF Cycle'])['core_orgUnit'].transform("count").reset_index()
    # print(df)
    # grouped = df.groupby(['core_orgUnit', 'RBF Cycle'])
    # for name, df_group in grouped:
    #     print(name, group)

    #     # print('\nCREATE TABLE {}('.format(group_name))

    

    # My SQL QUery FIlter
    sql_filter = request.POST.get('sql_filter', None)
    if sql_filter:
        df = process_mysql_filter(df, sql_filter)

    start = int(request.POST.get('start'))
    size = int(request.POST.get('length'))
    
    column_number = request.POST.get('order[0][column]')
    column_name = request.POST.get('columns['+column_number+'][data]')

    # print(headers)
    order = request.POST.get('order[0][dir]')
    
    # df = df[headers]
    # df = df.drop_duplicates()

    # max_cycle = df['RBF Cycle'].max()
    # print(max_cycle, type(max_cycle))

    total = len(df.index)
    search = request.POST.get('search[value]')
    if(search):
        # mask = df.apply(lambda x: x.apply(str).str.startswith(search, case=False, na=False))
        mask = np.column_stack([df[col].apply(str).str.contains(search, case=False,na=False) for col in df])
        df = df[mask.any(axis=1)]
        filter_total = len(df.index)
    else:
        filter_total = total
    try:
        if(order == 'asc'):
            df = df.sort_values([column_name], ascending=[True])
        else:
            df = df.sort_values([column_name], ascending=[False])
    except:
        #print("Column %s has problamatic Datatype it can't order"%column_name)
        pass
    

    export_file = request.POST.get('export', None)
    if export_file:
        from io import StringIO, BytesIO
        import xlsxwriter

        io = BytesIO()
        writer = pd.ExcelWriter(io, engine='xlsxwriter')
        del df['hash']
        df.to_excel(writer, 'T-Analytica Report')
        writer.save()
        writer.close()
        io.seek(0)
        
        response = StreamingHttpResponse(io, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        if export_file == 'Export Data':
            response['Content-Disposition'] = 'attachment; filename=%s' % profile+".xlsx"
        else:
            response['Content-Disposition'] = 'attachment; filename=%s' % export_file +".xlsx"
        # response['Content-Disposition'] = 'attachment; filename=%s' % profile+".xlsx"
        return response
    else:
        response = {}
        # response = df.to_dict(orient='split')
        df = df.iloc[start: (start+size)]
        df = df.round(2).astype(str)
        # print(df["total_score"])
        # print(df["the_number_of_women_who_had_received_at_least_4_ancs_from_any_provider_during_their_pregnancy_total_as_per_indicator_performance_reports_submitted"])
        response["draw"] = request.POST.get('draw')
        response["recordsTotal"] = total
        response["recordsFiltered"] = filter_total
        # for one_col in df.columns:
        #     print(df[one_col].dtype)
        #     if(df[one_col].dtype == 'datetime64[ns]' ):
        #         df[one_col] = df[one_col].dt.strftime('%Y-%m-%d').replace('NaT', '')
        # print(df.to_dict(orient='records'))
        df = df.replace({np.nan:None})
        response["data"] = df.to_dict(orient='records')
        return JsonResponse(response)

def get_frame_heads(request):
    df_name = request.GET.get('df_name')
    df = prepare_data_frame(request, df_name)
    columns = df.columns.sort_values().tolist()
    return HttpResponse(json.dumps(columns), content_type="application/json")

def get_head_vals(request):
    response = {}
    frame_name = request.GET.get('frame_name')
    df = prepare_data_frame(request, frame_name)
    head = request.GET.get('head')
    # df.fillna("N/A", inplace=True)
    column_vals = df[head].unique().tolist()
    if("_performance" in head):
        column_vals = arrange_column(column_vals, "performance")
    else:
        column_vals = sorted(column_vals)
    for column in column_vals:
        response[column] = column
    return HttpResponse(json.dumps(response), content_type="application/json")

def arrange_column(cols, category):
    updated_cols = []
    if(category == "performance"):
        column_vals = ["Excellent", "Good", "Average", "Below Average", "Poor", "Pending"]
        for one_std_col in column_vals:
            if(one_std_col in cols):
                updated_cols.append(one_std_col)
    # print(updated_cols, "="*50)     
    # print(cols, "="*50)     
    return updated_cols


def page_not_found(request, exception):
    return render(request,'admin_panel/404.html')
    # print(exception, "dansih"*20)




# import csv
# from django.http import StreamingHttpResponse

# class DummyFile:
#     def write(self, value_to_write):
#         return value_to_write

# def large_csv(request):
#     rows = ([str(i), str(2 * i), str(3 * i)] for i in range(555555))
#     writer = csv.writer(DummyFile())
#     data = [writer.writerow(row) for row in rows]
#     response = StreamingHttpResponse(data, content_type="text/csv")
#     response['Content-Disposition'] = 'attachment; filename="xyz"'
#     return response



# ============================= NHP Code ===========================================

def committee_keypoints(df, profile):

    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    base_drill = []

    number_of_committee =  len(df.index)
    # widget_chart_list.append(widget_chart(base_drill, "nhp_total_committee",  [number_of_committee], ["Active Committees"], "Committee Distribution"))


    total_vhc   = len(df[df["ctype"] == "VHC"].index)
    total_sc    = len(df[df["ctype"] == "HSCMC"].index)
    total_phc   = len(df[df["ctype"] == "HCMC"].index)
    widget_chart_list.append(widget_chart(base_drill, "nhp_committee_type",  [total_vhc, total_sc, total_phc], ["VHC", "HSCMC &", "HCMC" ], "Committees Types"))

    # women_leading = len(df[df["chairmain"] == "Women"])
    # widget_chart_list.append(widget_chart(["chairmain"], "committee_leadby",  [women_leading], ["Committees led by Women"], "Committee Leaders Gender wise"))

    
    womens = len(df[df["chairman"] == "Women"])
    widget_chart_list.append(widget_chart(["chairman"], "committee_chairman",  [womens], ["Women as Chairman"], "Chairman Gender wise"))


    womens = len(df[df["co_chairman"] == "Women"])
    widget_chart_list.append(widget_chart(["co_chairman"], "committee_co_chairman",  [womens], ["Women as Co-Chairman"], "Co Chairman Gender wise"))




    hcmc_population = df[df["ctype"] == "HCMC"]["Population Covered"].sum()/1000
    hscmc_population = df[df["ctype"] == "HSCMC"]["Population Covered"].sum()/1000
    vhc_population = df[df["ctype"] == "VHC"]["Population Covered"].sum()/1000
    widget_chart_list.append(widget_chart(base_drill, "nhp_total_committee_population",  [hcmc_population , vhc_population], ["K at HCMC,", "K at VHC"], "Population Covered"))


    total_population = df["Population Covered"].sum()/1000
    widget_chart_list.append(widget_chart([], "nhp_population_per_committee",  [total_population/number_of_committee], ["K Person/Committee"], "Population per Committee"))


    # x = df.groupby(["otg_year"])['OTG Amount'].agg('sum').reset_index()
    # x = x[x['OTG Amount'] == x['OTG Amount'].max()]
    # widget_chart_list.append(widget_chart([], "nhp_committee_otg_amount",  [x['OTG Amount'].iloc[0], x['otg_year'].iloc[0]], ["disbursed in", "" ], "Maximum OTG Disbursed"))

    maximum_enrollment = df["mou_year"].mode()[0]
    widget_chart_list.append(widget_chart(["mou_year", "mou_month", "mou_day"], "nhp_committee_enrollment",  [maximum_enrollment], ["has Maximum Enrollments" ], "Enrollment by Year"))


    number_of_bank = df["Bank Name"].nunique()
    widget_chart_list.append(widget_chart(["Bank Name", "IFSC Code"], "bank_engagement",  [number_of_bank], ["Bank in Current System"], "Bank Engagement"))

    


    
   
    





    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)


def committee_member_keypoints(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    base_drill = []

    number_of_worker =  len(df.index)
    widget_chart_list.append(widget_chart([], "nhp_total_committee_member", [number_of_worker], ["Total Mebers"], "Member Distribution"))

    number_of_femail = len(df[df["Sex"] == "F"].index)
    widget_chart_list.append(widget_chart([], "sex_distribution", [(number_of_femail/number_of_worker)*100], ["% Female Members"], "Gender Ratio"))


    member_min_age = int(df['Age'].min())
    member_max_age = int(df['Age'].max())
    
    widget_chart_list.append(widget_chart(["Age"], "nhp_age_distribution",  [member_min_age, member_max_age], ["to", "Years"], "Age Distribution"))


    qualification = "Graduate"
    total_qualified = len(df[df["Educational Qualification"] == qualification].index)
    widget_chart_list.append(widget_chart(["ctype"], "nhp_education_distribution",  [total_qualified], [qualification + " Members"], "Educational Profile"))


    invalid_mobile = len(df[df["Mobile number"] == "Invalid"].index)
    widget_chart_list.append(widget_chart([], "nhp_invalid_mobile",  [invalid_mobile], ["Invalid Mobile Numbers"], "Mobile Number Validation"))


    total_designation = df["Designation"].nunique()
    widget_chart_list.append(widget_chart(["ctype"], "nhp_member_designation",  [total_designation], ["Type of Designation"], "Designation Distribution"))

    
    
    
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)



def committee_rbf_manager(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []

    completing_this_month = len(df[df["current_month"] == 5].index)
    # widget_chart_list.append(widget_chart(["current_month"], "rbf_completion", [completing_this_month], ["Cycles being completed this month"], "RBF Cycles Distribution"))

    maximum_current_rbf = df["current_rbf"].mode()[0]
    maximum_current_rbf_count = len(df[df["current_rbf"] == maximum_current_rbf].index)
    widget_chart_list.append(widget_chart(["current_rbf", "current_month", "current_day"], "rbf_distribution",  [maximum_current_rbf_count], ["Committees in "+ str( int(maximum_current_rbf) ) +" RBF Cycle" ], "Maximum RBF belonging Committee"))


    amount_required = (df[df["current_month"] == 5]["OTG Amount"].sum())/1000
    # widget_chart_list.append(widget_chart(["current_month", "current_day"], "rbf_project_amount", [amount_required], ["K ₹ reuqired this month"], "Projected Amount"))


    late_rbfs = len(df[df["current_month"] > 5].index)
    # widget_chart_list.append(widget_chart(["current_rbf"], "late_rbf", [late_rbfs], ["Committees has overdue RBF"], "RBF not Assigned on TIme"))
    
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)


def committee_nhp_report(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []

    # activity = df["Activity Type"].nunique()
    # ongoing_cycle = len(df[df["rbf_state"] == "Ongoing"].index)
    widget_chart_list.append(widget_chart(["RBF Cycle"], "all_rbf_status", [""], ["RBF Cycle"], "RBF Progress"))


    for unit_code_name in ["Action_Plan_status", "Fund_Status_status", "IPR_-_1_status", "DVR_-_1_status", "IPR_-_2_status", "DVR_-_2_status", "Six_Monthly_Expenditure_status"]:
        unit = unit_code_name.replace("_status", "").replace("_"," ")
        
        # unit_count = len(df[df[unit_code_name] == "Not Completed"].index)
        widget_chart_list.append(widget_chart(["RBF Cycle"], unit_code_name, [""], [unit], unit + " Progress"))


    





    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)



def committee_action_plan(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []

    activity = df["Activity Type"].nunique()
    all_activity_cost = df["Activity Estimated funds required to conduct this activity"].sum()/1000000000
    widget_chart_list.append(widget_chart([], "rbf_activity_all", [all_activity_cost, activity], ["bn spend on", "Types of Activities"], "Overall Action Plan (Geography wise)"))

    state = "Ongoing"
    new_df = df[df["rbf_state"] == state]
    activity = new_df["Activity Type"].nunique()
    ongoing_activity_cost = new_df["Activity Estimated funds required to conduct this activity"].sum()/1000000000
    widget_chart_list.append(widget_chart([], "rbf_activity_ongoing", [ongoing_activity_cost, activity], ["bn spend on", "Types of Activities"], "Ongoing Action Plan (Geography wise)"))

    state = "Completed"
    new_df = df[df["rbf_state"] == state]
    activity = new_df["Activity Type"].nunique()
    completed_activity_cost = new_df["Activity Estimated funds required to conduct this activity"].sum()/1000000000
    widget_chart_list.append(widget_chart([], "rbf_activity_completed", [completed_activity_cost, activity], ["bn spend on", "Types of Activities"], "Completed Action Plan (Geography wise)"))


    widget_chart_list.append(widget_chart(["RBF Cycle"], "all_activity_by_rbf", [all_activity_cost, activity], ["bn spend on", "Types of Activities"], "Overall Action Plan (RBF wise)"))
    widget_chart_list.append(widget_chart(["RBF Cycle"], "ongoing_activity_by_rbf", [ongoing_activity_cost, activity], ["bn spend on", "Types of Activities"], "Ongoing Action Plan (RBF wise)"))
    widget_chart_list.append(widget_chart(["RBF Cycle"], "completed_activity_by_rbf", [completed_activity_cost, activity], ["bn spend on", "Types of Activities"], "Completed Action Plan (RBF wise)"))


    
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "all_activity_mean", [all_activity_cost, activity], ["bn spend on", "Types of Activities"], "Overall Action Plan (Average)"))
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "ongoing_activity_mean", [ongoing_activity_cost, activity], ["bn spend on", "Types of Activities"], "Ongoing Action Plan (Average)"))
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "completed_activity_mean", [completed_activity_cost, activity], ["bn spend on", "Types of Activities"], "Completed Action Plan (Average)"))
    


    # maximum_current_rbf = df["current_rbf"].mode()[0]
    # maximum_current_rbf_count = len(df[df["current_rbf"] == maximum_current_rbf].index)
    # widget_chart_list.append(widget_chart(["current_rbf", "current_month", "current_day"], "rbf_distribution",  [maximum_current_rbf_count], ["Committees in "+ str(maximum_current_rbf) +" RBF Cycle" ], "Maximum RBF belonging Committee"))


    # amount_required = (df[df["current_month"] == 6]["OTG Amount"].sum())/1000
    # widget_chart_list.append(widget_chart(["current_month", "current_day"], "rbf_project_amount", [amount_required], ["K ₹ reuqired this month"], "Projected Amount"))
    
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)

def vhc_target_indicators_consolidated(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    df = df[df["invalid_entry"] == "Valid"]

    type_of_indicator = 5 if "HCMC" in profile else 8
    widget_chart_list.append(widget_chart(["rbf_cycle"], "all_indicator", [type_of_indicator], [" Type of indicators present" ], "All Indicator Details"))

    target_met_percent = df["target_met_percent"].mean()
    widget_chart_list.append(widget_chart(["rbf_cycle"], "indicator_summry", [target_met_percent], ["% Target Met on Average"], "Overall Target Completed"))
   
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)


def committee_six_monthly_expenditure(df, profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []

    # activity = df["Activity Type"].nunique()
    approved_budget = df["Approved Budget"].sum()/100000
    six_month_expense = df["Six monthly Expenditure (Rs)"].sum()/100000
    widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_approve_vs_expense", [approved_budget, six_month_expense], ["L Approved and", "L Spent"], "Granted vs Approve vs Spent"))


    widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_approve_activity_based", [approved_budget], ["L Total Approved Budget"], "Approved Budget Activity-wise"))

    widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_expense_activity_based", [six_month_expense], ["L Total Spent"], "Total Expense Activity-wise"))
    

    widget_chart_list.append(widget_chart(["RBF Cycle"], "rbf_approve_vs_expense_activity_based", [approved_budget, six_month_expense], ["L Approved and", "L Spent"], "Plan vs Spent by committee types"))

    widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_totalfund_vs_expense_vs_balance", [approved_budget, six_month_expense], ["L Approved and", "L Spent"], "Total Fund vs Approved vs Spent vs Balance"))
    
    # quarter_1_spent = df["Quarter 1 Expenditure"].sum()/100000
    # quarter_2_spent = df["Quarter 2 Expenditure"].sum()/100000
    # widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_quarter_1_spent", [quarter_1_spent], ["L Spent in First Quarter"], "First Quarter Dsitribution"))
    # widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_quarter_2_spent", [quarter_2_spent], ["L Spent in Second Quarter"], "Second Quarter Dsitribution"))
    
    
    # new_df = df[df["Approved Budget"] == 0]
    # not_approve_six_month_expense = new_df["Six monthly Expenditure (Rs)"].sum()/100000
    # widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "not_approve_six_month_expense", [not_approve_six_month_expense], ["L Spent on Not Apprved Plans"], "Expense on not Approved Plans"))


    # quarter_1_spent = new_df["Quarter 1 Expenditure"].sum()/100000
    # quarter_2_spent = new_df["Quarter 2 Expenditure"].sum()/100000
    # widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_quarter_1_spent_not_approved", [quarter_1_spent], ["L Spent in First Quarter"], "First Quarter not Approved Expense"))
    # widget_chart_list.append(widget_chart(["RBF Cycle", "ctype"], "rbf_quarter_2_spent_not_approved", [quarter_2_spent], ["L Spent in Second Quarter"], "Second Quarter not Approved Expense"))
    
    
    # state = "Ongoing"
    # new_df = df[df["rbf_state"] == state]
    # activity = new_df["Activity Type"].nunique()
    # activity_cost = new_df["Activity Estimated funds required to conduct this activity"].sum()/100000
    # widget_chart_list.append(widget_chart([], "rbf_activity_ongoing", [activity_cost, activity], ["L spend on", "Types of Activities"], "Ongoing Action Plan (Geography wise)"))

    # state = "Completed"
    # new_df = df[df["rbf_state"] == state]
    # activity = new_df["Activity Type"].nunique()
    # activity_cost = new_df["Activity Estimated funds required to conduct this activity"].sum()/100000
    # widget_chart_list.append(widget_chart([], "rbf_activity_completed", [activity_cost, activity], ["L spend on", "Types of Activities"], "Completed Action Plan (Geography wise)"))


    # widget_chart_list.append(widget_chart(["RBF Cycle"], "all_activity_by_rbf", [activity_cost, activity], ["L spend on", "Types of Activities"], "Overall Action Plan (RBF wise)"))
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "ongoing_activity_by_rbf", [activity_cost, activity], ["L spend on", "Types of Activities"], "Ongoing Action Plan (RBF wise)"))
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "completed_activity_by_rbf", [activity_cost, activity], ["L spend on", "Types of Activities"], "Completed Action Plan (RBF wise)"))


    
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "all_activity_mean", [activity_cost, activity], ["L spend on", "Types of Activities"], "Overall Action Plan (Average)"))
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "ongoing_activity_mean", [activity_cost, activity], ["L spend on", "Types of Activities"], "Ongoing Action Plan (Average)"))
    # widget_chart_list.append(widget_chart(["RBF Cycle"], "completed_activity_mean", [activity_cost, activity], ["L spend on", "Types of Activities"], "Completed Action Plan (Average)"))
    


    # maximum_current_rbf = df["current_rbf"].mode()[0]
    # maximum_current_rbf_count = len(df[df["current_rbf"] == maximum_current_rbf].index)
    # widget_chart_list.append(widget_chart(["current_rbf", "current_month", "current_day"], "rbf_distribution",  [maximum_current_rbf_count], ["Committees in "+ str(maximum_current_rbf) +" RBF Cycle" ], "Maximum RBF belonging Committee"))


    # amount_required = (df[df["current_month"] == 6]["OTG Amount"].sum())/1000
    # widget_chart_list.append(widget_chart(["current_month", "current_day"], "rbf_project_amount", [amount_required], ["K ₹ reuqired this month"], "Projected Amount"))
    
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)


###########################################################################################################
                            #AUTHOR ABHISHEK AGRAWAL
                            #DATE 02 JULY 2021
                            # CHO PROFILE WIDGETS
############################################################################################################
def cho_profile(df,profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    
    
    total_cho = len(df['cho_id'])
    widget_chart_list.append(widget_chart(["STATE"], "total_cho",  [total_cho], ["Total No. of CHOs"], "Total CHO in Uttar Pradesh"))
    
    total = len(df['gender'])
    male = len(df[df['gender']=='Male'].index)
    womens = len(df[df["gender"] == "Female"])
    widget_chart_list.append(widget_chart(["gender"], "cho_gender_wise",  [womens,male,total], ["Females","Males","Total"], "CHO Gender wise"))
    no_data = len(df[df["Age-Group"] =="No Data"].index)
    incorrect_data = len(df[df["Age-Group"] =="DOB Incorrect"].index)
    widget_chart_list.append(widget_chart(["Age-Group"], "age",  [no_data,incorrect_data], ["No Data entered","Incorrect data"], "AGE Distribtion of CHO"))
    
    valid_mobile = len(df[df["mobile_status"] == "valid"].index)
    widget_chart_list.append(widget_chart(["mobile_status"], "cho_invalid_mobile",  [valid_mobile], ["Valid Mobile Numbers"], "Mobile Number Validation"))
    
    working_since = len(df[df["working_since_year"] == pd.datetime.now().year].index)
    working_since1 = len(df[df["working_since_year"] == 2006].index)
    widget_chart_list.append(widget_chart(["working_since_year"], "working_since",  [working_since,working_since1], ["Joined this year","Joined in 2006"], "CHO JOINING YEAR WISE"))
    
    
    
    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)          






def hwc_profile(df,profile):
    worker = profile.split("_")[0].upper()
    widget_chart_list = []
    
    
    sub_center = len(df["SUB CENTER"])
    widget_chart_list.append(widget_chart([], "sub_center",  [sub_center], ["No. of HWC"], "Total no. of HWC"))
    
    
    no_of_asha=0
    asha = df["asha_no"].astype(int).sum()
    widget_chart_list.append(widget_chart([], "asha",  [asha], ["No. of ASHA"], "Total no. of ASHA "))
    
    total = len(df['Electricity'])
    yes = len(df[df['Electricity']=='Yes'].index)/total*100
    no = len(df[df['Electricity']=='No'].index)/total*100
    widget_chart_list.append(widget_chart(["Electricity"], "electricity_in_subcenter",  [yes,no], ["% Electricty","% No Electricity"], "Electricity facilities in HWCs"))
    
    total = len(df['Water'])
    no= len(df[df['Water']=='No'].index)/total*100
    yes = len(df[df["Water"] == "Yes"].index)/total*100+len(df[df["Water"] == "Pipleline"].index)/total*100+len(df[df["Water"] == "Handpump"].index)/total*100
    widget_chart_list.append(widget_chart(["Water"], "water",  [yes,no], ["% HWCs Have water","% have no water"], "Water facility in HWC"))
    
    total_population = 0
    population = df["population"].astype(int).sum()
    widget_chart_list.append(widget_chart(["STATE"], "population",  [population], ["Total Population"], "Total Population covered"))


    statistics = {"worker": worker.lower()}
    return (statistics, widget_chart_list)          
