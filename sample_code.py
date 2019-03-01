from unittest import TestCase


class MyTests(TestCase):
    """ doc string """
    def test_foo():
        print "hello"

    # for some_var
    some_var = 3

    def __init__(*args, **kwargs):
        print "boo"

    """ not a docstring """
    flup = "asdf"
    # for test_aaa

    def test_aaa(self):
        """foo"""
        # don't take me out of test_aaa
        a = 2 + 2
        assert(a == 4)
