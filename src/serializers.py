
from rest_framework import serializers

from restapi.config_policy import models


class ConfigPolicySchemeSerializer(serializers.ModelSerializer):

    policy_id = serializers.IntegerField(source='policy_id')

    class Meta(object):
        model = models.ConfigPolicyScheme
        fields = (
            'policy_id', 'scheme_id', 'scheme_name',
            'scheme_type', 'scheme_description')

    def validate(self, attr):

        existing_scheme_names = self.Meta.model.objects.filter(
            policy=attr.get('policy_id'),
            scheme_name=attr.get('scheme_name'))

        if existing_scheme_names.exists():
            raise serializers.ValidationError({
                'scheme_name': [
                    'scheme_name "{0}" is already exists.'.format(attr.get('scheme_name'))
                ]
            })

        return super(ConfigPolicySchemeSerializer, self).validate(attr)


class ConfigPolicyRuleSerializer(serializers.ModelSerializer):

    policy_id = serializers.IntegerField(source='policy_id')

    class Meta(object):
        model = models.ConfigPolicyRule
        fields = (
            'policy_id', 'rule_id', 'eval_expression')


class ConfigPolicySerializer(serializers.ModelSerializer):

    schema = ConfigPolicySchemeSerializer(many=True, read_only=True)
    rules = ConfigPolicyRuleSerializer(many=True, read_only=True)

    class Meta(object):
        model = models.ConfigPolicy
        fields = (
            'policy_id', 'policy_description',
            'policy_name', 'schema', 'rules')


class ConfigPolicyDynamicSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        validation_fields = kwargs.pop('validation_fields')
        super(ConfigPolicyDynamicSerializer, self).__init__(*args, **kwargs)

        if validation_fields:
            for field in validation_fields:
                self.fields[field] = serializers.CharField(required=True)
