from jsonschema import Draft7Validator, validators

def default_values_from_schema(schema):
    if schema.get('type') != 'object':
        return schema["default"]
    
    obj = {}
    for sub_dir in schema['properties']:
        obj[sub_dir] = default_values_from_schema(schema['properties'][sub_dir])
    return obj

# Implementation from jsonschema documentaion. it requires to have "default":{} 
# at the object, so I didn't use it
def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )

DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)



def default_values_from_schema_using_validator(schema):
    obj = {}
    DefaultValidatingDraft7Validator(schema).validate(obj)
    return obj