# coding=utf-8
import re
import sys

if sys.version > '3':
    from urllib.parse import urlunsplit, urlsplit
else:
    from urlparse import urlunsplit, urlsplit

from validator_exceptions import ValidationError


class Field(object):
    def __str__(self):
        return self.__class__.__name__


class CharField(Field):
    def __init__(self, show_name=None, required=True, max_length=None, min_length=None):
        self.show_name = show_name
        self.required = required
        self.max_length = max_length
        self.min_length = min_length

    def validate(self, value):
        if value is None and self.required is False:
            return value
        # python2
        try:
            if not isinstance(value, basestring):
                raise ValidationError("Must be a string")
        # python3
        except NameError:
            if not isinstance(value, str):
                raise ValidationError("Must be a string")

        if self.max_length and len(value) > self.max_length:
            raise ValidationError("Value is too long")

        if self.min_length and len(value) < self.min_length:
            raise ValidationError("Value is too short")

        return value


class NumberField(Field):
    def __init__(self, show_name=None, required=True, max=None, min=None):
        self.show_name = show_name
        self.required = required
        self.max = max
        self.min = min

    def validate(self, value):
        raise NotImplementedError("Number field validate method must be override")


class IntegerField(NumberField):
    def __init__(self, show_name=None, required=True, max=None, min=None):
        super(IntegerField, self).__init__(show_name=show_name, required=required, max=max, min=min)

    def validate(self, value):
        if value is None and self.required is False:
            return value

        if not isinstance(value, int):
            raise ValidationError("Must be an integer")

        if self.max is not None and value > self.max:
            raise ValidationError("Value is too large")

        if self.min is not None and value < self.min:
            raise ValidationError("Value is too small")

        return value


class FloatField(NumberField):
    def __init__(self, show_name=None, required=True, max=None, min=None):
        super(FloatField, self).__init__(show_name=show_name, required=required, max=max, min=min)

    def validate(self, value):
        if value is None and self.required is False:
            return value

        if not isinstance(value, float):
            raise ValidationError("Must be a integer")

        if self.max is not None and value > self.max:
            raise ValidationError("Value is too large")

        if self.min is not None and value < self.min:
            raise ValidationError("Value is too small")

        return value


class EmailField(CharField):
    def __init__(self, show_name=None, required=True, max_length=None):
        super(EmailField, self).__init__(show_name=show_name, required=required,
                                         max_length=max_length, min_length=5)

    def validate(self, value):
        value = super(EmailField, self).validate(value)
        user_regex = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)',
            re.IGNORECASE)
        domain_regex = re.compile(
            r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,}(?<!-))$'
            # literal form, ipv4 address (SMTP 4.1.3)
            r'|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',
            re.IGNORECASE)
        domain_whitelist = ['localhost']
        if '@' not in value:
            raise ValidationError("Email format is not correct")

        user_part, domain_part = value.rsplit('@', 1)

        if not user_regex.match(user_part):
            raise ValidationError("Email format is not correct")

        if (domain_part not in domain_whitelist and
                not domain_regex.match(domain_part)):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
                if not domain_regex.match(domain_part):
                    raise ValidationError("Email format is not correct")
                else:
                    return
            except UnicodeError:
                pass
            raise ValidationError("Invalid Email format")
        return value


class URLField(CharField):
    def __init__(self, show_name=None, required=True, max_length=None):
        super(URLField, self).__init__(show_name=show_name, required=required,
                                       max_length=max_length, min_length=5)

    def validate(self, value):
        value = super(URLField, self).validate(value)
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        scheme, netloc, path, query, fragment = urlsplit(value)
        try:
            netloc = netloc.encode('idna').decode('ascii')  # IDN -> ACE
        except UnicodeError:  # invalid domain part
            raise ValidationError("URL format invalid")
        url = urlunsplit((scheme, netloc, path, query, fragment))
        if not regex.search(url):
            raise ValidationError("URL format invalid")
        return value


class BooleanField(Field):
    def __init__(self, show_name=None, required=True):
        self.show_name = show_name
        self.required = required

    def validate(self, value):
        if value is None and self.required is False:
            return None
        mapping = {1: True, 0: False, "1": True, "0": False, "true": True, "false": False,
                   "True": True, "False": False, True: True, False: False}
        try:
            return mapping[value]
        except Exception:
            raise ValidationError("Value invalid")