#Push sample data to MySQL db

import MySQLdb
import random
import time
import datetime
last_pushed = time.time()
interval = 0.1 #seconds
while True:
    if (last_pushed + interval) < time.time():
        conn = MySQLdb.connect(host="localhost", user="root", passwd="Katerina27", db="sample_data")
        cursor = conn.cursor()

        value = random.randrange(200)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        users = [1,2]
        sensors = [1,2,3]
        user = users[random.randrange(2)]
        sensor = sensors[random.randrange(3)]
        statement = "INSERT INTO data (time,value,sensor_id,tenant_id) VALUES ('{}',{},'{}','{}');".format(timestamp, value, sensor, user)
        print(statement)
        print("pushed {}".format(value))
        cursor.execute(statement);

        rows = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        last_pushed = time.time()