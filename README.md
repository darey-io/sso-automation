
This currently supports RHSSO version 7.4

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

# This will install package with the kcfetcher library
pip install -r requirements-kf-fetcher.txt
```

# Import data

A sample dataset is already available in `tests/data/kcfetcher-<VERSION-NUMBER>/`.


The playbook to import this dataset into another RHSSO server is at `main.yaml`.


Start test SSO server. We can use `sso74-openshift-rhel8:7.4` or `keycloak:9.0.3` docker image.

Another alternative is to use a sample developer sandbox in openshift. You can register for a sandbox here 
```
https://console-openshift-console.apps.sandbox-m3.1530.p1.openshiftapps.com/
```

If you are using an openshift environment, the server endpoint will look similar to 

```
https://sso-dre002ng-dev.apps.sandbox-m3.1530.p1.openshiftapps.com
```
So simply replace 172.17.0.2 with the openshift endpoint during your tests.

Using docker instead, follow below instructions

```shell
# docker run -e SSO_ADMIN_USERNAME=admin -e SSO_ADMIN_PASSWORD=admin -it registry.redhat.io/rh-sso-7/sso74-openshift-rhel8:7.4
docker run -it -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:9.0.3
# check that SSO server IP is 172.17.0.2

```

# Install the Ansible collection
- ansible-galaxy collection build - This will generate the tar.gz file
- Install the collection with below command
    ```
    ansible-galaxy collection install mynamespace-rhsso_automation_capabilities-0.0.1.tar.gz
    ```

# Run Ansible

```shell
ansible-playbook main.yml

This will create a realm named "ci0-realm" at https://172.17.0.2:8443.

You can now modify some realm settings at https://172.17.0.2:8443.
Changes can be saved to local disk using `kcfetcher`.
```
