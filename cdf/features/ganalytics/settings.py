from enum import Enum


NAME = "Analytics import"
DESCRIPTION = ""
ORDER = 1000

ORGANIC_SOURCES = (
    'google',
    'bing',
    'yahoo',
    "ask",
    "aol",
    "yandex",
    "baidu",
    "naver"
)

SOCIAL_SOURCES = (
    'facebook',
    'twitter',
    'pinterest',
    'linkedin',
    'reddit',
    'google+',
    'tumblr'
)


GROUPS = Enum(
    'Groups',
    [('visits.organic.all', 'Organic Visits')] +
    [('visits.organic.{}'.format(source), 'Organic Visits from {}'.format(source.capitalize())) for source in ORGANIC_SOURCES] +
    [('visits.social.all', 'Social Visits')] +
    [('visits.social.{}'.format(source), 'Social Visits from {}'.format(source.capitalize())) for source in SOCIAL_SOURCES]
)
