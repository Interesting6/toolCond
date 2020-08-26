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


model_run = joblib.load("./models/on.m")


def receive_mqtt_msg():
    while True:
        # Message queues for 'data' type
        data_msg_queue = ecci_client.get_sub_data_payload_queue()
        if not data_msg_queue.empty():
            data_msg = data_msg_queue.get()
            # print(data_msg, "data_msg")
            feats = data_msg["features"]
            if feats.ndim == 1:
                feats = feats.reshape(1, -1)

            on = model_run.predict(feats)

            payload={"type": "data", "contents": {"running": on.item(), "results_type":"running", "time":data_msg["time"]}}

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


