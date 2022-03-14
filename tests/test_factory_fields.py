from datetime import datetime

from pynamo_factories.factory import PynamoModelFactory
from pynamo_factories.fields import Use
from tests.test_models.models import MapModel


class TestFactoryFields():
    def test_value(self):
        class ValueFactory(PynamoModelFactory):
            __model__ = MapModel
            map_of = {
                'name': 'given name',
                'email': 'given_email@example.com',
                'birthday': datetime(1990, 1, 1, 12, 0, 0)
            }
            pass

        actual = ValueFactory.build()
        assert actual.map_of.name == 'given name'
        assert actual.map_of.email == 'given_email@example.com'
        assert actual.map_of.birthday == datetime(1990, 1, 1, 12, 0, 0)

    def test_callable(self):
        class ValueFactory(PynamoModelFactory):
            __model__ = MapModel
            map_of = lambda: {
                'name': 'given name',
                'email': 'given_email@example.com',
                'birthday': datetime(1990, 1, 1, 12, 0, 0)
            }
            pass

        actual = ValueFactory.build()
        assert actual.map_of.name == 'given name'
        assert actual.map_of.email == 'given_email@example.com'
        assert actual.map_of.birthday == datetime(1990, 1, 1, 12, 0, 0)

    def test_use(self):
        class ValueFactory(PynamoModelFactory):
            __model__ = MapModel
            map_of = Use(lambda now: {
                'name': 'given name',
                'email': 'given_email@example.com',
                'birthday': now
            }, datetime(1990, 1, 1, 12, 0, 0))
            pass

        actual = ValueFactory.build()
        assert actual.map_of.name == 'given name'
        assert actual.map_of.email == 'given_email@example.com'
        assert actual.map_of.birthday == datetime(1990, 1, 1, 12, 0, 0)
    pass
