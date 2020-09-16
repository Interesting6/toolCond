# 7-7
import redis
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import datetime
import json
import os
import struct
import numpy as np
import threading
from ecci_sdk import Client

def now_time():
    return datetime.datetime.now()

def parse1(datas):
    ts,data = datas
    ts = ts.decode('utf-8')
    # print(ts)
    # print(ts.split('-')[0])
    float_data  = struct.unpack(str(int(len(data[b'Value']) / 4)) + 'f', data[b'Value'])  # sizeof float = 4
    # print(float_data)
    # orgin_count = data[b'Count'].decode('utf-8')
    # print("orgin_count = ", orgin_count)
    # print("sensor1 orgin_count",orgin_count)
    # completion_count = orgin_count.zfill(8)
    # print(np.array(float_data).reshape(-1,3).shape)
    return np.array(float_data).reshape(-1,3)

def parse2(datas):
    ts,data = datas
    float_data  = struct.unpack(str(int(len(data[b'Value']) / 4)) + 'f', data[b'Value'])  # sizeof float = 4

    # orgin_count = data[b'Count'].decode('utf-8')

    # completion_count = orgin_count.zfill(8)
    # print("sensor2 completion_count",completion_count)

    return np.array(float_data).reshape(-1,3)

# 转存传感器1的数据
def archived_data_sensor1(rs,client):
    begin = datetime.datetime.now()
    results = rs.xrange("simulation",count=600)

    results= rs.xreadgroup('group1', 'xjtu', {'sensor11': ">"}, count=600,noack=True)
    if(len(results)!=0):
        print(" sensor1 len(results[0][1]) = ",len(results[0][1]))
        arrays_list = list(map(parse1,results[0][1]))
        # print("arrays_list=",arrays_list)
        concatenate_arrays = np.concatenate(arrays_list, axis=0)
        # print("concatenate_arrays=", concatenate_arrays)
        print("concatenate_arrays shape = ", concatenate_arrays.shape)
        print("concatenate_arrays type = ", type(concatenate_arrays))
        # client.write_points(influxdb_datas,batch_size=1)        # batch_size设为1是因为设置为其他将无法插入所有数据，如batch_size设为300时，300条数据时间戳均相同，导致只插入len(result)/batch_size的条数
        payload={"type":"data","contents":{"data":concatenate_arrays,"sensor":1, "time":now_time()}}
        client.publish(payload, "feature-extraction-1")
        # print('insert success')
        end = datetime.datetime.now()
        spend_time = end - begin
        print("spend_time=",spend_time)
    else:
        print("No new data is generated")

# 转存传感器2的数据
def archived_data_sensor2(rs,client):
    begin = datetime.datetime.now()

    results= rs.xreadgroup('group1', 'xjtu', {'sensor21': ">"}, count=600,noack=True)
    if(len(results)!=0):
        print(" sensor2 len(results[0][1]) = ",len(results[0][1]))
        arrays_list = list(map(parse1,results[0][1]))
        # print("arrays_list=",arrays_list)
        concatenate_arrays = np.concatenate(arrays_list, axis=0)
        # print("concatenate_arrays=", concatenate_arrays)
        print("concatenate_arrays shape = ", concatenate_arrays.shape)
        # client.write_points(influxdb_datas,batch_size=1)
        payload={"type":"data","contents":{"data":concatenate_arrays,"sensor":2, "time":now_time()}}
        client.publish(payload, "feature-extraction-1")
        # print('insert success')
        end = datetime.datetime.now()
        spend_time = end - begin
        print("spend_time=",spend_time)
    else:
        print("No new data is generated")


if __name__=="__main__":
    try:
        # 连接传感器1  redis
        # rs1 = redis.Redis(host="192.168.0.117", port=6379, db=0)
        rs1 = redis.Redis(host="192.168.0.21", port=6379, db=0)
        rs1.xgroup_destroy("sensor11", "group1")   #删除消费组
        response1=rs1.xgroup_create('sensor11','group1','$') #创建消费组    0-0  # 从头部开始消费
        print("sensor1 response = ", response1)
    except Exception as e:
        print("sensor1 redis error = ",e)

    try:
        # 连接传感器2  redis
        # rs2 = redis.Redis(host="192.168.0.117", port=6380, db=0)
        rs2 = redis.Redis(host="192.168.0.22", port=6380, db=0)
        rs2.xgroup_destroy("sensor21", "group1")   #删除消费组
        response2=rs2.xgroup_create('sensor21','group1','$') #创建消费组    0-0  # 从头部开始消费
        print("sensor2 response = ", response2)
    except Exception as e:
        print("sensor2 redis error = ",e)

    ecci_client = Client()
    mqtt_thread = threading.Thread(target=ecci_client.initialize)
    mqtt_thread.start()

    try:
        sched = BlockingScheduler()
        sched.add_job(archived_data_sensor1, 'interval', seconds=3,args=[rs1,ecci_client],id="archived_sensor1")
        sched.add_job(archived_data_sensor2, 'interval', seconds=3,args=[rs2,ecci_client],id="archived_sensor2")
        sched.start()
    except Exception as e:
        print(e)
