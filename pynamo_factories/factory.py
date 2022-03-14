from abc import ABC
from datetime import timezone
from random import random, seed as random_seed, randint
from typing import Generic, Type, Optional, TypeVar, cast, Union

from faker import Faker
from pynamodb.models import Model as PynamoModel
from pynamodb.attributes import (
    Attribute, BinaryAttribute, BinarySetAttribute, UnicodeAttribute, UnicodeSetAttribute, JSONAttribute,
    BooleanAttribute, NumberAttribute, NumberSetAttribute, VersionAttribute, TTLAttribute, UTCDateTimeAttribute,
    NullAttribute, MapAttribute, ListAttribute, DynamicMapAttribute
)

from pynamo_factories.exceptions import UnsupportedException, ConfigurationError
from pynamo_factories.fields import Use

T = TypeVar("T", bound=Union[PynamoModel, Attribute])
default_faker = Faker()


class PynamoModelFactory(ABC, Generic[T]):
    __model__: Type[T]
    __faker__: Optional[Faker]
    __allow_nulls__: bool = True
    __allow_empty__: bool = True
    __raise_unsupported__: bool = False

    @classmethod
    def set_random_seed(cls, seed):
        """Set a known random seed to make your tests reproducible"""
        Faker.seed(seed)
        random_seed(seed)

    @classmethod
    def build(cls, **kwargs) -> T:
        """
        builds an instance of the factory's __model__
        """
        for field_name, field in cls._get_model().get_attributes().items():
            if cls.should_set_field_default(field_name=field_name, field=field):
                # Leave the field out of the dict and PynamoDB will set the default value on creation
                pass
            elif field_name not in kwargs and isinstance(field, Attribute):
                build_arg = cls._build_field(field_name=field_name, field=field)
                kwargs.update(build_arg)
        return cast(T, cls.__model__(**kwargs))

    @classmethod
    def create_factory(cls, model: Type[T], base_factory: Optional[Type["PynamoModelFactory"]] = None, **kwargs):
        """
        Dynamically create a PynamoModelFactory for the given Pynamo Model
        :param model: the model to be manufactured
        :param base_factory: an existing factory to inherit from
        :param kwargs: args to be passed to the
        :return: a PynamoModelFactory. Call .build() to build a model.
        """
        kwargs.setdefault("__faker__", cls.get_faker())
        kwargs.setdefault("__allow_nulls__", cls.__allow_nulls__)
        kwargs.setdefault("__allow_empty__", cls.__allow_empty__)
        kwargs.setdefault("__raise_unsupported__", cls.__raise_unsupported__)

        name = model.__name__
        return cast(
            PynamoModelFactory,
            type(
                f"{name}Factory",
                (base_factory or cls,),
                {"__model__": model, **kwargs},
            ),
        )
        pass

    @classmethod
    def set_field_from_factory(cls, field_name):
        field = getattr(cls, field_name)
        if isinstance(field, Use):
            return field.to_value()
        if callable(field):
            return field()
        return field

    @classmethod
    def set_field(cls, *, field_name, field: Attribute):
        fake = cls.get_faker()
        if isinstance(field, BinaryAttribute):
            return bytes(fake.sentence(), 'utf-8')
        if isinstance(field, BinarySetAttribute):
            return map(utf8_bytes, fake.sentences(randint(0, 5)))
        if isinstance(field, BooleanAttribute):
            return fake.pybool()
        if isinstance(field, UnicodeAttribute):
            return fake.sentence()
        if isinstance(field, UnicodeSetAttribute):
            return fake.sentences(randint(cls._min_range(), 5))
        if isinstance(field, JSONAttribute):
            return fake.pydict(
                allowed_types=['str', 'int', 'float', 'email', 'address', 'job', 'phone_number', 'name', 'iso8601'])
        if isinstance(field, VersionAttribute):
            return fake.pyint(1, 5)
        if isinstance(field, NumberAttribute):
            return fake.pyint()
        if isinstance(field, NumberSetAttribute):
            return fake.pylist(randint(cls._min_range(), 5), False, value_types='int')
        if isinstance(field, TTLAttribute):
            return fake.date_time_this_year(after_now=True, tzinfo=timezone.utc)
        if isinstance(field, UTCDateTimeAttribute):
            return fake.date_time(tzinfo=timezone.utc)
        if isinstance(field, NullAttribute):
            return None
        if isinstance(field, MapAttribute) or isinstance(field, DynamicMapAttribute):
            if field is MapAttribute or field is DynamicMapAttribute:
                # Just a raw MapAttribute
                return fake.pydict()
            else:
                return cls.create_factory(field.__class__).build()
        if isinstance(field, ListAttribute):
            if field.element_type:
                factory = cls.create_factory(field.element_type)
                values = []
                for _ in range(randint(cls._min_range(), 5)):
                    values.append(factory.build())
                return values
            else:
                return fake.words(randint(0, 5))

        if cls.__raise_unsupported__:
            raise UnsupportedException(f'Field {field_name}: {type(field)} is not supported')
        return None

    @classmethod
    def should_set_field_none(cls, *, field_name, field) -> bool:
        """Override to define custom criteria for when a field should be None"""
        if not cls.__allow_nulls__:
            return False
        if type(field) in (VersionAttribute,):
            # Some attributes are not None-able
            return False
        if field.null and random() <= 0.25:
            return True
        return False

    @classmethod
    def should_set_field_default(cls, *, field_name, field) -> bool:
        """Override to define custom criteria for when a field should be set to its default or default_for_new value"""
        if field.default or field.default_for_new:
            return random() <= 0.25
        return False

    @classmethod
    def get_faker(cls) -> Faker:
        if hasattr(cls, "__faker__") and cls.__faker__:
            return cls.__faker__
        return default_faker

    @classmethod
    def _get_model(cls) -> Type[T]:
        if not hasattr(cls, "__model__") or not cls.__model__:
            raise ConfigurationError(f"missing model class in factory {cls.__name__}")
        return cls.__model__

    @classmethod
    def _build_field(cls, *, field_name, field) -> dict:
        if cls.should_set_field_none(field_name=field_name, field=field):
            return {field_name: None}
        elif hasattr(cls, field_name):
            return {field_name: cls.set_field_from_factory(field_name=field_name)}
        else:
            return {field_name: cls.set_field(field_name=field_name, field=field)}
        pass

    @classmethod
    def _min_range(cls):
        return 0 if cls.__allow_empty__ else 1


def utf8_bytes(string):
    return bytes(string, 'utf-8')


def is_pynamo_model(model) -> bool:
    return issubclass(model, PynamoModel)
