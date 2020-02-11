

=============
ckanext-mailchimp
=============

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!


------------
Requirements
------------

Tested with CKAN 2.8.3


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-mailchimp:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-mailchimp Python package into your virtual environment::

     pip install ckanext-mailchimp

3. Add ``mailchimp`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

The following config settings are required::

    ckan.mailchimp.api_key = <your mailchimp API key>
    ckan.mailchimp.base_url = <mailchimp base url for your account ex: https://us3.api.mailchimp.com/3.0>
    ckan.mailchimp.member_list_id = <list id of the member list, where new subscribers will be added>


------------------------
Development Installation
------------------------

To install ckanext-mailchimp for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/belgium-its-steering-committee/ckanext-mailchimp.git
    cd ckanext-mailchimp
    python setup.py develop
    pip install -r dev-requirements.txt

