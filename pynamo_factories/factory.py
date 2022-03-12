from abc import ABC
from contextlib import suppress
from datetime import tzinfo, timezone
from random import random, seed as random_seed, randint
from typing import Generic, Type, Optional, TypeVar, cast, Union

from faker import Faker
from pynamodb.models import Model as PynamoModel
from pynamodb.attributes import (
    Attribute, BinaryAttribute, BinarySetAttribute, UnicodeAttribute, UnicodeSetAttribute, JSONAttribute,
    BooleanAttribute, NumberAttribute, NumberSetAttribute, VersionAttribute, TTLAttribute, UTCDateTimeAttribute,
    NullAttribute, MapAttribute, ListAttribute, DynamicMapAttribute
)

from pynamo_factories.fields import Use

T = TypeVar("T", bound=Union[PynamoModel, Attribute])
default_faker = Faker()


class ConfigurationError(Exception):
    pass


class UnsupportedException(Exception):
    pass


class PynamoModelFactory(ABC, Generic[T]):
    __model__: Type[T]
    __faker__: Optional[Faker]
    __allow_nulls__: bool = True
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
        for field_name, field_cls in cls._get_model().get_attributes():
            if cls.should_set_field_default(field_name=field_name, field_cls=field_cls):
                # Leave the field out of the dict and PynamoDB will set the default value on creation
                pass
            elif field_name not in kwargs and isinstance(field_cls, Attribute):
                build_arg = cls._build_attribute(attr_name=field_name, attr_class=field_cls)
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
        kwargs.setdefault("__allow_none_optionals__", cls.__allow_none_optionals__)

        return cast(
            PynamoModelFactory,
            type(
                f"{model.__name__}Factory",
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
    def set_field(cls, *, field_name, field_cls: Attribute):
        fake = cls.get_faker()
        if isinstance(field_cls, BinaryAttribute):
            return fake.sentence()
        if isinstance(field_cls, BinarySetAttribute):
            return fake.sentences(randint(0, 5))
        if isinstance(field_cls, BooleanAttribute):
            return fake.pybool()
        if isinstance(field_cls, UnicodeAttribute):
            return fake.sentence()
        if isinstance(field_cls, UnicodeSetAttribute):
            return fake.sentences(randint(0, 5))
        if isinstance(field_cls, JSONAttribute):
            return fake.pydict()
        if isinstance(field_cls, NumberAttribute):
            return fake.pyint()
        if isinstance(field_cls, NumberSetAttribute):
            return fake.pylist(randint(0, 5), False, value_types='int')
        if isinstance(field_cls, VersionAttribute):
            return fake.pyint(1, 5)
        if isinstance(field_cls, TTLAttribute):
            return fake.date_time_this_year(after_now=True, tzinfo=timezone.utc)
        if isinstance(field_cls, UTCDateTimeAttribute):
            return fake.date_time(tzinfo=timezone.utc)
        if isinstance(field_cls, NullAttribute):
            return None
        if isinstance(field_cls, MapAttribute) or isinstance(field_cls, DynamicMapAttribute):
            if field_cls is MapAttribute or field_cls is DynamicMapAttribute:
                # Just a raw MapAttribute
                return fake.pydict()
            else:
                return cls.create_factory(field_cls.__class__).build()
        if isinstance(field_cls, ListAttribute):
            if field_cls.element_type:
                factory = cls.create_factory(field_cls.element_type.__class__)
                values = []
                for _ in range(randint(0, 5)):
                    values.append(factory.build())
                return values
            else:
                return fake.words(randint(0, 5))

        if cls.__raise_unsupported__:
            raise UnsupportedException
        return None

    @classmethod
    def should_set_field_none(cls, *, field_name, field_cls) -> bool:
        """Override to define custom criteria for when a field should be None"""
        if not cls.__allow_nulls__:
            return False
        if field_cls.null and random() <= 0.25:
            return True
        return False

    @classmethod
    def should_set_field_default(cls, *, field_name, field_cls) -> bool:
        """Override to define custom criteria for when a field should be set to its default or default_for_new value"""
        if field_cls.default or field_cls.default_for_new:
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
            raise ConfigurationError("missing model class in factory Meta")
        model = cls.__model__
        if is_pynamo_model(model):
            with suppress(NameError):
                cast(PynamoModel, model).update_forward_refs()
        return model

    @classmethod
    def _build_attribute(cls, *, attr_name, attr_class) -> dict:
        if cls.should_set_field_none(field_name=attr_name, field_cls=attr_class):
            return {attr_name: None}
        elif hasattr(cls, attr_name):
            return {attr_name: cls.set_field_from_factory(field_name=attr_name)}
        else:
            return {attr_name: cls.set_field(field_name=attr_name, field_cls=attr_class)}
        pass


def is_pynamo_model(model) -> bool:
    return issubclass(model, PynamoModel)
