from dtwinpylib.dtwinpy.interfaceAPI import interfaceAPI
api = interfaceAPI()
api.indicator(logic=0.89,input= 0.93)
api.station_status(True, False,True, False, True)
api.queue_status(5,7,6,5,8)
api.RCT_server(8,15,32,1)