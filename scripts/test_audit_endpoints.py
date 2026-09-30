"""Offline checks for catalog generation: python -m unittest discover -s scripts."""

import unittest

from audit_endpoints import normalize, parse_wadl


class CatalogTests(unittest.TestCase):
    def test_nested_paths_and_query_parameters(self):
        raw = b'''<application xmlns="http://wadl.dev.java.net/2009/02">
          <resources base="http://internal.invalid/v2/">
            <resource path="sports/{sport}">
              <param style="query" name="lang"/>
              <resource path="leagues/{league}">
                <method name="GET" id="getLeague"><request>
                  <param style="query" name="limit"/>
                  <param style="query" name="lang"/>
                </request></method>
              </resource>
            </resource>
          </resources>
        </application>'''
        records = parse_wadl(raw, "https://sports.core.api.espn.com/v2")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["url"], "https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}")
        self.assertEqual(records[0]["query_parameters"], ["lang", "limit"])

    def test_normalization_keeps_distinct_resources(self):
        self.assertEqual(normalize("/sports/football/leagues/nfl/athletes/{id}"),
                         normalize("/sports/{sport}/leagues/{league}/athletes/{athlete}"))
        self.assertNotEqual(normalize("/athletes/{id}"), normalize("/teams/{id}"))
