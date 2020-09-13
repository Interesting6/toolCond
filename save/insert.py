from ecci_sdk import Client
import threading
from queue import Queue
import time
import cx_Oracle
import os

id_ds = -1
id_irons = -1
id_life = -1
id_running = -1
id_cls = -1

iron_flag = 0
knife_flag = 0
running_flag = 0

def receive_mqtt_msg(cursor):
    global id_irons
    global id_life
    global id_running
    global id_ds
    global id_cls

    global iron_flag
    global knife_flag
    global running_flag

    while True:
        # Message queues for 'data' type
        data_send_queue = ecci_client.get_sub_data_sender_queue()
        data_msg_queue = ecci_client.get_sub_data_payload_queue()
        #
        if not data_msg_queue.empty():
            data_msg = data_msg_queue.get()
            send_msg = data_send_queue.get()
            # 
            print("send_msg:", send_msg)
            print("data_msg:", data_msg)
            

            if send_msg == "datasource":
                pass

            elif send_msg == "feature-extraction-1": 
                id_ds += 1
                t = [data_msg["time"], id_ds]
                param = [ t + d_s.tolist() for d_s in data_msg["down_sample"]]
                # print(f"------DownSample-------,{param}")
                cursor.executemany('insert into downsample_table(time, id, A1, A2, A3, V1, V2, V3) values(:0,:1,:2,:3,:4,:5,:6,:7)', param)
                
            elif send_msg == "cluster-1": 
                id_cls += 1
                param = [data_msg["time"], id_cls] + data_msg["s1"].tolist() + data_msg["s2"].tolist()
                print(f"------Cluster-------,{param}")
                insert_sql = 'insert into cluster_table(time, id, A1, A2, A3, AC, V1, V2, V3, VC) values(:0,:1,:2,:3,:4,:5,:6,:7,:8,:9)'
                cursor.execute(insert_sql, param)
            
            elif send_msg == "irons-1":
                data_msg.pop('results_type')
                if data_msg["iron"] != 0:
                    iron_flag = 1
                id_irons += 1
                insert_sql = "insert into iron_table(time, id, iron_score, iron) values(:time, :num, :iron_score, :iron)"
                param = {**data_msg, "num": id_irons}
                # print("---------:", param)
                cursor.execute(insert_sql, param)


            elif send_msg == "life-1":
                data_msg.pop('results_type')
                if data_msg["life"] != 0:
                    knife_flag = 1
                id_life += 1
                insert_sql = "insert into life_table(time, id, life_score, life) values(:time, :num, :life_score, :life)"
                param = {**data_msg, "num": id_life} 
                # print("---------:", param)
                cursor.execute(insert_sql, param)
                
            elif send_msg == "running-1":
                data_msg.pop('results_type')
                id_running += 1
                param = {**data_msg, "num": id_running}
                if data_msg["running"] == 1:
                    running_flag = 1
                    # param不变，其running为1
                if data_msg["running"] == 0 and running_flag == 1:
                    if iron_flag == 1 and knife_flag == 1:
                        param["running"] = 5
                    elif iron_flag == 1 and knife_flag == 0:
                        param["running"] = 3
                    elif iron_flag == 0 and knife_flag == 1:
                        param["running"] = 2
                    else:
                        param["running"] = 4
                    running_flag = 0
                    iron_flag = 0
                    knife_flag = 0

                insert_sql = "insert into running_table(time, id, operate) values(:time, :num, :running)"
                # print("---------:", param)
                cursor.execute(insert_sql, param)

            else:
                raise ValueError("send_msg error!")
            
            db.commit()
            print(f"{send_msg} insert successed!")
            
        # else:
        #     print("empty!")


if __name__ == "__main__":

    os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.UTF8'  #设置语言环境
    db = cx_Oracle.connect('test','test','39.99.136.63:1521/helowin')   #连接数据库   用户名、密码、数据库名
    cursor = db.cursor()

    sql1 = cursor.execute('select table_name from user_tables')  #查询数据
    table_data = sql1.fetchmany(10) 
    if len(table_data) != 0:
        table_data = [item[0] for item in table_data]
        if "DOWNSAMPLE_TABLE" in table_data:
            cursor.execute("drop table downsample_table")
        if "CLUSTER_TABLE" in table_data:
            cursor.execute("drop table cluster_table")
        if "IRON_TABLE" in table_data:
            cursor.execute("drop table iron_table")
        if "LIFE_TABLE" in table_data:
            cursor.execute("drop table life_table")
        if "RUNNING_TABLE" in table_data:
            cursor.execute("drop table running_table")
        # cursor.commit()

    create_table = """
        create table downsample_table(
            time varchar(30),
            id integer,
            A1 float,
            A2 float,
            A3 float,
            V1 float,
            V2 float,
            V3 float
        )
    """       
    create_flag = cursor.execute(create_table)  

    create_table = """
        create table cluster_table(
            time varchar(30),
            id integer,
            A1 float,
            A2 float,
            A3 float,
            AC float,
            V1 float,
            V2 float,
            V3 float,
            VC float
        )
    """       
    create_flag = cursor.execute(create_table)  

    create_table = """
        create table iron_table(
            time varchar(30),
            id integer,
            iron_score float,
            iron integer 
        )
    """       
    create_flag = cursor.execute(create_table)  

    create_table = """
        create table life_table(
            time varchar(30),
            id integer,
            life_score float,
            life integer 
        )
    """       
    create_flag = cursor.execute(create_table)  

    create_table = """
        create table running_table(
            time varchar(30),
            id integer,
            operate integer 
        )
    """
    create_flag = cursor.execute(create_table)  
    
    try:
        #msgQueue=queue.Queue()
        ecci_client = Client()
        mqtt_thread = threading.Thread(target = ecci_client.initialize)
        mqtt_thread.start()
        thread_mqtt = threading.Thread(target = receive_mqtt_msg, args=(cursor, ))
        # 处理消息
        thread_mqtt.start()
        thread_mqtt.join()
    except Exception as e:
        print(e)
    finally:
        db.close()

