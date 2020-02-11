from ckan.common import request
from ckan.controllers.home import HomeController
from ckan.lib.helpers import flash_success, flash_error

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email

from validate_email import validate_email


class NewsletterController(HomeController):

    def subscribe(self):
        email = request.params.get('email', None)
        if email and validate_email(email):
            names = name_from_email(email)
            success, msg = mailchimp_add_subscriber(names[0], names[1], email, tags=["Mailinglist-user"])
            if success:
                flash_success(msg)
            else:
                flash_error(msg)
        else:
            flash_error("Please provide a valid email address!")
        return super(NewsletterController, self).index()
