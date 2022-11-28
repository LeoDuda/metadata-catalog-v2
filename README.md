# Metadata Standards Catalog code base

This repository contains the code base for the Research Data Alliance [Metadata
Standards Catalog], version 2. The version 1 code is kept in a [separate repository].

For information on how to install and run an instance of the Catalog yourself,
see the [Installation Guide].

For information on how to contribute to the development of the Catalog,
see the [Guide for Contributors].

The data model used by the API is documented in OpenAPI format. It is stored
locally as [openapi.yaml] and may be explored interactively on [SwaggerHub].

[Metadata Standards Catalog]: https://rdamsc.bath.ac.uk/
[separate repository]: https://github.com/rd-alliance/metadata-catalog-dev
[Installation Guide]: INSTALLATION.md
[Guide for Contributors]: CONTRIBUTING.md
[openapi.yaml]: openapi.yaml
[SwaggerHub]: https://app.swaggerhub.com/apis-docs/alex-ball/rda-metadata-standards-catalog/2.0.0

# Changes for the KIT-Version

### Database
The database used in https://msc.datamanager.kit.edu/ was not compatible with the second version of the catalog from scratch. To make it compatible the provided tool from https://github.com/rd-alliance/metadata-catalog-data was used.

The HMC subjects were added manually as keywords to each schema which uses them. They now can be found in metadata-catalog-v2/instance/data/db.json

To make the HMC subjects searchable they also had to be added to the thesaurus vocabulary. This was done by adding them manually as new terms in metadata-catalog-v2/instance/data/vocab.json

### Architecture
The architecture of the second version of the Metadata Standards Catalog is build completly different to the first version. Instead of one big file which contains all the functions, the main functions were distributed into single files. These files were edited to match the look and the functionality of the KIT version of the Metadata Standards Catalog. With this comes a new file named metastore.py for the added functionality of the metastore.
