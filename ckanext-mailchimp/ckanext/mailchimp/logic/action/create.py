from ckan.logic.action.create import user_create
from ckan.common import config

from ckanext.mailchimp.logic.mailchimp import MailChimpClient
from ckanext.mailchimp.util import name_splitter


def mailchimp_user_create(context, data_dict):
    user = user_create(context, data_dict)

    if user is not None and data_dict is not None and data_dict.get('newsletter', None) == 'subscribed':
        split_names = name_splitter(data_dict.get('fullname', data_dict.get('name', None)))
        mailchimp_add_subscriber(split_names[0], split_names[1], data_dict.get('email', None), tags=["NAP-user"])
    return user


def mailchimp_add_subscriber(firstname, lastname, email, tags=None):
    """
    if user is not already in mailchimp add user to mailchimp

    :param firstname: first name of the subscriber
    :param lastname: last name of the subscriber
    :param email: email of the subscriber
    :param tags: array of tags for the subscriber -> https://mailchimp.com/help/manage-tags/
    :return: True if successful, False if not
    """
    mailchimp_client = MailChimpClient(
        api_key=config.get('ckan.mailchimp.api_key', None),
        base_url=config.get('ckan.mailchimp.base_url', None),
        member_list_id=config.get('ckan.mailchimp.member_list_id', None)
    )

    subscriber = mailchimp_client.find_subscriber_by_email(email)
    if subscriber is None:
        success, message = mailchimp_client.create_new_subscriber(
            firstname,
            lastname,
            email,
            tags
        )
        return success, message
    else:
        subscriber_tags = [tag.get('name', '') for tag in subscriber.get('tags', [])]
        merged_tags = subscriber_tags + tags if tags else subscriber_tags
        success = mailchimp_client.update_subscriber_tags(subscriber.get('id', None), merged_tags)
        if success:
            return False, "ALREADY_SUBSCRIBED"
        else:
            return False, "ERROR_UPDATE"
