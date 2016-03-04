
import unittest
import os
import random

os.environ['DJANGO_SETTINGS_MODULE'] = 'restapi.settings'

from django.db import IntegrityError

from restapi.config_policy import models
from restapi.config_policy.tests.utils import get_test_hash_id


class TestConfigPolicysSchemeModel(unittest.TestCase):

    def setUp(self):
        self.test_prefix_hash = get_test_hash_id('scheme_test')
        self.policy_name = '%s-policy_%s' % (
            self.test_prefix_hash,
            random.randrange(1000, 9999)
        )

        exists_policy = models.ConfigPolicy.objects.filter(
            policy_name__contains=self.test_prefix_hash)

        if any((exists_policy, )):
            raise Exception('test hash already exists.')

        self.test_policy = models.ConfigPolicy(
            policy_name=self.policy_name)

        self.test_policy.save()

    def tearDown(self):

        try:
            # cleanup test policy
            query_result = models.ConfigPolicy.objects.filter(
                policy_name__contains=self.test_prefix_hash)
            query_result.delete()

        except models.ConfigPolicy.DoesNotExist:
            pass

        # teardown test
        # raise error if some records are remaining..
        remaining_schemes = models.ConfigPolicy.objects.filter(
            policy_name__contains=self.test_prefix_hash)
        self.assertEqual(len(remaining_schemes), 0)

    def test_save_duplicated_scheme(self):

        duplicated_name = 'duplicated_scheme-%s' % random.randrange(1000, 9999)
        policy_scheme_a = models.ConfigPolicyScheme(
            scheme_name=duplicated_name,
            scheme_type='some_type_a')

        # before save
        self.assertEqual(policy_scheme_a.scheme_id, None)
        self.assertEqual(len(self.test_policy.schema), 0)

        # do save
        self.test_policy.add_scheme(policy_scheme_a)

        # after save
        self.assertEqual(self.test_policy.policy_id, policy_scheme_a.policy.policy_id)
        self.assertEqual(type(policy_scheme_a.scheme_id), long)
        self.assertEqual(len(self.test_policy.schema), 1)

        policy_scheme_b = models.ConfigPolicyScheme(
            scheme_name=duplicated_name,
            scheme_type='some_type_b')

        with self.assertRaises(IntegrityError):
            self.test_policy.add_scheme(policy_scheme_b)
