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
            self.tokentime = t_now      #--- updating the time when the next token was created.
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
                    break
            else:
                print("Error:\n\tAsset not found in the assets list.\n\tVerify the accuracy of asset name and the assets list. Asset name is case sensitive.")

            return(asset_id)
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
            print(f"Following data was PUT successfully to '{aspect_name}' aspect: {payload}")
        else:
            print(f"Error during '{aspect_name}' PUT method:\n\t",response.text)
            print("Trying again ...................\n....\n....")
            response2 = requests.request("PUT", url, headers=headers, data=payload)  # PUT API call
            if not response2.text:
                print(f"Following data was PUT successfully to '{aspect_name}' aspect: {payload} in the second attempt.")
            else:
                print(f"\nPUT method failed for '{aspect_name}' again. Attention required !!!")
                print("Error:\n\t",response2.text)

    #--- write validation indicator [logic,input] = [float, float]
    def indicator(self, data):
        aspect_name = "validation_indicator"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "logic" : data[0],
            "input" : data[1]
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

    #--- write station_status [station1, station2, station3, station4, station5] = [boolean, boolean, boolean, boolean, boolean]
    def station_status(self, data):
        aspect_name = "station_status"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "station_1" : data[0],
            "station_2" : data[1],
            "station_3" : data[2],
            "station_4" : data[3],
            "station_5" : data[4]
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

    #--- write queue_status [queue1, queue2, queue3, queue4, queue5] = [int, int, int, int, int]
    def queue_status(self, data):
        aspect_name = "queue_status"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "queue_1" : data[0],
            "queue_2" : data[1],
            "queue_3" : data[2],
            "queue_4" : data[3],
            "queue_5" : data[4]
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

    #--- write queue_status [part id, path 1, path 2, queue id] = [int, float, float, int]
    def RCT_server(self, data):
        aspect_name = "RCT_server"
        payload = json.dumps([
            {
            "_time" : datetime.datetime.utcnow().isoformat() + 'Z',
            "part_id" : data[0],
            "path_1" : data[1],
            "path_2" : data[2],
            "queue_id" : data[3]
            }
        ])
        self.token_check()
        self.put_timeseries(payload = payload, aspect_name=aspect_name)

