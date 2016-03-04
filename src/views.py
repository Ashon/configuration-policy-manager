
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from restapi.common import generics
from restapi.common import mixins
from restapi.config_policy import models
from restapi.config_policy import serializers


class ConfigPolicyListAPI(generics.RestAPIGenericView,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):

    queryset = models.ConfigPolicy.objects.all()
    serializer_class = serializers.ConfigPolicySerializer
    search_fields = ('policy_name', 'policy_description')

    def get(self, request, *args, **kwargs):
        return super(
            ConfigPolicyListAPI, self
        ).list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(
            ConfigPolicyListAPI, self
        ).create(request, *args, **kwargs)


class ConfigPolicyAPI(generics.RestAPIGenericView,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):

    queryset = models.ConfigPolicy.objects.all()
    serializer_class = serializers.ConfigPolicySerializer
    lookup_url_kwarg = 'policy_id'

    def get(self, request, *args, **kwargs):
        return super(
            ConfigPolicyAPI, self
        ).retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super(
            ConfigPolicyAPI, self
        ).update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(
            ConfigPolicyAPI, self
        ).destroy(request, *args, **kwargs)


class ConfigPolicySchemeListAPI(generics.RestAPIGenericView,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin):

    queryset = models.ConfigPolicyScheme.objects.all()
    serializer_class = serializers.ConfigPolicySchemeSerializer
    lookup_url_kwarg = 'policy_id'
    search_fields = ('scheme_name', 'scheme_type', 'scheme_description')

    def get_queryset(self):
        policy_id = self.kwargs.get('policy_id')
        return models.ConfigPolicyScheme.objects.filter(policy=policy_id)

    def get(self, request, *args, **kwargs):
        return super(
            ConfigPolicySchemeListAPI, self
        ).list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        request.DATA.update(kwargs)

        return super(
            ConfigPolicySchemeListAPI, self
        ).create(request, *args, **kwargs)


class ConfigPolicySchemeAPI(generics.RestAPIGenericView,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):

    queryset = models.ConfigPolicyScheme.objects.all()
    serializer_class = serializers.ConfigPolicySchemeSerializer
    lookup_url_kwarg = 'scheme_id'

    def get(self, request, *args, **kwargs):
        return super(
            ConfigPolicySchemeAPI, self
        ).retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):

        request.DATA.update(kwargs)

        return super(
            ConfigPolicySchemeAPI, self
        ).update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):

        request.DATA.update(kwargs)

        return super(
            ConfigPolicySchemeAPI, self
        ).destroy(request, *args, **kwargs)


class ConfigPolicyRuleListAPI(generics.RestAPIGenericView,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):

    queryset = models.ConfigPolicyRule.objects.all()
    serializer_class = serializers.ConfigPolicyRuleSerializer
    lookup_url_kwarg = 'policy_id'
    search_fields = ('rule_id', 'eval_expression')

    def get(self, request, *args, **kwargs):
        return super(
            ConfigPolicyRuleListAPI, self
        ).list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        request.DATA.update(kwargs)

        return super(
            ConfigPolicyRuleListAPI, self
        ).create(request, *args, **kwargs)


class ConfigPolicyRuleAPI(generics.RestAPIGenericView,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):

    queryset = models.ConfigPolicyRule.objects.all()
    serializer_class = serializers.ConfigPolicyRuleSerializer
    lookup_url_kwarg = 'rule_id'

    def get(self, request, *args, **kwargs):
        return super(
            ConfigPolicyRuleAPI, self
        ).retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):

        request.DATA.update(kwargs)

        return super(
            ConfigPolicyRuleAPI, self
        ).update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):

        request.DATA.update(kwargs)

        return super(
            ConfigPolicyRuleAPI, self
        ).destroy(request, *args, **kwargs)


class ConfigPolicyValidationAPI(generics.RestAPIGenericView):

    queryset = models.ConfigPolicy.objects.all()
    serializer_class = serializers.ConfigPolicySerializer
    lookup_url_kwarg = 'policy_id'

    def get_policy_form_serializer(self, *args, **kwargs):
        schema_name_list = [scheme.scheme_name for scheme in self.get_object().schema]

        return serializers.ConfigPolicyDynamicSerializer(
            validation_fields=schema_name_list, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        policy = self.get_object()
        result, reason = policy.validate_self()
        status_code = status.HTTP_200_OK

        return Response({
            'result': result,
            'reason': reason
        })

    def post(self, request, *args, **kwargs):

        # validate request form by policy schema
        form_serializer = self.get_policy_form_serializer(data=request.DATA)

        if form_serializer.is_valid():

            cleaned_data = form_serializer.data
            policy = self.get_object()

            result, reason = policy.validate(**cleaned_data)

            if result:
                response_data = {
                    'result': result,
                    'reason': reason
                }
                status_code = status.HTTP_200_OK

            else:
                response_data = {
                    'result': result,
                    'reason': reason
                }
                status_code = status.HTTP_400_BAD_REQUEST

        else:
            response_data = {
                'result': False,
                'reason': form_serializer.errors
            }
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=status_code)
