# Usage

```python
from pynamodb import Model
from pynamodb_factories import PynamoModelFactory

class SomePynamoModel(Model):
    ...
    pass

class SomeModelFactory(PynamoModelFactory):
    __model__ = SomePynamoModel
    pass

fake_model = SomeModelFactory.build()
```