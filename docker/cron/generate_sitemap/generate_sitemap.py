#!/usr/bin/env python3

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generate sitemap."""
import logging
import sys
import os
import osv
import osv.logs
import datetime
import argparse
from google.cloud import ndb

from xml.etree.ElementTree import Element, SubElement, ElementTree

_OUTPUT_DIRECTORY = './sitemap_output'
_SITEMAPS_PREFIX = 'sitemap_'
_SITEMAP_INDEX_PATH = f'./{_SITEMAPS_PREFIX}index.xml'
_SITEMAP_URL_LIMIT = 49999


def fetch_vulnerability_ids(ecosystem: str) -> list[str]:
  """Fetch vulnerabilities' id for the given ecosystem."""
  bugs = osv.Bug.query(
      osv.Bug.status == osv.BugStatus.PROCESSED,
      osv.Bug.public == True,  # pylint: disable=singleton-comparison
      osv.Bug.ecosystem == ecosystem).order(-osv.Bug.timestamp)
  bug_ids = [bug.db_id for bug in bugs]
  return bug_ids


def osv_get_ecosystems():
  """Get list of ecosystems."""
  query = osv.Bug.query(projection=[osv.Bug.ecosystem], distinct=True)
  return sorted([bug.ecosystem[0] for bug in query if bug.ecosystem],
                key=str.lower)


def get_sitemap_filename_for_ecosystem(ecosystem: str) -> str:
  ecosystem_name = ecosystem.replace(' ', '_').replace('.', '__').strip()
  return f'./{_SITEMAPS_PREFIX}{ecosystem_name}.xml'


def get_sitemap_url_for_ecosystem(ecosystem: str, base_url: str) -> str:
  ecosystem_name = ecosystem.replace(' ', '_').replace('.', '__').strip()
  return f'{base_url}/{_SITEMAPS_PREFIX}{ecosystem_name}.xml'


def generate_sitemap_for_ecosystem(ecosystem: str, base_url: str) -> None:
  """Generate a sitemap for the give n ecosystem."""
  logging.info('Generating sitemap for ecosystem "%s".', ecosystem)
  vulnerability_ids = fetch_vulnerability_ids(ecosystem)
  filename = get_sitemap_filename_for_ecosystem(ecosystem)
  urlset = Element(
      'urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

  # TODO: For large ecosystems with over 50,000 vulnerabilities, generate
  # multiple sitemaps.
  for vuln in vulnerability_ids[:_SITEMAP_URL_LIMIT]:
    url = SubElement(urlset, 'url')
    loc = SubElement(url, 'loc')
    loc.text = f'{base_url}/vulnerability/{vuln}'
    lastmod = SubElement(url, 'lastmod')
    lastmod.text = datetime.datetime.now().isoformat()

  tree = ElementTree(urlset)
  tree.write(filename, encoding='utf-8', xml_declaration=True)


def generate_sitemap_index(ecosystems: set[str], base_url: str) -> None:
  """Generate a sitemap index."""
  logging.info('Generating sitemap index.')
  sitemapindex = Element(
      'sitemapindex', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

  for ecosystem in ecosystems:
    sitemap = SubElement(sitemapindex, 'sitemap')
    loc = SubElement(sitemap, 'loc')
    loc.text = get_sitemap_url_for_ecosystem(ecosystem, base_url)
    lastmod = SubElement(sitemap, 'lastmod')
    lastmod.text = datetime.datetime.now().isoformat()

  tree = ElementTree(sitemapindex)
  tree.write(_SITEMAP_INDEX_PATH, encoding='utf-8', xml_declaration=True)


def generate_sitemaps(base_url: str) -> None:
  """Generate sitemaps including all vulnerabilities, split by ecosystem."""

  # Go over the base ecosystems index. Otherwise we'll have duplicated
  # vulnerabilities in the sitemap.
  base_ecosystems = {
      ecosystem for ecosystem in osv_get_ecosystems() if ':' not in ecosystem
  }
  for ecosystem in base_ecosystems:
    generate_sitemap_for_ecosystem(ecosystem, base_url)

  generate_sitemap_index(base_ecosystems, base_url)


def main() -> int:
  parser = argparse.ArgumentParser(description='Generate sitemaps.')
  parser.add_argument(
      '--base_url',
      required=True,
      help='The base URL for the sitemap entries (without trailing /).')
  args = parser.parse_args()

  os.makedirs(_OUTPUT_DIRECTORY, exist_ok=True)
  os.chdir(_OUTPUT_DIRECTORY)

  generate_sitemaps(args.base_url)
  return 0


if __name__ == '__main__':
  _ndb_client = ndb.Client()
  osv.logs.setup_gcp_logging('generate_sitemap')
  with _ndb_client.context():
    sys.exit(main())
