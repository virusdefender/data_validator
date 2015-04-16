# coding=utf-8
from fields import Field, IntegerField, CharField, EmailField, URLField
from validator_exceptions import ValidationError


class ValidatorMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'Validator':
            return type.__new__(mcs, name, bases, attrs)

        mappings = dict()

        for k, v in attrs.iteritems():
            if isinstance(v, Field):
                mappings[k] = v

        for k in mappings.iterkeys():
            attrs.pop(k)

        attrs['mappings'] = mappings

        return type.__new__(mcs, name, bases, attrs)


class Validator(dict):
    __metaclass__ = ValidatorMetaClass

    def __init__(self, data, **kwargs):
        super(Validator, self).__init__(**kwargs)
        self._origin_data = data
        self._validated_data = dict()
        self._validated = False
        self.errors = []

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def _get(self, field_name):
        try:
            return self._origin_data[field_name]
        except KeyError:
            return None

    def is_validate(self, **kwargs):
        for field_name, field_instance in self.mappings.iteritems():
            try:
                self._validated_data[field_name] = field_instance.validate(self._get(field_name), **kwargs)
            except ValidationError, e:
                show_name = field_instance.show_name
                if not show_name:
                    show_name = field_name
                self.errors.append({"show_name": show_name, "message": e.message, "field_name": field_name})

        if not self.errors:
            self._validated = True
            return True
        else:
            return False

    @property
    def data(self):
        if not self._validated:
            raise ValidationError("Data property is called before is_valid()")
        return self._validated_data