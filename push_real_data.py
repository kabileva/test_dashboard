import MySQLdb
import random
import time
import datetime
last_pushed = time.time()
interval = 1 #seconds
while True:
    if (last_pushed + interval) < time.time():
        conn = MySQLdb.connect(host="localhost", user="root", passwd="Katerina27", db="sample_data")
        cursor = conn.cursor()

        value = random.randrange(200)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        users = ['kate', 'kate_multitenancy']
        user = users[random.randrange(2)]
        statement = "INSERT INTO real_data (tenant_id,gid,value,sid,time) VALUES ('{}','{}',{},'{}','{}');".format(user, 'gateway001002',value, 'temperature-gateway0010', timestamp)
        print(statement)
        print("pushed {}".format(value))
        cursor.execute(statement);

        rows = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        last_pushed = time.time()