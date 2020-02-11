from ckan.common import config
from ckan.logic.action.update import user_update

from ckanext.mailchimp.logic.mailchimp import MailChimpClient
from ckanext.mailchimp.util import name_splitter


def mailchimp_user_update(context, data_dict):
    user = user_update(context, data_dict)
    mailchimp_client = MailChimpClient(
        api_key=config.get('ckan.mailchimp.api_key', None),
        base_url=config.get('ckan.mailchimp.base_url', None),
        member_list_id=config.get('ckan.mailchimp.member_list_id', None)
    )

    if user is not None and data_dict is not None:
        if data_dict.get('newsletter', None) == 'subscribed':
            # if user is not already in mailchimp add user to mailchimp
            if mailchimp_client.find_subscriber_by_email(data_dict.get('email', None)) is None:
                split_names = name_splitter(data_dict.get('fullname', data_dict.get('name', None)))
                mailchimp_client.create_new_subscriber(
                    split_names[0], split_names[1], data_dict.get('email', None), tags=["NAP-user"])
        elif data_dict.get('newsletter', None) is None or data_dict.get('newsletter', None) == '':
            # if user is already in mailchimp remove user from mailchimp
            if mailchimp_client.find_subscriber_by_email(data_dict.get('email', None)) is not None:
                mailchimp_client.delete_subscriber_by_email(data_dict.get('email', None))

    return user
