# flask_sqlalchemy/schema.py
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Tenant as TenantModel, Sensor as SensorModel, Data as DataModel


class Tenant(SQLAlchemyObjectType):
    class Meta:
        model = TenantModel
        interfaces = (relay.Node, )
        


class TenantConnection(relay.Connection):
    class Meta:
        node = Tenant


class Sensor(SQLAlchemyObjectType):
    class Meta:
        model = SensorModel
        interfaces = (relay.Node, )


class SensorConnection(relay.Connection):
    class Meta:
        node = Sensor


class Data(SQLAlchemyObjectType):
    class Meta:
        model = DataModel
        interfaces = (relay.Node, )


class DataConnections(relay.Connection):
    class Meta:
        node = Data


class Query(graphene.ObjectType):
    nodes = relay.Node.Field()

    all_tenants = SQLAlchemyConnectionField(TenantConnection, sort=None)
  
  # Allows sorting over multiple columns, by default over the primary key
    all_data = SQLAlchemyConnectionField(DataConnections)
    # Disable sorting over this field
    all_sensors = SQLAlchemyConnectionField(SensorConnection, sort=None)

    tenant = graphene.Field(Tenant, id = graphene.Argument(type=graphene.Int, required=False))

    def resolve_tenant(self, info, id):
        #return name
        # name = args.get("name")
        query = Tenant.get_query(info)
        output = query.filter(Tenant.id == id).first()
        return output

schema = graphene.Schema(query=Query)

query = '{\
  allData {\
    edges {\
      node {\
        id\
        time\
        value\
        }\
      }\
    }\
  }'

result = schema.execute(query)
print(result.data['allData']['edges'][0]['node']['value'])