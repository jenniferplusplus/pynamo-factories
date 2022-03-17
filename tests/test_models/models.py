from pynamodb.attributes import NumberAttribute, NumberSetAttribute, BinaryAttribute, BinarySetAttribute, \
    BooleanAttribute, UnicodeAttribute, UnicodeSetAttribute, JSONAttribute, VersionAttribute, TTLAttribute, \
    UTCDateTimeAttribute, NullAttribute, MapAttribute, ListAttribute, DynamicMapAttribute
from pynamodb.models import Model, MetaModel


class Meta(MetaModel):
    table_name = "test"
    pass


class ComplexMap(MapAttribute):
    name = UnicodeAttribute()
    email = UnicodeAttribute()
    birthday = UTCDateTimeAttribute()


class MapListMap(MapAttribute):
    arr = ListAttribute(of=ComplexMap)


class EmptyModel(Model):
    Meta = Meta
    pass


class NumberModel(EmptyModel):
    num = NumberAttribute()
    nums = NumberSetAttribute()
    pass


class BinaryModel(EmptyModel):
    bin = BinaryAttribute()
    bins = BinarySetAttribute()
    pass


class BooleanModel(EmptyModel):
    boolean = BooleanAttribute()
    pass


class UnicodeModel(EmptyModel):
    line = UnicodeAttribute()
    lines = UnicodeSetAttribute()
    pass


class JsonModel(EmptyModel):
    json = JSONAttribute()
    pass


class VersionModel(EmptyModel):
    ver = VersionAttribute()
    pass


class TtlModel(EmptyModel):
    ttl = TTLAttribute()
    pass


class DateModel(EmptyModel):
    date = UTCDateTimeAttribute()
    pass


class NullModel(EmptyModel):
    # This is absurd, but PynamoDB requires the null param to be True for NullAttribute
    # Omitting it is not a valid model
    null = NullAttribute(null=True)
    pass


class MapModel(EmptyModel):
    map = MapAttribute()
    dyn_map = DynamicMapAttribute()
    map_of = ComplexMap()
    pass


class ListModel(EmptyModel):
    list = ListAttribute()
    list_of = ListAttribute(of=ComplexMap)


class MapListMapModel(EmptyModel):
    map = MapListMap()
    val = NumberAttribute(default=1001)
