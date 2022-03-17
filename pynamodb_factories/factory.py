from abc import ABC
from datetime import timezone
from random import random, seed as random_seed, randint
from typing import Generic, Type, Optional, TypeVar, cast, Union, Any

from faker import Faker
from pynamodb.models import Model as PynamoModel
from pynamodb.attributes import (
    Attribute, BinaryAttribute, BinarySetAttribute, UnicodeAttribute, UnicodeSetAttribute, JSONAttribute,
    BooleanAttribute, NumberAttribute, NumberSetAttribute, VersionAttribute, TTLAttribute, UTCDateTimeAttribute,
    NullAttribute, MapAttribute, ListAttribute
)

try:
    from pynamodb.attributes import DynamicMapAttribute
except ImportError:
    DynamicMapAttribute = None
    pass

from pynamodb_factories.exceptions import UnsupportedException, ModelError, RequiredArgumentError
from pynamodb_factories.fields import Use, Required, Ignored

T = TypeVar("T", bound=Union[PynamoModel, Attribute])
default_faker = Faker()


class PynamoModelFactory(ABC, Generic[T]):
    """
    This class is used to define a factory for the provided Pynamodb model.
    To get a factory class, inherit this class and assign the desired Pynamodb model schema class to the __model__ attr.

    Call build() to generate a new faked instance of the __model__ schema.

    Set attributes on the factory class to provide custom handling for the same-named attributes in the schema. The
    set attribute can be any value, a callable, or an instance of the Use class. Callables will be executed and the
    return value assigned to the attribute.

    ## Usage
    ```
    class MyFactory(PythonModelFactory):
        __model__ = MyModel
        id = 'test_id'

    faked_MyModel = MyFactory.build(**build_kwargs)
    ```

    Attributes:
        __model__: The schema to generate fake models of
        __faker__: (Optional) Your own custom configured Faker instance
        __allow_nulls__: (Optional) Whether to allow None values in attributes which can accept them. Defaults to True.
        __allow_empty__: (Optional) Whether to allow collection attributes to have zero length. Defaults to True.
        __raise_unsupported: (Optional) Whether to raise an exception when an unsupported attribute is encounterd.
            Defaults to False. As of PynamoDB 5.3.x, only the DiscriminatorAttribute is unsupported. Raising can make
            this issue easier to identify. Suppressing the exception allows you to provide handling for it yourself.
            To do this, override the set_field() method in your factory class.

    """

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
        Builds an instance of the factory's __model__

        Args:
            kwargs: Will be trimmed to remove extraneous items and passed to the schema constructor

        Returns:
            An instance of the __model__ schema class
        """
        keys = []
        for field_name, field in cls._get_model().get_attributes().items():
            keys.append(field_name)
            if cls.should_set_field_default(field_name=field_name, field=field):
                # Leave the field out of the dict and PynamoDB will set the default value on creation
                pass
            elif isinstance(field, Attribute):
                build_arg, required = cls._build_field(field_name=field_name, field=field, build_arg=kwargs.get(field_name))
                if required and field_name not in kwargs:
                    raise RequiredArgumentError(f"Required argument {field_name} was not in the build kwargs")
                kwargs.update(build_arg)
        build_args = dict(filter(lambda item: item[0] in keys, kwargs.items()))
        return cast(T, cls.__model__(**build_args))

    @classmethod
    def create_factory(cls, model: Type[T], base_factory: Optional[Type["PynamoModelFactory"]] = None, **kwargs):
        """
        Dynamically create a PynamoModelFactory for the given Pynamo Model.

        Args:
            model: the model to be manufactured
            base_factory: an existing factory to inherit from
            kwargs: args to be passed to the
        Returns:
            A PynamoModelFactory object. Call .build() to build a model.
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
        """
        Sets a field based a custom attribute from the factory

        Args:
            cls: The current factory class
            field_name: The name of the attribute
        Returns:
            The value to be set on the generated model attribute
        """
        field = getattr(cls, field_name)
        if isinstance(field, Use):
            return field.to_value()
        if callable(field):
            return field()
        return field

    @classmethod
    def set_field(cls, *, field_name, field: Attribute, build_arg: Any):
        """
        Generates a value with Faker to be assigned to the attribute

        Args:
            field_name: The name of the attribute
            field: The schema attribute object itself
        Returns:
            The value to be set on the generated model attribute
        """
        fake = cls.get_faker()
        if isinstance(field, BinaryAttribute):
            return build_arg if build_arg is not None else bytes(fake.sentence(), 'utf-8')
        if isinstance(field, BinarySetAttribute):
            return build_arg if build_arg is not None else map(_utf8_bytes, fake.sentences(randint(0, 5)))
        if isinstance(field, BooleanAttribute):
            return build_arg if build_arg is not None else fake.pybool()
        if isinstance(field, UnicodeAttribute):
            return build_arg if build_arg is not None else fake.sentence()
        if isinstance(field, UnicodeSetAttribute):
            return build_arg if build_arg is not None else fake.sentences(randint(cls._min_range(), 5))
        if isinstance(field, JSONAttribute):
            return build_arg if build_arg is not None else fake.pydict(
                allowed_types=['str', 'int', 'float', 'email', 'address', 'job', 'phone_number', 'name', 'iso8601'])
        if isinstance(field, VersionAttribute):
            return build_arg if build_arg is not None else fake.pyint(1, 5)
        if isinstance(field, NumberAttribute):
            return build_arg if build_arg is not None else fake.pyint()
        if isinstance(field, NumberSetAttribute):
            return build_arg if build_arg is not None else fake.pylist(randint(cls._min_range(), 5), False, value_types='int')
        if isinstance(field, TTLAttribute):
            return build_arg if build_arg is not None else fake.date_time_this_year(after_now=True, tzinfo=timezone.utc)
        if isinstance(field, UTCDateTimeAttribute):
            return build_arg if build_arg is not None else fake.date_time(tzinfo=timezone.utc)
        if isinstance(field, NullAttribute):
            return None
        if isinstance(field, MapAttribute) or (DynamicMapAttribute and isinstance(field, DynamicMapAttribute)):
            if field is MapAttribute or field is DynamicMapAttribute:
                # Just a raw MapAttribute
                return build_arg if build_arg is not None else fake.pydict()
            else:
                build_arg = build_arg if build_arg is not None else {}
                return cls.create_factory(field.__class__).build(**build_arg)
        if isinstance(field, ListAttribute):
            if field.element_type:
                factory = cls.create_factory(field.element_type)
                values = []
                if build_arg is not None:
                    for arg in build_arg:
                        values.append(factory.build(**arg))
                else:
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
        """
        Override to define custom criteria for when a field should be None
        Args:
            field_name: The name of the attribute
            field: The schema attribute object itself
        Returns:
            bool. True to set None, False to set a value.
        """
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
        """
        Override to define custom criteria for when a field should be set to its default or default_for_new value
        Args:
            field_name: The name of the attribute
            field: The schema attribute object itself
        Returns:
            bool. True to allow the default value, False to set a generated value.
        """
        if field.default or field.default_for_new:
            return random() <= 0.25
        return False

    @classmethod
    def get_faker(cls) -> Faker:
        """Get the Faker instance"""
        if hasattr(cls, "__faker__") and cls.__faker__:
            return cls.__faker__
        return default_faker

    @classmethod
    def _get_model(cls) -> Type[T]:
        if not hasattr(cls, "__model__") or not cls.__model__:
            raise ModelError(f"missing model class in factory {cls.__name__}")
        return cls.__model__

    @classmethod
    def _build_field(cls, *, field_name, field, build_arg) -> (dict, bool):
        set_none = cls.should_set_field_none(field_name=field_name, field=field)
        none_result = {field_name: None}
        if hasattr(cls, field_name):
            if isinstance(getattr(cls, field_name), Required):
                return {}, True
            if isinstance(getattr(cls, field_name), Ignored):
                return {}, False
            return none_result if set_none else {field_name: cls.set_field_from_factory(field_name=field_name)}, False
        else:
            return none_result if set_none else {field_name: cls.set_field(field_name=field_name, field=field, build_arg=build_arg)}, False
        pass

    @classmethod
    def _min_range(cls):
        return 0 if cls.__allow_empty__ else 1


def _utf8_bytes(string):
    return bytes(string, 'utf-8')
