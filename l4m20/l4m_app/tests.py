from django.test import TestCase
from . import utilities as U

class Tests(TestCase):

    def test_get_all_teams(self):
        U.get_all_teams()
