"""Validate only the JSON Schema keywords used by this specimen; no dependencies."""
import re

KEYWORDS = {'$schema', 'title', 'description', 'type', 'properties', 'required',
            'additionalProperties', 'items', 'enum', 'const', 'minimum',
            'minItems', 'minLength', 'pattern'}

def validate(value, schema, path='$'):
    unknown = set(schema) - KEYWORDS
    if unknown:
        raise ValueError(f'Unsupported schema keywords: {unknown}')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'number': (int, float), 'boolean': bool, 'null': type(None)}
    if 'type' in schema:
        kind = schema['type']
        ok = isinstance(value, types[kind])
        if kind in ('integer', 'number') and isinstance(value, bool): ok = False
        if not ok: raise ValueError(f'{path}: expected {kind}')
    if 'enum' in schema and value not in schema['enum']: raise ValueError(f'{path}: enum')
    if 'const' in schema and value != schema['const']: raise ValueError(f'{path}: const')
    if 'minimum' in schema and value < schema['minimum']: raise ValueError(f'{path}: minimum')
    if 'minLength' in schema and len(value) < schema['minLength']: raise ValueError(f'{path}: minLength')
    if 'pattern' in schema and re.search(schema['pattern'], value) is None: raise ValueError(f'{path}: pattern')
    if isinstance(value, dict):
        if set(schema.get('required', [])) - set(value): raise ValueError(f'{path}: missing keys')
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False and set(value) - set(props):
            raise ValueError(f'{path}: extra keys')
        for k, v in value.items():
            if k in props: validate(v, props[k], path + '.' + k)
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0): raise ValueError(f'{path}: minItems')
        for i, item in enumerate(value):
            if 'items' in schema: validate(item, schema['items'], f'{path}[{i}]')

