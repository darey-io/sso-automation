#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from setuptools.glob import glob

DOCUMENTATION = r"""
module: api

author:
  - Dare (@darey-io)
short_description: TODO
description:
  - TODO
version_added: 1.0.0
extends_documentation_fragment: []
# TODO provide fragment for server_instance
#  - mynamespace.rhsso_automation_capabilities.server_instance
seealso: []

options:
  datadir:
    description:
      - Path to directory with dataThe.
    type: str
    required: true
  realm:
    description:
      - Name of realm to load.
    type: str
    required: true
  server_instance:
    description: TODO
    type: dict
    required: true
notes:
  - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Import one realm
  mynamespace.rhsso_automation_capabilities.import_realm:
    datadir: test/data/kcfetcher-0.0.4
    realm: ci0-realm
    server_instance:
      url: "https://172.17.0.2:8443"
      username: admin
      password: admin
"""


RETURN = r"""
records:
  description:
    - TODO what to return?
  returned: success
  type: list
  sample:
    - some_key: some_value
"""

import os
from ansible.module_utils.basic import AnsibleModule
from kcapi import Keycloak, OpenID
from kcloader.resource import RealmResource, SingleCustomAuthenticationResource, IdentityProviderManager

# from ..module_utils import errors, arguments


def get_kc(server_instance):
    token = OpenID.createAdminClient(server_instance["username"], server_instance["password"], url=server_instance["url"]).getToken()
    keycloak_api = Keycloak(token, server_instance["url"])
    master_realm = keycloak_api.admin()
    return keycloak_api, master_realm


def run(module):
    datadir = module.params["datadir"]
    realm_name = module.params["realm"]
    server_instance = module.params["server_instance"]
    keycloak_api, master_realm = get_kc(server_instance)

    # load realm
    realm_filepath = os.path.join(datadir, f"{realm_name}/{realm_name}.json")  # often correct
    realm_res = RealmResource({
        'path': realm_filepath,
        # 'name': '',
        # 'id': 'realm',
        'keycloak_api': keycloak_api,
        'realm': realm_name,
    })
    state = realm_res.publish(minimal_representation=True)

    # TODO load auth flows and roles, then
    # load all auth flows
    auth_flow_filepaths = glob(os.path.join(datadir, f"{realm_name}/authentication/flows/*/*.json"))
    for auth_flow_filepath in auth_flow_filepaths:
        auth_flow_res = SingleCustomAuthenticationResource({
            'path': auth_flow_filepath,
            # 'name': 'authentication',
            # 'id': 'alias',
            'keycloak_api': keycloak_api,
            'realm': realm_name,
        })
        creation_state = auth_flow_res.publish()
        state = state and creation_state

    # load identity providers
    idp_manager = IdentityProviderManager(keycloak_api, realm_name, datadir)
    creation_state = idp_manager.publish()

    module.warn("returned changed/created/deleted status describes only IdentityProviders")
    return creation_state, "TODO-some-data"


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            # arguments.get_spec("server_instance"),
            server_instance=dict(
                type="dict",
            ),
            datadir=dict(
                type="str",
            ),
            realm=dict(
                type="str",
            ),
        ),
    )

    try:
        changed, record = run(module)
        module.exit_json(changed=changed, record=record)
    # except errors.KeycloakError as e:
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
