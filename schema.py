# flask_sqlalchemy/schema.py
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Tenant as TenantModel, Sensor as SensorModel, Data as DataModel


class Tenant(SQLAlchemyObjectType):
    class Meta:
        model = TenantModel
        #interfaces = (relay.Node, )
        

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

    #Fields for resolving; resolving function should be resolve_field_name
    #Query: tenantId (tenantId: 1) {...}
    tenant_id = graphene.List(Tenant, tenant_id = graphene.Argument(type=graphene.Int, required=False))
    #Query: tenantName (tenantName: 1) {...}
    tenant_name = graphene.List(Tenant, tenant_name = graphene.Argument(type=graphene.String, required=False))
    #Query: DataByTenantName (tenantName: 1) {...}
    data_by_tenant_name =  graphene.List( Data, tenant_name = graphene.Argument(type=graphene.String, required=False))
    
    all_tenants = SQLAlchemyConnectionField(TenantConnection, sort=None)
    #Allows sorting over multiple columns, by default over the primary key
    all_data = SQLAlchemyConnectionField(DataConnections)
    # Disable sorting over this field
    all_sensors = SQLAlchemyConnectionField(SensorConnection, sort=None)
    #Query Tenant by name
    def resolve_tenant_name(self, info, tenant_name):
        query = Tenant.get_query(info = info)
        query = query.filter(TenantModel.name == tenant_name)
        objs = query.all()
        return objs
    #Query Tenant by id
    def resolve_tenant_id(self, info, tenant_id):
        query = Tenant.get_query(info = info)
        query = query.filter(TenantModel.id == tenant_id)
        objs = query.all()
        return objs

    #Query Data by Tenant.name 
    def resolve_data_by_tenant_name(self, info, tenant_name):
        query = Data.get_query(info = info)
        #join TenantModel to include the argument for tenant
        query = query.join(DataModel.tenant)
        query = query.filter(TenantModel.name == tenant_name)
        objs = query.all()
        return objs

schema = graphene.Schema(query=Query)
