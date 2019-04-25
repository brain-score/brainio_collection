import peewee

from brainio_collection.lookup import pwdb


class AttributeModel(peewee.Model):
    name = peewee.CharField(unique=True)
    type = peewee.CharField()

    class Meta:
        database = pwdb


class ImageModel(peewee.Model):
    image_id = peewee.CharField(unique=True)

    class Meta:
        database = pwdb


class ImageMetaModel(peewee.Model):
    image = peewee.ForeignKeyField(ImageModel, backref="image_meta_models")
    attribute = peewee.ForeignKeyField(AttributeModel, backref="image_meta_models")
    value = peewee.CharField()

    class Meta:
        database = pwdb


class StimulusSetModel(peewee.Model):
    name = peewee.CharField()

    class Meta:
        database = pwdb


class ImageStoreModel(peewee.Model):
    store_type = peewee.CharField()
    location = peewee.CharField()
    location_type = peewee.CharField()
    unique_name = peewee.CharField(unique=True, null=True, index=True)
    sha1 = peewee.CharField(unique=True, null=True, index=True)

    class Meta:
        database = pwdb


class StimulusSetImageMap(peewee.Model):
    stimulus_set = peewee.ForeignKeyField(StimulusSetModel, backref="stimulus_set_image_maps")
    image = peewee.ForeignKeyField(ImageModel, backref="stimulus_set_image_maps")

    class Meta:
        database = pwdb


class ImageStoreMap(peewee.Model):
    image_store = peewee.ForeignKeyField(ImageStoreModel, backref="image_image_store_maps")
    image = peewee.ForeignKeyField(ImageModel, backref="image_image_store_maps")
    path = peewee.CharField()

    class Meta:
        database = pwdb


def list_stimulus_sets():
    return [ssm.name for ssm in StimulusSetModel.select()]

