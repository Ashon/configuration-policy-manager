
import unittest
import os
import random

os.environ['DJANGO_SETTINGS_MODULE'] = 'restapi.settings'

from django.db import IntegrityError
from jinja2 import Environment
from jinja2.exceptions import TemplateSyntaxError

from restapi.config_policy import models
from restapi.config_policy.tests.utils import get_test_hash_id


class TestConfigPolicyRuleModel(unittest.TestCase):

    def setUp(self):

        self.test_prefix_hash = get_test_hash_id('rule_test')
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

    def test_eval_expression(self):

        expression = 'schemeA == True'
        expr_kwargs = {
            'schemeA': False
        }

        rule = models.ConfigPolicyRule(eval_expression=expression)
        expr = rule.compiled_expression
        self.assertEqual(expr(**expr_kwargs), False)

    def test_cmp_one_to_multiple_expr(self):

        string = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'
        dataset = string.split(' ')
        expr_kwargs = {
            'schemeA': random.choice(dataset),
            'dataset': dataset
        }

        expression = 'schemeA in dataset'
        rule = models.ConfigPolicyRule(eval_expression=expression)
        expr = rule.compiled_expression

        self.assertEqual(expr(**expr_kwargs), True)

        self.assertEqual(expr({
            'schemeA': 'I\'m not in dataset',
            'dataset': dataset
        }), False)

    def test_set_equality(self):

        expression = 'setA == setB'
        rule = models.ConfigPolicyRule(eval_expression=expression)
        expr = rule.compiled_expression

        res = expr(
            setA=set((1, 2, 4, 3, 5)),
            setB=set((1, 2, 3, 4, 5))
        )

        self.assertEqual(res, True)

    def test_rule_without_policy(self):
        expression = 'setA == setB'
        rule = models.ConfigPolicyRule(eval_expression=expression)

        with self.assertRaises(IntegrityError):
            rule.save()

    def test_use_predefined_fn(self):
        expression = '"".join(["a", "b"])'
        rule = models.ConfigPolicyRule(eval_expression=expression)
        expr = rule.compiled_expression
        self.assertEqual(expr(), 'ab')

    def test_use_import(self):
        expression = 'import sys'
        rule = models.ConfigPolicyRule(eval_expression=expression)

        with self.assertRaises(TemplateSyntaxError):
            rule.compiled_expression

    def test_rules_in_policy(self):

        self.test_policy.add_rule(
            models.ConfigPolicyRule(eval_expression='word in wordlist'))

        self.test_policy.add_rule(
            models.ConfigPolicyRule(eval_expression='word == "Lorem"'))

        self.assertEqual(len(self.test_policy.rules), 2)

        # test dataset
        word = 'Lorem'
        word_list = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'.split(' ')

        for rule in self.test_policy.rules:
            assertion = rule.compiled_expression(word=word, wordlist=word_list)
            self.assertEqual(assertion, True)

    def test_policy_validation(self):

        # add schema
        self.test_policy.add_scheme(
            models.ConfigPolicyScheme(scheme_name='word'))
        self.test_policy.add_scheme(
            models.ConfigPolicyScheme(scheme_name='wordlist'))

        # assert schema length
        self.assertEqual(len(self.test_policy.schema), 2)

        # add policy rule
        self.test_policy.add_rule(
            models.ConfigPolicyRule(eval_expression='word in wordlist'))
        self.test_policy.add_rule(
            models.ConfigPolicyRule(eval_expression='word == "Lorem"'))

        # assert rules length
        self.assertEqual(len(self.test_policy.rules), 2)

        # test form data
        form_data = {
            'word': 'Lorem',
            'wordlist': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'.split(' ')
        }
        # assert True
        self.assertTrue(self.test_policy.validate(**form_data))

        # wrong form data
        wrong_form_data = {
            'word': 'lorem',
            'wordlist': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'.split(' ')
        }
        # assert False
        validation, reason = self.test_policy.validate(**wrong_form_data)
        self.assertFalse(validation)

    def test_policy_rule_self_validation_without_envvar(self):

        # without environ function
        policy_rule_a = models.ConfigPolicyRule(eval_expression='word in wordlist')
        self.test_policy.add_rule(policy_rule_a)

        total_validation, violation_list = policy_rule_a.validate_self(['word', 'wordlist'])
        self.assertTrue(total_validation)

        expr_a = policy_rule_a.compiled_expression
        self.assertTrue(expr_a(word='a', wordlist=['a', 'b', 'c']))

    def test_policy_rule_self_validation_with_envvar(self):

        # with environ function
        policy_rule_b = models.ConfigPolicyRule(eval_expression='max(numlist) == 5')
        self.test_policy.add_rule(policy_rule_b)

        total_validation, violation_list = policy_rule_b.validate_self(['numlist'])
        self.assertTrue(total_validation)

        expr_b = policy_rule_b.compiled_expression
        self.assertTrue(expr_b(numlist=[1, 3, 5]))

    def test_self_validation_many(self):

        def get_abc(a=None, b=None, c=None):
            return {'a': a, 'b': b, 'c':c}

        env = Environment()

        names = ['a', 'b', 'c']

        # operand test..
        # unary, binary, compare
        expressions = [

            ('a * b == c', get_abc(a=2, b=4, c=8)),

            ('a and b == True', get_abc(a=True, b=True)),

            ('not a and b', get_abc(a=False, b=True)),

            ('a != b', get_abc(a=False, b=True)),

            ('a == b == c', get_abc(a=2, b=2, c=2)),

            ('a - b - c == 0', get_abc(a=2, b=1, c=1)),

            ('not a', get_abc(a=False)),

            ('(a + b) * c == 316', get_abc(a=1, b=1, c=158)),

            ('a in b', get_abc(a=1, b=[1, 2, 3, 1, 4, 2])),

            ('a not in b', get_abc(a=1, b=[6, 2, 3, 5, 4, 2])),

            ('a.__len__() == 3', get_abc(a=[1, 2, 3])),

            ('a < 3', get_abc(a=2)),

            ('a < b + c', get_abc(a=5, b=3, c=3))

            #   :
        ]

        for expr, test_var in expressions:
            policy_rule = models.ConfigPolicyRule(eval_expression=expr)

            # validate each rule expressions
            validation_result, reason = policy_rule.validate_self(names)
            self.assertTrue(validation_result)

            # all expressions will returns true
            func = policy_rule.compiled_expression
            compare_result = func(**test_var)
            self.assertTrue(compare_result)

    def test_import_module_in_env(self):

        import re
        names = ['a']

        expr = "match('^[a-zA-Z]*$', a)"
        policy_rule = models.ConfigPolicyRule(eval_expression=expr)
        policy_rule.environment.globals['match'] = re.match

        validation_result, reason = policy_rule.validate_self(names)
        self.assertTrue(validation_result)

        func = policy_rule.compiled_expression

        regex_match_result = func(a='afwef')
        self.assertTrue(regex_match_result)

        regex_match_result = func(a='afwe1f')
        self.assertFalse(regex_match_result)
