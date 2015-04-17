# coding=utf-8
from unittest import TestCase

from fields import Field, IntegerField, CharField, EmailField, URLField, BooleanField, FloatField
from validator_exceptions import ValidationError

import validators
import validator_exceptions


class FieldsTest(TestCase):
    def setUp(self):
        pass

    def test_char_field(self):
        # data type
        c = CharField()
        self.assertRaises(ValidationError, c.validate, 100)

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

        # both max min
        c = CharField(max_length=3, min_length=3)
        self.assertRaises(ValidationError, c.validate, "11")
        self.assertRaises(ValidationError, c.validate, "1111")
        self.assertEqual(c.validate("123"), "123")

    def test_integer_field(self):
        # data type
        f = IntegerField()
        self.assertRaises(ValidationError, f.validate, "123")
        self.assertRaises(ValidationError, f.validate, 123.4)

        # required
        f = IntegerField(required=True)
        self.assertRaises(ValidationError, f.validate, None)

        f = IntegerField(required=False)
        self.assertEqual(f.validate(123), 123)

        # max
        f = IntegerField(max=100)
        self.assertRaises(ValidationError, f.validate, 101)
        self.assertEqual(f.validate(100), 100)

        # min
        f = IntegerField(min=100)
        self.assertRaises(ValidationError, f.validate, 99)
        self.assertEqual(f.validate(100), 100)

        # test both min max
        f = IntegerField(max=100, min=100)
        self.assertRaises(ValidationError, f.validate, 99)
        self.assertRaises(ValidationError, f.validate, 101)
        self.assertEqual(f.validate(100), 100)

    def test_float_field(self):
        # data type
        f = FloatField()
        self.assertRaises(ValidationError, f.validate, 123)
        self.assertRaises(ValidationError, f.validate, "123")

        # required
        f = FloatField(required=True)
        self.assertRaises(ValidationError, f.validate, None)

        f = FloatField(required=False)
        self.assertEqual(f.validate(123.23), 123.23)

        # max
        f = FloatField(max=100.03)
        self.assertRaises(ValidationError, f.validate, 100.031)
        self.assertEqual(f.validate(100.01), 100.01)

        # min
        f = FloatField(min=100.01)
        self.assertRaises(ValidationError, f.validate, 100.0)
        self.assertEqual(f.validate(100.01), 100.01)

        # test both min max
        f = FloatField(max=100.034, min=100.034)
        self.assertRaises(ValidationError, f.validate, 99.2)
        self.assertRaises(ValidationError, f.validate, 100.1)
        self.assertEqual(f.validate(100.034), 100.034)

    def test_email_field(self):
        # data type
        f = EmailField()
        self.assertRaises(ValidationError, f.validate, 123)

        # max length
        f = EmailField(max_length=15)
        self.assertRaises(ValidationError, f.validate, "1fsd239f342fe23fer32ews@qq.com")
        self.assertEqual(f.validate("12345@qq.com"), "12345@qq.com")

        # email format
        f = EmailField()
        for item in ["123", "123@", "@qq.com", "@qq", "123@", "123@qq", "123#qq.com"]:
            self.assertRaises(ValidationError, f.validate, item)

        for item in ["123@qq.aa.com", "123fsdljk@staff.qq.com.cn"]:
            self.assertEqual(f.validate(item), item)

    def test_url_field(self):
        # data type
        f = URLField()
        self.assertRaises(ValidationError, f.validate, 123)

        # length
        f = URLField(max_length=20)
        self.assertRaises(ValidationError, f.validate, "http://baidu.com/11111111111111111/2222222222/?fsdfds=122")

        f = URLField()

        # url format
        for item in ["baidu.com", "htt://baidu.com", "http://baidu", "https:baidu.com",
                     "https//baidu.com", "//baidu.com"]:
            self.assertRaises(ValidationError, f.validate, item)

        for item in ["http://baidu.com", "http://www.baidu.com", "http://baidu.com/",
                     "https://baidu.com", "ftp://baidu.com", "http://8.8.8.8", "http://baidu.com:1023",
                     "http://8.8.8.8:8080"]:
            self.assertEqual(f.validate(item), item)

    def test_boolean_field(self):
        f = BooleanField()

        for item in [1, "1", "true", "True", True]:
            self.assertEqual(f.validate(item), True)
        for item in [0, "0", "false", "False", False]:
            self.assertEqual(f.validate(item), False)

        for item in [2, "2", {}]:
            self.assertRaises(ValidationError, f.validate, item)