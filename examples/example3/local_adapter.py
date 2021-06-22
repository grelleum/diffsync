import json

from slugify import slugify

from diffsync import DiffSync
from models import Region, Country

COUNTRIES_FILE = "countries.json"


class LocalAdapter(DiffSync):
    """DiffSync Adapter to Load the list of regions and countries from a local JSON file."""

    # Define all data models that this adapter makes use of.
    # Note that the variable names ("region", "country") need to match between DiffSync Adapter classes.
    region = Region
    country = Country

    # When doing a diff or a sync between 2 adapters,
    #  DiffSync will recursively check all models defined at the top level and their children.
    # Since our data model defines countries as children of a region, we don't need to list country here
    top_level = ["region"]

    # Human readable name of the Adapter,
    # mainly used when doing a diff to indicate where each data is coming from
    type = "Local"

    def load(self, filename=COUNTRIES_FILE):
        """Load all regions and countries from a local JSON file."""

        data_file = open(filename, "r")
        countries = json.loads(data_file.read())

        # Load all regions first
        # A Region object will be created for each region and it will be stored inside the adapter with self.add()
        # To create a Region we are using "self.region" instead of "Region" directly to allow someone to extend this adapter without redefining everything.
        region_names = set([country.get("region") for country in countries])
        for region in region_names:
            self.add(self.region(slug=slugify(region), name=region))

        # Load all countries
        # A Country object will be create for each country, it will be store inside the object with self.add
        # and it will be linked to its parent with parent.add_child(item)
        for country in countries:

            # Retrive the parent region object from the internal cache.
            region = self.get(obj=self.region, identifier=slugify(country.get("region")))

            name = country.get("country")
            item = self.country(
                slug=slugify(name), name=name, subregion=country.get("subregion", None), region=region.slug
            )
            self.add(item)

            region.add_child(item)

        data_file.close()
