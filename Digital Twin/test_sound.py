from dtwinpylib.dtwinpy.helper import Helper
helper = Helper()
(tstr, t1) = helper.get_time_now()
helper.printer("hello", 'green', play= True)
(tstr, t2) = helper.get_time_now()
delta_t= t2 - t1
print(delta_t)


