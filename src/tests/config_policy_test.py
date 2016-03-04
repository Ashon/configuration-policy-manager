
import unittest
import os
import random

os.environ['DJANGO_SETTINGS_MODULE'] = 'restapi.settings'

from django.db import IntegrityError

from restapi.config_policy import models
from restapi.config_policy.tests.utils import get_test_hash_id


class TestConfigPolicyModel(unittest.TestCase):

    def setUp(self):
        self.test_prefix_hash = get_test_hash_id('policy_test')
        self.policy_name = '%s-policy_%s' % (
            self.test_prefix_hash,
            random.randrange(1000, 9999)
        )

        exists_policy = models.ConfigPolicy.objects.filter(
            policy_name__contains=self.test_prefix_hash)

        if exists_policy.exists():
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

    def test_get_policy(self):

        policy = models.ConfigPolicy.objects.get(policy_name=self.policy_name)

        self.assertEqual(type(policy), models.ConfigPolicy)
        self.assertEqual(type(policy.policy_id), long)

    def test_duplicated_policy_name(self):

        duplicated_policy_name = self.test_policy.policy_name

        duplicated_policy = models.ConfigPolicy(
            policy_name=duplicated_policy_name)

        with self.assertRaises(IntegrityError):
            duplicated_policy.save()

    def test_add_scheme_to_policy(self):

        scheme_name = '%s-scheme_%s' % (
            self.test_prefix_hash,
            random.randrange(1000, 9999)
        )

        # insert and get test config policy to DB
        scheme = models.ConfigPolicyScheme(
            scheme_name='var_%s' % scheme_name,
            scheme_type='type_%s' % scheme_name)

        # add scheme to policy
        policy_scheme = self.test_policy.add_scheme(scheme)

        # do assert
        self.assertEqual(type(policy_scheme), models.ConfigPolicyScheme)
        self.assertEqual(policy_scheme.policy, self.test_policy)
        self.assertEqual(policy_scheme, scheme)

        # remove policy_scheme
        self.test_policy.remove_scheme(scheme)
        policy_scheme_list = self.test_policy.schema

        # scheme should not exists in test_policy's scheme list
        self.assertNotIn(scheme, policy_scheme_list)

    def test_drop_scheme_list(self):

        scheme_length = random.randrange(5, 10)

        for _ in range(scheme_length):

            scheme_name = '%s-scheme_%s' % (
                self.test_prefix_hash,
                random.randrange(1000, 9999)
            )

            # insert and get test config policy to DB
            scheme = models.ConfigPolicyScheme(
                scheme_name='var_%s' % scheme_name)

            self.test_policy.add_scheme(scheme)

        policy_scheme_list = self.test_policy.schema

        # length of policy_scheme_list should equals to scheme_length
        self.assertEqual(scheme_length, len(policy_scheme_list))

        # drop and assert, length should equals to 0.
        self.test_policy.schema.delete()
        policy_scheme_list = self.test_policy.schema
        self.assertEqual(0, len(policy_scheme_list))

    def test_policy_j2env_singleton(self):

        policy_a = models.ConfigPolicy()
        policy_scheme = models.ConfigPolicyScheme()
        policy_rule = models.ConfigPolicyRule()

        self.assertEqual(
            policy_a.environment, policy_scheme.environment)

        self.assertEqual(
            policy_scheme.environment, policy_rule.environment)

        import re
        policy_a.environment.globals['match'] = re.match

        # policy_scheme should have 'match' which declared in all facades.
        self.assertTrue('match' in policy_scheme.environment.globals.keys())
        self.assertTrue('match' in policy_rule.environment.globals.keys())
        self.assertTrue('match' in models.ConfigPolicyEnvironment().environment.globals.keys())
