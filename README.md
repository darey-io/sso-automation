# About

Collection allows transferring configuration data between RH SSO servers.
Steps to use:
- a source SSO server is configured using web GUI
- `kcfetcher` command creates a data dump to local filesystem
- the collection takes data dump and applies changes to destination SSO server
- the destination SSO server should now have same configuration as source SSO server

# Installation

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install ansible_core==2.14.1  # also more recent versions should work
pip install -r requirements.txt

# this will install package with kcfetcher command
pip install -r requirements-dev.txt
```

# Import data

A sample dataset is already available in `tests/data/kcfetcher-0.0.6/`.
It was created with kcfetcher tag 0.0.6.

A sample playbook to import this dataset is at `playbooks/test_import_realm.yml`.
The destination SSO IP and credentials are hardcoded in it - change them if needed.
IP is assumed to be 172.17.0.2.

Start test SSO server. We can use `sso74-openshift-rhel8:7.4` or `keycloak:9.0.3` docker image.

```shell
# docker run -e SSO_ADMIN_USERNAME=admin -e SSO_ADMIN_PASSWORD=admin -it registry.redhat.io/rh-sso-7/sso74-openshift-rhel8:7.4
docker run -it -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:9.0.3
# check that SSO server IP is 172.17.0.2

ansible-playbook playbooks/test_import_realm.yml
```

This will create a realm named "ci0-realm" at https://172.17.0.2:8443.

# Export data

You can now modify some realm settings at https://172.17.0.2:8443.
Changes can be saved to local disk using `kcfetcher`.

```shell
# configuration with environment variables will be changed in future
export KEYCLOAK_API_CA_BUNDLE=
export SSO_API_URL=https://172.17.0.2:8443/
export SSO_API_USERNAME=admin
export SSO_API_PASSWORD=admin

# output directory path is currently hardcoded
kcfetcher
# a directory output/kcfetcher was created
```