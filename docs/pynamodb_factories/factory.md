Module pynamodb_factories.factory
=================================

Functions
---------

    
`is_pynamo_model(model) ‑> bool`
:   

    
`random()`
:   random() -> x in the interval [0, 1).

    
`utf8_bytes(string)`
:   

Classes
-------

`PynamoModelFactory()`
:   This class is used to define a factory for the provided Pynamodb model.
    To get a factory class, inherit this class and assign the desired Pynamodb model schema class to the __model__ attr.
    
    Call build() to generate a new faked instance of the __model__ schema.
    
    Set attributes on the factory class to provide custom handling for the same-named attributes in the schema. The
    set attribute can be any value, a callable, or an instance of the Use class. Callables will be executed and the
    return value assigned to the attribute.
    
    # Usage:
    ```
    class MyFactory(PythonModelFactory):
        __model__ = MyModel
        id = 'test_id'
    
    faked_MyModel = MyFactory.build(**build_kwargs)
    ```
    
    # Attributes:
    
        __model__: The schema to generate fake models of
        __faker__: (Optional) Your own custom configured Faker instance
        __allow_nulls__: (Optional) Whether to allow None values in attributes which can accept them. Defaults to True.
        __allow_empty__: (Optional) Whether to allow collection attributes to have zero length. Defaults to True.
        __raise_unsupported: (Optional) Whether to raise an exception when an unsupported attribute is encounterd.
            Defaults to False. As of PynamoDB 5.3.x, only the DiscriminatorAttribute is unsupported. Raising can make
            this issue easier to identify. Suppressing the exception allows you to provide handling for it yourself.
            To do this, override the set_field() method in your factory class.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Static methods

    `build(**kwargs) ‑> ~T`
    :   Builds an instance of the factory's __model__
        :param kwargs: Will be trimmed to remove extraneous items and passed to the schema constructor
        :return: An instance of the __model__ schema class

    `create_factory(model: Type[~T], base_factory: Optional[Type[ForwardRef('PynamoModelFactory')]] = sys.stderr, **kwargs)`
    :   Dynamically create a PynamoModelFactory for the given Pynamo Model.
        :param model: the model to be manufactured
        :param base_factory: an existing factory to inherit from
        :param kwargs: args to be passed to the
        :return: a PynamoModelFactory. Call .build() to build a model.

    `get_faker() ‑> faker.proxy.Faker`
    :   Get the Faker instance

    `set_field(*, field_name, field: pynamodb.attributes.Attribute)`
    :   Generates a value with Faker to be assigned to the attribute
        :param field_name: The name of the attribute
        :param field: The schema attribute object itself
        :return: The value to be set on the generated model attribute

    `set_field_from_factory(field_name)`
    :   Sets a field based a custom attribute from the factory
        :param cls: The current factory class
        :param field_name: The name of the attribute
        :return: The value to be set on the generated model attribute

    `set_random_seed(seed)`
    :   Set a known random seed to make your tests reproducible

    `should_set_field_default(*, field_name, field) ‑> bool`
    :   Override to define custom criteria for when a field should be set to its default or default_for_new value
        :param field_name: The name of the attribute
        :param field: The schema attribute object itself
        :return: bool. True to allow the default value, False to set a generated value.

    `should_set_field_none(*, field_name, field) ‑> bool`
    :   Override to define custom criteria for when a field should be None
        :param field_name: The name of the attribute
        :param field: The schema attribute object itself
        :return: bool. True to set None, False to set a value.