from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from pynamodb_factories.factory import PynamoModelFactory
from tests.test_models.models import Meta


class TestDefaultFields:
    def test_default(self):
        class DefaultModel(Model):
            Meta = Meta
            name = UnicodeAttribute(default='default value')
            pass

        class DefaultFactory(PynamoModelFactory):
            __model__ = DefaultModel
            pass

        DefaultFactory.set_random_seed(1)
        actual = DefaultFactory.build()
        assert actual.name == 'default value'
    pass
