from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model, MetaModel


class TestModel(Model):
    class Meta(MetaModel):
        table_name = "test"
        pass

    field = UnicodeAttribute()


class TestModelCreation:
    def test_model(self):
        model = TestModel(**{})

        assert model
        pass
