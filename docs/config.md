# mutacc configuration

## vcf parsing

In general, mutacc should allow any amount of meta data to be inserted to the database.
To extract the relevant meta data from the INFO column in the passed vcf, the user
must specify what keys should be added to the variant document. This can be specified in
the config file passed with the `--config-file` option, adding a key 'vcf_parser' in the yaml file.
Alternatively, this information can be passed on in a separate yaml file, using the `--vcf-parser` option.

### import

To specify what information should be extracted from the INFO column upon importing to the database,
each relevant key should be given as an element in an list. Below is an example of how
to extract a single valued field from INFO

```yaml
import:
  - id: <ID> # the ID of the field in the vcf
    multivalue: <true|false> # Specify if the field contains multiple values
    out_type: int # What datatype the value should be casted to
    out_name: <name> # This will be the name for the value in the variant document in the database
    ...
```

If there are multiple values under one key in INFO, the key `multivalue` needs to
be set to **true**, and the user must specify how the values are separated in the vcf
by adding a `separator`, e.g. `separator: ','`.

In case each data value in a multivalued key is given in a specific format, e.g.
`...,value_1|value_2|value_3,...`. The user can specify the format under the `format` key
, e.g. `format: 'value_1|value_2|value_3'` and specify how the data values are separated with
the `format_separator` key, e.g. `format_separator: '1'`. Furthermore, the user can specify what data
values should be extracted by using the `target` key
```yaml
...
target:
  - value_1
  _ value_2
...
```
would only extract the first and third data value. Optionally if `target: all`,
all values would be extracted. to convert the INFO entry `ANN=a|b|c,d|e|f,g|h|i` in a vcf
One could specify this in the yaml with

```yaml
import:
  - id: ANN
    multivalue: true
    separator: ','
    format_separator: '|'
    format: 'value_1|value_2|value_3'
    target: all
    out_type: list
    out_name: annotation
```  

This would give a `annotation` field in the mongodb variant document

```json
  "annotation": [
    {"value_1": "a", "value_2": "b", "value_3": "c"},
    {"value_1": "d", "value_2": "e", "value_3": "f"},
    {"value_1": "g", "value_2": "h", "value_3": "i"}
  ]
```

### export

When exporting with mutacc, a vcf of all queried variants will be created. Just as
when importing from a vcf, what meta data that should get included in the exported vcf.
This is done using the same principle. however, here the user need to add the `vcf_type` and
`description`. These will be used in constructing the vcf header. e.g.
```yaml
export:
  - id: value_id # The key name in the variant, or case mongodb document
    vcf_type: Integer # Data type the value should have in vcf, e.g. 'Integer'
    out_name: VCF_ID # This will be the ID name in the vcf
    description: "This is a description for vcf_id" # Description to that ID to be added in vcf header
```

would add a INFO entry `VCF_ID=<value>`. Here both the variant document, and the
related case document will be searched for the key 'value_id', and added to the INFO
column if found in any of the documents.

If for example we have a variant document as below

```json
  "chrom": "1"
  "start": 12345
  ...
  "case": "case_id"
  ...
```

and the corresponding case document
```json
  "case_id": "case_id"
  "genes": [
    {"hgnc_id": "ID1", "gene_name": "GENE1"},
    {"hgnc_id": "ID2", "gene_name": "GENE2"}
  ]
```

This can be exported into the vcf file with the yaml entry

```yaml
export:
  - id: genes
    vcf_type: String
    out_name: ANN
    description: "Gene annotation, format: hgnc_id|gene_name"
    target: all
    format_separator: "|"
```

This will give a INFO entry as the one below
```
ANN=ID1|GENE1,ID2|GENE2
```

And a header
```
##INFO=<ID=ANN,Number=.,Type=String,Description="Gene annotation, format: hgnc_id|gene_name">
```

In this way, it is up to the user what meta data is imported and exported in the vcf.
an example yaml file is found in ```mutacc/resources/vcf-info-def.yaml``` [here](../mutacc/resources/vcf-info-def.yaml). If nothing
is given in the configuration file or with the ```--vcf-parse``` option, this will also
be the default parser used.
