#Push sample data with GraphQL
#Drop existing tables if any before running

#initialize db with first tenants and sensors
import random
from models import engine, db_session, Base, Tenant, Data, Sensor
Base.metadata.create_all(bind=engine)

#add first user
kate = Tenant(name='kate')
db_session.add(kate)

#add second user
kate_multitenancy = Tenant(name='kate_multitenancy')
db_session.add(kate_multitenancy)

#add sensors
t = Sensor(name='temperature')
db_session.add(t)
e = Sensor(name='electricity')
db_session.add(e)
p = Sensor(name='pressure')
db_session.add(p)

users = [kate, kate_multitenancy]
sensors = [e,p,t]
#add 100 entries
n = 100


for i in range(n):

    v = random.randrange(200)

    u = users[random.randrange(len(users))]
    s = sensors[random.randrange(len(sensors))]

    entry = Data(value = v, tenant = u, sensor = s)
    print("({}) pushed {} {} to {}".format(n, v, s, u))
    db_session.add(entry)
    db_session.commit()


db_session.commit()
