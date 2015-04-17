# coding=utf-8
from unittest import TestCase

from fields import Field, IntegerField, CharField, EmailField, URLField, BooleanField
from validator_exceptions import ValidationError

import validators
import validator_exceptions


class FieldsTest(TestCase):
    def setUp(self):
        pass

    def test_char_field(self):
        # required
        c = CharField(required=True)
        self.assertRaises(ValidationError, c.validate, None)

        c = CharField(required=False)
        self.assertEqual(c.validate("1234567890"), "1234567890")

        # min length
        c = CharField(min_length=4)
        self.assertRaises(ValidationError, c.validate, "123")
        self.assertEqual(c.validate("1234"), "1234")
        self.assertEqual(c.validate("1234"), "1234")

        # max length
        c = CharField(max_length=4)
        self.assertRaises(ValidationError, c.validate, "11111")
        self.assertEqual(c.validate("1234"), "1234")
        self.assertEqual(c.validate("123"), "123")
        self.assertEqual(c.validate(""), "")
