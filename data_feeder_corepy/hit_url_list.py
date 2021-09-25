# import requests

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import time, datetime
import dateutil.relativedelta


class AnalyticaFeeder:

    def __init__(self, host, **kwargs):
        self.bcpm_zip_gen_Urls = {
            'asha'                      : 'http://nhm-bcpm.in/mapping/get-master-data_cron.php',
            'sangini'                   : 'http://nhm-bcpm.in/mapping/get-master-sangini_cron.php',
            'anm'                       : 'http://nhm-bcpm.in/mapping/get-master-anm_cron.php',
            'asha_payment'              : 'http://nhm-bcpm.in/nhm/findAshareport_json_cron.php',
            'asha_payment_status'       : 'http://nhm-bcpm.in/nhm/payment_status_cron.php',
            'sangini_payment'           : 'http://www.nhm-bcpm.in/nhm/findSanginireport_json_cron.php',
            'sangini_payment_status'    : 'http://www.nhm-bcpm.in/nhm/sangini_status_cron.php'
        }

        self.user = "tattva"
        self.password = "demo1234"
        # self.user = "tattva"
        # self.password = "demo1234"
        self.HOST    = host

        self.from_session = kwargs.get("from_session", datetime.datetime.today().date())
        self.to_session = kwargs.get("to_session", datetime.datetime.today().date())
        

    def loadURL(self, url):
        start = time.time()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(url + " ==Completed==")
        except Exception as e:
            print(url  + " ==Failed==" + str(e))
        done = time.time()
        elapsed = done - start
        print(elapsed, "*"*20)

    def availbale_sessions(self):
        if(isinstance(self.from_session, str)):
            self.from_session = datetime.datetime.strptime(self.from_session, "%B-%Y").date()
        if(isinstance(self.to_session, str)):
            self.to_session = datetime.datetime.strptime(self.to_session, "%B-%Y").date()
        while(self.from_session <= self.to_session):
            yield(self.from_session)
            self.from_session += dateutil.relativedelta.relativedelta(months=1)

    def start(self): 
        is_profile_updated = False
        is_server_data_updated = False
        for one_session in self.availbale_sessions():
            
            with requests.session() as client:
                client.get(self.HOST)
                csrftoken = client.cookies['csrftoken']
                login_data = {'username':self.user,'password':self.password, 'csrfmiddlewaretoken':csrftoken}
                d = client.post(self.HOST+"login/" ,data=login_data)
                print("User Logged In", d)

                for module, url in self.bcpm_zip_gen_Urls.items():
                    if( module == "asha" or module == "sangini" or module == "anm"):
                        if(is_profile_updated):
                            print("No need for %s module it already completed"%module)
                            continue
                    if not is_server_data_updated:
                        hit_url = url + "/?m=" + str(one_session.month) + "&y=" + str(one_session.year)
                        self.loadURL(hit_url)
                    # hit_url = self.HOST + "dashboard/prepare_redis/"+ module + "/?session=" + one_session.strftime("%B-%Y")
                    # hit_url = self.HOST + "admin/prepare_redis/"+ module + "/?session=" + one_session.strftime("%B-%Y")
                    # x = client.get(hit_url)
                    # print(x.text)
            is_profile_updated = True
                    
# call_AnalyticaFeeder = AnalyticaFeeder("127.0.0.1", from_session="May-2019", to_session="August-2019")
# call_AnalyticaFeeder = AnalyticaFeeder("http://192.168.0.7:4000/")

# call_AnalyticaFeeder = AnalyticaFeeder("http://127.0.0.1:8000/", from_session="August-2019", to_session="October-2019")
call_AnalyticaFeeder = AnalyticaFeeder("http://127.0.0.1:8000/", from_session="April-2019", to_session="January-2020")
# call_AnalyticaFeeder = AnalyticaFeeder("http://45.114.143.31:5000/", from_session="April-2019", to_session="October-2019")
call_AnalyticaFeeder.start()