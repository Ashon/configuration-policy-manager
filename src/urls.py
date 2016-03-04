
from django.conf.urls.defaults import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from restapi.config_policy import views


restfw_api_urlpatterns = patterns(
    'restapi.config_policy',

    url(
        regex=r'^config_policy/$',
        view=views.ConfigPolicyListAPI.as_view(),
        name='config_policy_list_api'),

    url(
        regex=r'^config_policy/(?P<policy_id>[0-9]+)/$',
        view=views.ConfigPolicyAPI.as_view(),
        name='config_policy_api'),

    url(
        regex=r'^config_policy/(?P<policy_id>[0-9]+)/scheme/$',
        view=views.ConfigPolicySchemeListAPI.as_view(),
        name='config_policy_scheme_list_api'),

    url(
        regex=r'^config_policy/(?P<policy_id>[0-9]+)/scheme/(?P<scheme_id>[0-9]+)/$',
        view=views.ConfigPolicySchemeAPI.as_view(),
        name='config_policy_scheme_api'),

    url(
        regex=r'^config_policy/(?P<policy_id>[0-9]+)/rule/$',
        view=views.ConfigPolicyRuleListAPI.as_view(),
        name='config_policy_rule_list_api'),

    url(
        regex=r'^config_policy/(?P<policy_id>[0-9]+)/rule/(?P<rule_id>[0-9]+)/$',
        view=views.ConfigPolicyRuleAPI.as_view(),
        name='config_policy_rule_api'),

    url(
        regex=r'^config_policy/(?P<policy_id>[0-9]+)/validate/$',
        view=views.ConfigPolicyValidationAPI.as_view(),
        name='config_policy_validation_api'),
)


urlpatterns = format_suffix_patterns(restfw_api_urlpatterns)
