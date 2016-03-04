
from django.db import models
from django.db import IntegrityError

import jinja2

from restapi.shared_components.models import BaseModel


CONFIG_MODEL_NAME_MAX_LENGTH = 40
CONFIG_MODEL_DESCRIPTION_MAX_LENGTH = 4096


def singleton(_class):

    ''' Singleton decorator '''

    instances = {}

    def getinstance(*args, **kwargs):
        if _class not in instances:
            instances[_class] = _class(*args, **kwargs)

        return instances[_class]

    return getinstance


@singleton
class ConfigPolicyEnvironment(object):

    ''' returns jinja2.Environment instance
        which has some global functions. '''

    # environment namespaces
    env_global = {
        'max': max,
        'min': min,
        'len': len
    }

    def __init__(self):
        self.environment = jinja2.Environment()

        for name, fn in self.env_global.iteritems():
            self.environment.globals[name] = fn


class ConfigPolicyAbstractModel(BaseModel):

    class RestAPIModelMeta(object):
        router = 'config_policy'
        allow_delete = True

    class Meta(object):
        abstract = True

    # singleton facade
    @property
    def environment(self):
        return ConfigPolicyEnvironment().environment


class ConfigPolicy(ConfigPolicyAbstractModel):

    policy_id = models.AutoField(primary_key=True)

    policy_name = models.CharField(
        max_length=CONFIG_MODEL_NAME_MAX_LENGTH, null=False, unique=True)

    policy_description = models.CharField(
        max_length=CONFIG_MODEL_DESCRIPTION_MAX_LENGTH, null=True)

    class Meta(object):
        db_table = 'config_policy'

    @property
    def schema(self):
        return ConfigPolicyScheme.objects.filter(policy=self)

    @property
    def rules(self):
        return ConfigPolicyRule.objects.filter(policy=self)

    def add_scheme(self, config_policy_scheme):

        config_policy_scheme.policy = self
        config_policy_scheme.save()

        return config_policy_scheme

    def remove_scheme(self, config_policy_scheme):

        if config_policy_scheme.policy == self:
            config_policy_scheme.delete()

            return True

        else:
            return False

    def add_rule(self, config_policy_rule):

        config_policy_rule.policy = self
        config_policy_rule.save()

        return config_policy_rule

    def remove_rule(self, config_policy_rule):

        if config_policy_rule.policy == self:
            config_policy_rule.delete()
            return True

        else:
            return False

    def validate_self_schema(self):
        validation_result = True
        violation_list = {}

        return validation_result, violation_list

    def validate_self_rules(self, schema_names):

        ''' Validates policy rules with policy schema
            It returns aggregated validation result. '''

        rule_validation = True
        violation_list = {}

        for rule in self.rules:

            result, reason = rule.validate_self(schema_names)

            rule_validation &= result

            if result is False:
                key = "rule_%s" % str(rule.rule_id)

                violation_list[key] = []

                for wrong_scheme in reason:
                    violation_list[key].append(
                        '"{0}" is not in policy schma'.format(wrong_scheme))

        return rule_validation, violation_list

    def validate_self(self):

        schema_names = [
            str(scheme.scheme_name) for scheme in self.schema
        ]

        violation_list = {}

        # validate policy schema
        schema_validation, schema_violation_list = self.validate_self_schema()

        # validation policy rules
        rule_validation, rule_violation_list = self.validate_self_rules(schema_names)

        # aggregate violation list
        if schema_violation_list:
            violation_list['schema'] = schema_violation_list

        if rule_violation_list:
            violation_list['rule'] = rule_violation_list

        # aggregate validation results
        total_validation = all((
            schema_validation,
            rule_validation
        ))

        return total_validation, violation_list

    def validate(self, *args, **kwargs):

        violation_list = {}
        total_validation = True

        for rule in self.rules:
            validation_result = rule.validate(**kwargs)

            if validation_result is False:
                violation_list[rule.rule_id] = rule.eval_expression

            total_validation &= validation_result

        return total_validation, violation_list


class ConfigPolicyScheme(ConfigPolicyAbstractModel):

    scheme_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(
        ConfigPolicy, null=False,
        db_column='policy_id')

    scheme_name = models.CharField(
        max_length=CONFIG_MODEL_NAME_MAX_LENGTH, null=False)

    scheme_type = models.CharField(
        max_length=CONFIG_MODEL_NAME_MAX_LENGTH, null=False)

    scheme_description = models.CharField(
        max_length=CONFIG_MODEL_DESCRIPTION_MAX_LENGTH, null=True)

    class Meta(object):
        db_table = 'config_policy_scheme'
        unique_together = ('scheme_id', 'policy_id')

    def save(self, *args, **kwargs):

        existing_scheme_name = ConfigPolicyScheme.objects.filter(
            policy=self.policy, scheme_name=self.scheme_name)

        if existing_scheme_name.exists():
            raise IntegrityError(
                'scheme_name "{0}" is already exists.'.format(self.scheme_name))

        super(ConfigPolicyScheme, self).save(*args, **kwargs)


class ConfigPolicyRule(ConfigPolicyAbstractModel):

    rule_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(
        ConfigPolicy, null=False,
        db_column='policy_id')

    eval_expression = models.CharField(
        max_length=CONFIG_MODEL_DESCRIPTION_MAX_LENGTH, null=False)

    class Meta(object):
        db_table = 'config_policy_rule'

    def save(self, *args, **kwargs):

        try:

            # this routine will occurs TemplateSyntaxError
            # when expression syntax is wrong.
            self.compiled_expression

            # if compile passed, then save record.
            super(ConfigPolicyRule, self).save(*args, **kwargs)

        except jinja2.exceptions.TemplateSyntaxError as template_error:

            raise IntegrityError(
                'eval_expression "{0}" occurs syntax error : {1}.'.format(
                    self.eval_expression, template_error))

    @property
    def compiled_expression(self):

        ''' Compile Expression with Environment instance '''

        return self.environment.compile_expression(
            self.eval_expression, undefined_to_none=False)

    def validate_self(self, schema_names):

        ''' validates self eval_expression with env and schema_name.
            It returns validation result and violation schma name list. '''

        rule_parser = jinja2.parser.Parser(self.environment, self.eval_expression, state='variable')
        expression = rule_parser.parse_expression()

        expr_name_nodes = expression.find_all(jinja2.nodes.Name)

        name_list = set([
            node.name for node in expr_name_nodes
        ])

        matched_names = set([
            name for name in name_list
            if name in schema_names + self.environment.globals.keys()
        ])

        return name_list == matched_names, list(name_list - matched_names)

    def validate(self, *args, **kwargs):

        ''' validate kwargs with compiled expression.
            It retruns validation result '''

        validation_result = self.compiled_expression(**kwargs)

        return validation_result
