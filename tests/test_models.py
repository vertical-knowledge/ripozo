__author__ = 'Tim Martin'
from cqlengine import columns, uuid1
from cqlengine.models import Model


# from cqlengine documentation
class Person(Model):
    id = columns.UUID(primary_key=True, default=uuid1)
    first_name = columns.Text(index=True)
    last_name = columns.Text(index=True)
    test_batch = columns.TimeUUID(default=uuid1, index=True)


class Comment(Model):
    id = columns.TimeUUID(primary_key=True, default=uuid1)
    owner_id = columns.UUID()
    subject = columns.Text()
    comment = columns.Text()


class Dummy(Model):
    id = columns.TimeUUID(primary_key=True, default=uuid1)
    id2_ = columns.UUID()
    text_ = columns.Text()
    boolean_ = columns.Boolean()
    int_ = columns.Integer()
    long_ = columns.BigInt()
    varint_ = columns.VarInt()
    datetime_ = columns.DateTime()
    bytes_ = columns.Bytes()
    ascii_ = columns.Ascii()
    float_ = columns.Float()
    decimal_ = columns.Decimal()
    set_ = columns.Set(columns.Text)
    list_ = columns.List(columns.Text)
    map_ = columns.Map(columns.Text, columns.Text)


class Restricted(Model):
    id = columns.UUID(primary_key=True, default=uuid1)


class CustomMethodModel(Model):
    id = columns.UUID(primary_key=True, default=lambda: uuid1())
    text = columns.Text(required=False)


class MultipleKeys(Model):
    id1 = columns.UUID(partition_key=True, default=uuid1)
    id2 = columns.UUID(partition_key=True, default=uuid1)
    id3 = columns.UUID(primary_key=True, default=uuid1)
