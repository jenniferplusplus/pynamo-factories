from datetime import datetime

from pytest import mark
from pynamodb.models import Model

from pynamodb_factories.factory import PynamoModelFactory
from tests.test_models.models import EmptyModel, NumberModel, BinaryModel, BooleanModel, UnicodeModel, JsonModel, \
    VersionModel, TtlModel, DateModel, NullModel, MapModel, ListModel, ComplexMap

t = int(datetime.utcnow().timestamp())


@mark.parametrize('seed', range(t, t + 20))
class TestFactories:
    def test_model(self, seed):
        class EmptyFactory(PynamoModelFactory):
            __model__ = EmptyModel
            pass

        EmptyFactory.set_random_seed(seed)
        actual = EmptyFactory.build()
        assert actual
        assert actual.serialize() is not None
        assert isinstance(actual, Model)
        assert isinstance(actual, EmptyModel)
        pass

    def test_number_attributes(self, seed):
        class NumberFactory(PynamoModelFactory):
            __model__ = NumberModel
            pass

        NumberFactory.set_random_seed(seed)
        actual = NumberFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, "num")
        assert isinstance(actual.num, int)

        assert hasattr(actual, "nums")
        for n in actual.nums if actual.nums else range(0):
            assert isinstance(n, int)
        pass

    def test_binary_attributes(self, seed):
        class BinaryFactory(PynamoModelFactory):
            __model__ = BinaryModel
            pass

        BinaryFactory.set_random_seed(seed)
        actual = BinaryFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, "bin")
        assert isinstance(actual.bin, bytes)

        assert hasattr(actual, 'bins')
        for b in actual.bins if actual.bins else range(0):
            assert isinstance(b, bytes)
        pass

    def test_boolean_attributes(self, seed):
        class BoolFactory(PynamoModelFactory):
            __model__ = BooleanModel
            pass

        BoolFactory.set_random_seed(seed)
        actual = BoolFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, "boolean")
        assert isinstance(actual.boolean, bool)
        pass

    def test_unicode_attributes(self, seed):
        class UnicodeFactory(PynamoModelFactory):
            __model__ = UnicodeModel
            pass

        UnicodeFactory.set_random_seed(seed)
        actual = UnicodeFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, "line")
        assert isinstance(actual.line, str)

        assert hasattr(actual, "lines")
        for line in actual.lines if actual.lines else range(0):
            assert isinstance(line, str)
        pass

    def test_json_attributes(self, seed):
        class JsonFactory(PynamoModelFactory):
            __model__ = JsonModel
            pass

        JsonFactory.set_random_seed(seed)
        actual = JsonFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, "json")
        assert isinstance(actual.json, dict)
        pass

    def test_version_attribute(self, seed):
        class VersionFactory(PynamoModelFactory):
            __model__ = VersionModel
            pass

        VersionFactory.set_random_seed(seed)
        actual = VersionFactory.build()
        assert actual
        assert actual.serialize()

        assert hasattr(actual, 'ver')
        assert isinstance(actual.ver, int)
        pass

    def test_ttl_attributes(self, seed):
        class TtlFactory(PynamoModelFactory):
            __model__ = TtlModel
            pass

        TtlFactory.set_random_seed(seed)
        actual = TtlFactory.build()
        assert actual
        assert actual.serialize()

        assert hasattr(actual, 'ttl')
        assert isinstance(actual.ttl, datetime)
        pass

    def test_date_attributes(self, seed):
        class DateFactory(PynamoModelFactory):
            __model__ = DateModel
            pass

        DateFactory.set_random_seed(seed)
        actual = DateFactory.build()
        assert actual
        assert actual.serialize()

        assert hasattr(actual, 'date')
        assert isinstance(actual.date, datetime)
        pass

    def test_null_attributes(self, seed):
        class NullFactory(PynamoModelFactory):
            __model__ = NullModel
            pass

        NullFactory.set_random_seed(seed)
        actual = NullFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, 'null')
        assert actual.null is None
        pass

    def test_map_attributes(self, seed):
        class MapFactory(PynamoModelFactory):
            __model__ = MapModel
            pass

        MapFactory.set_random_seed(seed)
        actual = MapFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, 'map')
        assert actual.map is not None

        assert hasattr(actual, 'dyn_map')
        assert actual.dyn_map is not None

        assert hasattr(actual, 'map_of')
        assert isinstance(actual.map_of, ComplexMap)
        pass

    def test_list_attributes(self, seed):
        class ListFactory(PynamoModelFactory):
            __model__ = ListModel
            pass

        ListFactory.set_random_seed(seed)
        actual = ListFactory.build()
        assert actual
        assert actual.serialize() is not None

        assert hasattr(actual, 'list')
        assert actual.list is not None

        assert hasattr(actual, 'list_of')
        for each in actual.list_of if actual.list_of else range(0):
            assert isinstance(each, ComplexMap)
        pass

    def test_build_args(self, seed):
        class MapFactory(PynamoModelFactory):
            __model__ = MapModel
            pass

        build_args = {
            'map_of': {
                'name': 'given name',
                'email': 'given_email@example.com',
                'birthday': datetime(1990, 1, 1, 12, 0, 0)
            }
        }

        MapFactory.set_random_seed(seed)
        actual = MapFactory.build(**build_args)
        assert actual.serialize() is not None
        assert actual.map_of.name == 'given name'
        assert actual.map_of.email == 'given_email@example.com'
        assert actual.map_of.birthday == datetime(1990, 1, 1, 12, 0, 0)

    def test_extra_build_args(self, seed):
        class MapFactory(PynamoModelFactory):
            __model__ = UnicodeModel
            pass

        build_args = {
            'dne': 'some value'
        }

        MapFactory.set_random_seed(seed)
        actual = MapFactory.build(**build_args)
        assert actual.serialize() is not None
