import peewee

from brainio_collection.lookup import pwdb
from brainio_collection.stimuli import StimulusSetModel


class AssemblyModel(peewee.Model):
    """An AssemblyModel stores information about the canonical location where the data
    for a DataAssembly is stored.  """
    name = peewee.CharField()
    assembly_class = peewee.CharField()
    stimulus_set = peewee.ForeignKeyField(StimulusSetModel, backref="assembly_models")

    class Meta:
        database = pwdb


class AssemblyStoreModel(peewee.Model):
    """An AssemblyStoreModel stores the location of a DataAssembly data file.  """
    assembly_type = peewee.CharField()
    location_type = peewee.CharField()
    location = peewee.CharField()
    unique_name = peewee.CharField(unique=True, null=True, index=True)
    sha1 = peewee.CharField(unique=True, null=True, index=True)

    class Meta:
        database = pwdb


class AssemblyStoreMap(peewee.Model):
    """An AssemblyStoreMap links an AssemblyRecord to an AssemblyStore.  """
    assembly_model = peewee.ForeignKeyField(AssemblyModel, backref="assembly_store_maps")
    assembly_store_model = peewee.ForeignKeyField(AssemblyStoreModel, backref="assembly_store_maps")
    role = peewee.CharField()

    class Meta:
        database = pwdb


class AssemblyLookupError(Exception):
    pass


def lookup_assembly(name):
    pwdb.connect(reuse_if_open=True)
    try:
        assy = AssemblyModel.get(AssemblyModel.name == name)
    except AssemblyModel.DoesNotExist as e:
        raise AssemblyLookupError("A DataAssembly named " + name + " was not found.")
    return assy
