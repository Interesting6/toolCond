from ecci_sdk import Client
import threading
import time
import argparse
import joblib
import numpy as np

# parser = argparse.ArgumentParser(description='manual to this script')
# parser.add_argument('--Pub', type=str, default='predictor')
# args = parser.parse_args()
# Pub = args.Pub



clus1 = joblib.load("./models/cluster1.m")
clus2 = joblib.load("./models/cluster2.m")



def receive_mqtt_msg():
    while True:
        # Message queues for 'data' type
        data_msg_queue = ecci_client.get_sub_data_payload_queue()
        if not data_msg_queue.empty():
            data_msg = data_msg_queue.get()
            # print(data_msg, "data_msg")
            feats = data_msg["features"]
            if feats.ndim == 1:
                feats = feats.reshape(1, 6, 10)
            feats1 = feats[:, 0, [0,7,6]]
            feats2 = feats[:, 4, [0,7,6]]

            cls1 = clus1.predict(feats1)
            cls2 = clus1.predict(feats2)

            res1 = np.append(feats1, cls1)
            res2 = np.append(feats2, cls2)

            payload={"type": "data", "contents": {"s1":res1, "s2":res2, "results_type":"feature", "time":data_msg["time"]}}

            try:
                ecci_client.publish(payload, "save-1")
                print(payload, "payload")
                # with open("./results.txt", "a") as f:
                #     f.write(str(data) + "\n")
            except Exception as e:
                print(e)



if __name__ == "__main__":
    #msgQueue=queue.Queue()
    ecci_client = Client()
    mqtt_thread = threading.Thread(target = ecci_client.initialize)
    mqtt_thread.start()
    thread_mqtt = threading.Thread(target = receive_mqtt_msg())
    # 处理消息

    thread_mqtt.start()
    thread_mqtt.join()


