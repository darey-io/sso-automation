import os
import json

from ansible.module_utils.basic import AnsibleModule
from kcapi import OpenID, Keycloak
from kcapi.rest.crud import KeycloakCRUD


def main():
    argument_spec = {
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str", "no_log": True},
        "source_data_path": {"required": True, "type": "str" },
        "target_realm": {"required": True, "type": "str" },
        "target_kc": {"required": True, "type": "str" },
        "import": {"required": True, "type": "list" },
    }

    module = AnsibleModule(argument_spec=argument_spec)

    user =  module.params["user"]
    password =  module.params["password"]
    src = module.params["source_data_path"]
    target_realm =  module.params["target_realm"]
    target_kc =  module.params["target_kc"]
    import_items =  module.params["import"]

    


    messages = []

    rd = {
        "changed": False,
        "messages": messages
    }


    token = OpenID.createAdminClient(user, password, target_kc).getToken()
    kc = Keycloak(token, target_kc)

    os.chdir(src)

    # create realm first
    try:
        kc.admin().create({"enabled": "true", "id": target_realm, "realm": target_realm})
        messages.append(f"SUCCESS: realm '{target_realm}' successfully installed.")
    except:
        pass

    if "groups" in import_items:
        os.chdir("groups")
        groups_json_filenames = os.listdir()
        if groups_json_filenames:
            group_names = [x.split(".")[0] for x in groups_json_filenames]
        
        if group_names:
            groups = kc.build('groups', target_realm)
            for group in group_names:
                try:
                    groups.create({"name": group}).isOk()
                    messages.append(f"SUCCESS: group '{group}' successfully installed.")
                    rd["changed"] = True
                except Exception as e:
                    pass

        os.chdir(src)


    if "roles" in import_items:
        os.chdir("roles")
        roles_json_filenames = os.listdir()
        if roles_json_filenames:
            role_names = [x.split(".")[0] for x in roles_json_filenames]
        
        if role_names:
            roles = kc.build('roles', target_realm)
            for role in role_names:
                try:
                    roles.create({"name": role}).isOk()
                    messages.append(f"SUCCESS: role '{role}' successfully installed.")
                    rd["changed"] = True
                except Exception as e:
                    # messages.append(f"WARNING: not able to install role '{role}'!")
                    pass

        os.chdir(src)

    if "clients" in import_items:
        os.chdir("clients")

        client_names = []
        for folder in os.listdir():
            if os.path.isdir(folder):
                client = os.listdir(folder)
                client = [x.split(".")[0] for x in client if x.endswith("json")]
                client_names += client

        if client_names:
            for client_name in client_names:
                client = {
                    "enabled": True,
                    "attributes": {},
                    "redirectUris": [],
                    "clientId": client_name,
                    "protocol": "openid-connect", 
                    "directAccessGrantsEnabled": True
                }    

                clients = kc.build('clients', target_realm)   
                try:
                    clients.create(client).isOk()
                    messages.append(f"SUCCESS: client '{client_name}' successfully installed.")
                    rd["changed"] = True
                except Exception as e:
                    # messages.append(f"WARNING: not able to install client '{client_name}'!")
                    pass
        os.chdir(src)

    module.exit_json(**rd)


if __name__ == '__main__':
    main()