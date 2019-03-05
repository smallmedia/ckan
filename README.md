
# Small Media CKAN Notes


1. `vagrant up` should get you a working local install
2. `vagrant ssh` to login to the vagrant machine
3. From the `/vagrant` directory (which is the default), run `paster serve /etc/ckan/default/ckan.ini`
4. Visit the app at http://192.168.33.10:5000/

## Working with paster on local

* To create a sysadmin account, run: `paster sysadmin add myusername -c /etc/ckan/default/ckan.ini`
* If you build a new extension remember to run the installation commands before adding it to plugins list in the config file:
  1. `. /home/vagrant/bin/activate` (local) or `. /webapps/iod-ckan/bin/activate` (staging/live)
  2. `cd ckanext-nameofextension/`
  3. `python setup.py develop`
* To edit your local config file: `sudo vi /etc/ckan/default/ckan.ini`. On staging/live machine exit from CKAN user first

## Deploy to iod-ckan-live

1. Go to the deploy folder: `cd deploy`
2. Run the deploy script: `ansible-playbook live.yml`

## Working with paster on iod-ckan-live

* Login to `iod-ckan-live`:  `ssh iod-ckan-live.aws.smallmedia.org.uk`
* Switch to the CKAN user: `sudo su - iod-ckan`
* `paster <command> /etc/ckan/default/ckan.ini`
* If server not running: `sudo service supervisor restart` (exit from CKAN user first)

## Update View Tracking

If you already deployed the ckan, set `ckan.tracking_enabled` to true in the `[app:main]` section of your CKAN configuration file (e.g `/etc/ckan/default/ckan.ini`):
```
[app:main]
ckan.tracking_enabled = true
```
Otherwise the ckan config file will be created based on `ckan.ini.j2` witch the `tracking_enabled` is true by default.

To update tracking summary: `paster tracking update -c /etc/ckan/default/ckan.ini`

To rebuild the serch index: `paster search-index rebuild -c /etc/ckan/default/ckan.ini`

Also it's possible to create a cron job to do the updating and rebuilding periodically. run `crontab -e` and add this line to current cron file:
```
@hourly /usr/lib/ckan/bin/paster --plugin=ckan tracking update -c /etc/ckan/default/ckan.ini && /usr/lib/ckan/bin/paster --plugin=ckan search-index rebuild -r -c /etc/ckan/default/ckan.ini
```
Be sure that the path of the paster is correct.
The `@hourly` can be replaced with `@daily`, `@weekly` or `@monthly`.


## Showcase
To install showcase:
```
cd ckanext-showcase
python setup.py develop
pip install -r dev-requirements.txt
```

Showcase will create it's tables. CKAN timeout when Showcase is enabled for the first time. to solve the problem you need to disable all plugins.
Edit the local config file: `sudo vi /etc/ckan/default/ckan.ini` and comment out the `ckan.plugins` line. then add this line instead: `ckan.plugins = showcase` and run the CKAN.
After creating the tables, enable all plugins again.
