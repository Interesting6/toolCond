from ecci_sdk import Client
import threading
from queue import Queue
from feature_extract_func import extract_feature
import time, datetime
import argparse
import numpy as np
import scipy.stats as sts

# parser = argparse.ArgumentParser(description='manual to this script')
# parser.add_argument('--Pub', type=str, default='feature_extractor')
# args = parser.parse_args()
# Pub = args.Pub

def now_time():
    return datetime.datetime.now()

def receive_mqtt_msg():

    feat = [0, 0]
    flag = [0, 0]
    freq = 2048
    while True:
        # Message queues for 'data' type
        data_msg_queue = ecci_client.get_sub_data_payload_queue()
        if not data_msg_queue.empty():
            data_msg = data_msg_queue.get()
            # print(data_msg, "data_msg")
            if data_msg["sensor"] == 1:
                s1_data = data_msg["data"]
                s1_time = data_msg["time"]
                # s1_len = len(s1_data)
                ds_s1 = s1_data[::freq, :]
                feat[0] = extract_feature(s1_data)
                flag[0] = 1
            else:
                s2_data = data_msg["data"]
                s2_time = data_msg["time"]
                # s2_len = len(s2_data)
                ds_s2 = s2_data[::freq, :]
                feat[1] = extract_feature(s2_data)
                flag[1] = 1


            if sum(flag) == 2:

                feat_array = np.concatenate(feat, axis=0)
                com_len = min(len(ds_s1), len(ds_s2)) - 1
                # print(f"----shape----------s1_data:{s1_data.shape}, s2_data:{s2_data.shape}" )
                s1_data_com = s1_data[:freq*com_len, :].reshape(com_len, freq, -1)
                s2_data_com = s2_data[:freq*com_len, :].reshape(com_len, freq, -1)

                s1_data_mean = s1_data_com.mean(1)
                s2_data_mean = s2_data_com.mean(1)
                s1_data_skew = sts.skew(s1_data_com, axis=1)
                s2_data_skew = sts.skew(s2_data_com, axis=1)
                s1_data_varmean = s1_data_com.var(1).mean(1, keepdims=True)
                s2_data_varmean = s2_data_com.var(1).mean(1, keepdims=True)

                ds = np.concatenate((ds_s1[:com_len], ds_s2[:com_len], s1_data_mean, s2_data_mean,
                            s1_data_varmean, s2_data_varmean, s1_data_skew, s2_data_skew), axis=1)

                sensor_time = str(max(s1_time, s2_time))
                payload1={"type": "data", "contents": {"down_sample": ds, "time":sensor_time, "results_type": "downsample"}}
                payload2={"type": "data", "contents": {"features": feat_array, "time":sensor_time}}
                feat = [0, 0]
                flag = [0, 0]
                try:
                    ecci_client.publish(payload1, "save-1")
                    ecci_client.publish(payload2, ["irons-1", "life-1", "running-1", "cluster-1"])
                    print("payload1", payload1,)
                    print("payload2", payload2,)
                except IOError:
                    print("error")



if __name__ == "__main__":
    #msgQueue=queue.Queue()
    ecci_client = Client()
    mqtt_thread = threading.Thread(target = ecci_client.initialize)
    mqtt_thread.start()
    thread_mqtt = threading.Thread(target = receive_mqtt_msg())
    # 处理消息

    thread_mqtt.start()
    thread_mqtt.join()


