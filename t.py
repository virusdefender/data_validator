# coding=utf-8
import validators


class MyValidator(validators.Validator):
    username = validators.CharField(show_name=u"用户名", max_length=20, min_length=3)
    age = validators.IntegerField(max=90, min=18)
    email = validators.EmailField(max_length=20)
    url = validators.URLField()

t = MyValidator({"username": "123", "age": 40, "email": "123433@42423.com", "url": "http://baidu.com"})
if t.is_validate():
    print t.data
else:
    print t.errors