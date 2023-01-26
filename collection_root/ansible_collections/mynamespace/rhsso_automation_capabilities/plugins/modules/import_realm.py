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
from kcloader.resource import \
    RealmResource, \
    AuthenticationFlowManager, \
    IdentityProviderManager, \
    ClientManager, \
    RealmRoleManager, \
    UserFederationManager, \
    ClientScopeManager, \
    DefaultDefaultClientScopeManager, \
    DefaultOptionalClientScopeManager
from kcloader.resource.group_resource import GroupManager


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

    realm_filepath = os.path.join(datadir, f"{realm_name}/{realm_name}.json")  # often correct
    realm_res = RealmResource({
        'path': realm_filepath,
        # 'name': '',
        # 'id': 'realm',
        'keycloak_api': keycloak_api,
        'realm': realm_name,
    })
    # create realm before mangers
    states = list()
    states.append(realm_res.publish(minimal_representation=True))

    auth_manager = AuthenticationFlowManager(keycloak_api, realm_name, datadir)
    idp_manager = IdentityProviderManager(keycloak_api, realm_name, datadir)
    uf_manager = UserFederationManager(keycloak_api, realm_name, datadir)
    group_manager = GroupManager(keycloak_api, realm_name, datadir)
    client_manager = ClientManager(keycloak_api, realm_name, datadir)
    realm_role_manager = RealmRoleManager(keycloak_api, realm_name, datadir)
    client_scope_manager = ClientScopeManager(keycloak_api, realm_name, datadir)
    default_default_client_scope_manager = DefaultDefaultClientScopeManager(keycloak_api, realm_name, datadir)
    default_optional_client_scope_manager = DefaultOptionalClientScopeManager(keycloak_api, realm_name, datadir)

    # --------------------------------------------
    # Pass 1 - create minimal realm, simple roles, etc
    states.append(auth_manager.publish())
    states.append(idp_manager.publish())
    states.append(uf_manager.publish())
    states.append(realm_role_manager.publish(include_composite=False))
    states.append(client_manager.publish(include_composite=False))
    states.append(group_manager.publish())
    # new client_scopes are not yet created, we need setup_new_links=False.
    states.append(default_default_client_scope_manager.publish(setup_new_links=False))
    states.append(default_optional_client_scope_manager.publish(setup_new_links=False))
    states.append(client_scope_manager.publish(include_scope_mappings=False))

    # ---------------------------------
    # Pass 2, resolve circular dependencies
    states.append(realm_res.publish(minimal_representation=True))
    states.append(realm_role_manager.publish(include_composite=True))
    states.append(client_manager.publish(include_composite=True))
    states.append(default_default_client_scope_manager.publish(setup_new_links=True))
    states.append(default_optional_client_scope_manager.publish(setup_new_links=True))
    states.append(client_scope_manager.publish(include_scope_mappings=True))

    return any(states), "TODO-some-data"


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
