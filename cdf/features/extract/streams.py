import re

from cdf.core.metadata.constants import FIELD_RIGHTS
from cdf.features.extract.settings import GROUPS
from cdf.metadata.url.url_metadata import (
    INT_TYPE, STRING_TYPE, BOOLEAN_TYPE,
    FLOAT_TYPE,
    ES_NOT_ANALYZED
)
from cdf.core.streams.base import StreamDefBase


_EXTRACT_RESULT_COUNT = 5


def render_field_strategy(features_options, field_name, field_settings,
                          public_field_settings):
    """
    Modify field object generated by `cdf.query.datamodel.get_fields

    :param features_options: All features options for this analysis
    :param field_name : field_
    :param field_name : initial field settings as defined in StreamDef class
    :param public_field_settings : dict of public field generated by cdf.query.datamodel.get_fields
    """
    # Iterate on options from `extract` feature
    # Format is
    # [
    #    {
    #        "name":            "string",   # rule name slugified
    #        "rx":              "string",
    #        "rx_match":        "string",
    #        "rx_ignore_case":  "bool",
    #        "agg":             "string : list, first, count, exist",
    #        "es_field":    "string",
    #        "cast":                  "string : s, i, b, f"
    #    },
    #    ...
    # ]
    for field in features_options["extract"]:
        if "extract.{}".format(field["es_field"]) == field_name:
            # If we extract a list, we put the flag as multiple
            # (as we may store items or list of items depending on the crawl)
            # it's always multiple=false by default
            if field["agg"] == "list":
                public_field_settings["multiple"] = True
            # Set name created by user
            public_field_settings["name"] = field["name"]


def check_enabled(field):
    """
    return True if extract field is enabled
    All es_fields from
    """
    def _check_enabled_options(extract_options):
        return any(f["es_field"] == field for f in extract_options)
    return _check_enabled_options


def _generate_ers_document_mapping():
    """
    ExtractResultsStreamDef's URL_DOCUMENT_MAPPING
    """
    dm = {}
    for type_name, short_type_name in (STRING_TYPE, 's'), (INT_TYPE, 'i'),\
                                      (BOOLEAN_TYPE, 'b'), (FLOAT_TYPE, 'f'):
        for i in range(_EXTRACT_RESULT_COUNT):
            dm["extract.extract_%s_%i" % (short_type_name, i)] = {
                "type": type_name,
                "default_value": None,
                "settings": {
                    ES_NOT_ANALYZED,
                    FIELD_RIGHTS.ADMIN
                },
                "render_field_modifier": render_field_strategy,
                "enabled": check_enabled("extract_%s_%i" % (short_type_name, i))
            }
    return dm


class ExtractResultsStreamDef(StreamDefBase):
    FILE = 'urlextract'
    HEADERS = (
        ('id', int),  # url_id
        ('label', str),  # user-entered name
        ('es_field', str),  # ES label
        ('agg', str),  # list, first, count, exist
        ('cast', str),  # empty (s), s(tr), i(nt), b(ool), f(loat)
        ('rank', int),  # for lists; they come unordered!
        ('value', str)  # bool is '0'/'1'
    )

    URL_DOCUMENT_DEFAULT_GROUP = GROUPS.extract.name

    URL_DOCUMENT_MAPPING = _generate_ers_document_mapping()
    _RE_BLANKS = re.compile(r"\s+")

    def process_document(self, document, stream):
        url_id, label, es_field, agg, cast, rank, value = stream
        if cast:
            value = self._apply_cast(cast, value)

        if agg != "list":
            document["extract"][es_field] = value
        else:
            self._put_in_place(document["extract"], es_field, rank, value)

    @staticmethod
    def _apply_cast(cast, value):
        """
        Cast value according to cast.
        :param cast: Expected type ("" == str)
        :type cast: str
        :param value: String input value
        :type value: str
        :return:Casted value
        """
        if not cast or cast == 's':
            return value
        value = ExtractResultsStreamDef._RE_BLANKS.sub("", value)
        if cast == 'i':
            try:
                return int(value)
            except ValueError:
                return None
        if cast == 'b':
            return value == '1'  # or value[0].lower() in 'typo'
        if cast == 'f':
            try:
                return float(value)
            except ValueError:
                return None
        raise AssertionError("{} not in 'sibf'".format(cast))

    @staticmethod
    def _put_in_place(extract, es_field, rank, value):
        """
        Put value in extract[label] at the specified rank.
        If the array is too short, add some None.
        :param extract: document["extract"]
        :type extract: dict
        :param es_field: ES field name
        :type es_field: str
        :param rank: position
        :type rank: int
        :param value: what to put
        :type value:
        """
        if rank < 0:
            return
        if extract[es_field] is None:
            tmp = []
        elif not isinstance(extract[es_field], list):
            tmp = [extract[es_field]]
        else:
            tmp = extract[es_field]
        while len(tmp) <= rank:
            tmp.append(None)
        tmp[rank] = value
        extract[es_field] = tmp
