Module pynamodb_factories.exceptions
====================================

Classes
-------

`ModelError(*args, **kwargs)`
:   The given class is not a valid Pynamodb model and cannot be used to generate fakes

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`RequiredArgumentError(*args, **kwargs)`
:   A required arguments was not included in the build kwargs

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`UnsupportedException(*args, **kwargs)`
:   The attribute is not supported by pynamodb-factories, and cannot be faked

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException