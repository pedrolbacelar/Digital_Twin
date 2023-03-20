import requests
import json
import base64
import datetime

class interfaceAPI():
    def __init__(self, asset_name = "5s_Model", account = "premium"):
        self.asset_name = asset_name
        self.account = account
        self.bearer_token_flag = False
        self.asset_id_flag = False
        self.bearer_token = self.bearerToken()
        self.tokentime = datetime.datetime.now().timestamp()
        if self.bearer_token_flag is True:
            self.asset_id = self.get_assetid()
        if self.bearer_token_flag and self.asset_id_flag is True:
            print(f"API object created for '{self.asset_name}' using '{self.account}' account.")
        else:
            print(f"\nAPI object failed to create. Check whether '{self.account}' and '{self.asset_name}' is the correct account and asset name.\n\n")

    def token_check(self):
        t_now = datetime.datetime.now().timestamp()
        if (t_now - self.tokentime) > 1700:
            self.bearer_token = self.bearerToken()
            print(self.bearer_token)


    def bearerToken(self):
        if self.account == "alex":
            #--- App details from developer cockpit
            CLIENT_ID = "iiotuxpc-testdm-v1.0.0"
            CLIENT_SECRET = "UvwnNgdc8Y0KsE7IZSFy2Jp28kQGzAd0fEHXcDOWbIX"
            APP_NAME = "testdm"
            APP_VERSION = "v1.0.0"
            HOST_TENANT = "iiotuxpc"
            USER_TENANT = "iiotuxpc"
            credential_create_time = "23/02/2023::18:53"

            #--- generate access token
            id = CLIENT_ID
            secret = CLIENT_SECRET
            encode_msg = id + ":" + secret
            token = base64.b64encode(encode_msg.encode("utf-8")).decode("utf-8")

            url = "https://gateway.eu1.mindsphere.io/api/technicaltokenmanager/v3/oauth/token"

            payload = json.dumps({
            "grant_type": "client_credentials",
            "appName": APP_NAME,
            "appVersion": APP_VERSION,
            "hostTenant": HOST_TENANT,
            "userTenant": USER_TENANT
            })
            headers = {
            'X-SPACE-AUTH-KEY': "Basic " + token,
            'Content-Type': 'application/json'
            }

            token_response = requests.request("POST", url, headers=headers, data=payload)
            # print(token_response.text)
            if "access_token" in json.loads(token_response.text):
                bearer_token = json.loads(token_response.text)["access_token"]
                self.bearer_token_flag = True
                return(bearer_token)
            else:
                print("\n\nBearer token failed to generate.\nTrying to generate bearer token again ......\n...\n...")
                token_response = requests.request("POST", url, headers=headers, data=payload)
                if "access_token" in json.loads(token_response.text):
                    bearer_token = json.loads(token_response.text)["access_token"]
                    self.bearer_token_flag = True
                    return(bearer_token)
                else:
                    print("\n\nBearer token failed to generate. Please check the account name and the client credentials.\n\n")
            
        elif self.account == "premium":
            #--- App details from developer cockpit
            APP_NAME = "cannon"
            APP_VERSION = "v1.0.0"
            HOST_TENANT = "mswitops"
            USER_TENANT = "mswitpro"
            credential_create_time = "created by organizer"

            #--- access token provided by the organizer
            token = "bXN3aXRvcHMtY2Fubm9uLXYxLjAuMC0xMzc4NTgwMjQ6U0RxUFpabjl0YkJodUM2V0VwUGFONEdZbzJFN2k0dWpBcEJTTlUzOUJ5QQ=="

            url = "https://gateway.eu1.mindsphere.io/api/technicaltokenmanager/v3/oauth/token"

            payload = json.dumps({
            "grant_type": "client_credentials",
            "appName": APP_NAME,
            "appVersion": APP_VERSION,
            "hostTenant": HOST_TENANT,
            "userTenant": USER_TENANT
            })
            headers = {
            'X-SPACE-AUTH-KEY': "Basic " + token,
            'Content-Type': 'application/json'
            }

            token_response = requests.request("POST", url, headers=headers, data=payload)
            # print(token_response.text)
            if "access_token" in json.loads(token_response.text):
                    bearer_token = json.loads(token_response.text)["access_token"]
                    self.bearer_token_flag = True
                    return(bearer_token)
            else:
                print("\n\nBearer token failed to generate.\nTrying to generate bearer token again ......\n...\n...")
                token_response = requests.request("POST", url, headers=headers, data=payload)
                if "access_token" in json.loads(token_response.text):
                    bearer_token = json.loads(token_response.text)["access_token"]
                    self.bearer_token_flag = True
                    return(bearer_token)
                else:
                    print("\n\nBearer token failed to generate. Please check the account name and the client credentials.\n\n")

        else:
            print("Error:\n\tAccount not found.\n\tVerify the accuracy of account name. Account name is case sensitive.")

    def get_assetid(self):
        #--- get list of assets
        url = "https://gateway.eu1.mindsphere.io/api/assetmanagement/v3/assets"
        payload={}
        headers = {
        'Authorization': 'Bearer ' + self.bearer_token
        }
        assets_list_response = requests.request("GET", url, headers=headers, data=payload)  # GET API call for assets_list
        assets_list=json.loads(assets_list_response.text)
        assets_count = assets_list["page"]["totalElements"]     # total number of assets available
        
        try:
            #--- find the asset_name and the corresponding ID in the assets_list
            for ii in range(0,assets_count):
                if assets_list["_embedded"]["assets"][ii]["name"] == self.asset_name:
                    asset_id = assets_list["_embedded"]["assets"][ii]["assetId"]
                    # print(asset_name,asset_Id)
                    self.asset_id_flag = True
                    return(asset_id)
            else: print("Error:\n\tAsset not found in the assets list.\n\tVerify the accuracy of asset name and the assets list. Asset name is case sensitive.")
        except IndexError:
            print("Error:\n\tAsset not found in the assets list.\n\tVerify the accuracy of asset name and the assets list. Asset name is case sensitive.")

    def get_timeseries(self, aspect_name, from_time, to_time):
        
        data_condition = "?from=" + from_time + "&to=" + to_time    # query condition with from and to time period
        end_point = "iottimeseries/v3/timeseries/" + self.asset_id + "/" + aspect_name + data_condition
        base_url = "https://gateway.eu1.mindsphere.io/api/"
        url = base_url + end_point

        payload={}
        headers = {
        'Authorization': 'Bearer ' + self.bearer_token
        }

        time_series_response = requests.request("GET", url, headers=headers, data=payload)  # GET API call
        print(time_series_response.text)
        time_series=json.loads(time_series_response.text)
        return(time_series)
    

    def put_timeseries(self, aspect_name, payload):
                
        end_point = "iottimeseries/v3/timeseries/" + self.asset_id + "/" + aspect_name
        base_url = "https://gateway.eu1.mindsphere.io/api/"
        url = base_url + end_point

        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': "Bearer " + self.bearer_token
        }

        response = requests.request("PUT", url, headers=headers, data=payload)  # PUT API call
        if not response.text:
            print("Data PUT successfully.")
        else:
            print("Error:\n\t",response.text)
            print("Trying again ...................\n....\n....")
            response2 = requests.request("PUT", url, headers=headers, data=payload)  # PUT API call
            if not response2.text:
                print("Data PUT successfully.")
            else:
                print("\nPUT method failed. Attention required.")
                print("Error:\n\t",response2.text)

    def indicator(self, logic, input):
        aspect_name = "validation_indicator"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "logic" : logic,
            "input" : input
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

    def station_status(self, station_1, station_2, station_3, station_4, station_5):
        aspect_name = "station_status"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "station_1" : station_1,
            "station_2" : station_2,
            "station_3" : station_3,
            "station_4" : station_4,
            "station_5" : station_5
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

    def queue_status(self, queue_1, queue_2, queue_3, queue_4, queue_5):
        aspect_name = "queue_status"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "queue_1" : queue_1,
            "queue_2" : queue_2,
            "queue_3" : queue_3,
            "queue_4" : queue_4,
            "queue_5" : queue_5
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

    def RCT_server(self, part_id, path_1, path_2, queue_id):
        aspect_name = "RCT_server"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "part_id" : part_id,
            "path_1" : path_1,
            "path_2" : path_2,
            "queue_id" : queue_id
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

