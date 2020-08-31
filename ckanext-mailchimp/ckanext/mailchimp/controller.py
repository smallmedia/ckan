# coding=utf-8
from ckan.common import request
from ckan.controllers.home import HomeController
from ckan.lib.helpers import flash_success, flash_error, lang
from validate_email import validate_email

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email

flash_messages = {
    "SUCCESS": {
        "en": u"A confirmation email was sent to you to verify your email address. Please check your spam folder if "
              u"you did not receive this email. If the problem persists, contact us at <a "
              u"href='mailto:contact@transportdata.be'>contact@transportdata.be</a>",
        "nl": u"Een bevestigingsmail werd verstuurd naar uw email adres. Controleer uw spam folder indien u deze niet "
              u"ontvangen heeft. Bij verdere problemen kan u ons contacteren via <a "
              u"href='mailto:contact@transportdata.be'>contact@transportdata.be</a> ",
        "fr": u"Nous vous avons envoyé un mail de confirmation. Si vous ne le voyez pas, vérifiez dans vos spam s’il "
              u"ne s’y trouve pas. Si le problème persiste, prenez contact avec nous via <a "
              u"href='mailto:contact@transportdata.be'>contact@transportdata.be</a> ",
        "de": u"Eine E-Mail wurde an Sie gesendet, um Ihre E-Mail-Adresse zu bestätigen. Bitte überprüfen Sie auch "
              u"Ihren Spam-Ordner wenn Sie diese E-Mail nicht erhalten haben. Wenn das Problem weiterhin besteht, "
              u"kontaktiere uns per <a href='mailto:contact@transportdata.be'>contact@transportdata.be</a>  ",
        "fa_IR": u"برای تایید آدرس ایمیل خود یک ایمیل تاییدیه به شما ارسال شده است."
              u"اگر این ایمیل را دریافت نکردید، لطفاً بخش اسپم ایمیل خود را بررسی کنید."
              u"اگر همچنان تکرار شد، با ما به آدرس: contact@iranopendata.org تماس بگیرید."
    },
    "ERROR_ADD": {
        "en": u"An error occurred while adding you to the mailing list.",
        "nl": u"Er is een fout opgetreden bij het toevoegen aan de mailinglijst.",
        "fr": u"Une erreur s'est produite lors de votre ajout à la liste de diffusion.",
        "de": u"Beim Hinzufügen zur Mailingliste ist ein Fehler aufgetreten.",
        "fa_IR": u"هنگام افزودن ایمیل شما به فهرست ایمیل‌ها، خطایی رخ داد."
    },
    "ALREADY_SUBSCRIBED": {
        "en": u"You already subscribed to the newsletter.",
        "nl": u"U bent reeds ingeschreven op de mailinglijst.",
        "fr": u"Vous êtes déjà abonné à la newsletter.",
        "de": u"Sie haben den Newsletter bereits abonniert.",
        "fa_IR": u"شما قبلا در خبرنامه عضو شده‌اید."
    },
    "ERROR_UPDATE": {
        "en": u"An error occurred while updating your information.",
        "nl": u"Er is een fout opgetreden tijdens het updaten van uw informatie",
        "fr": u"Une erreur s'est produite lors de la mise à jour de vos informations.",
        "de": u"Beim Aktualisieren Ihrer Informationen ist ein Fehler aufgetreten.",
        "fa_IR": u"در هنگام به‌روزرسانی اطلاعات‌تان، خطایی رخ داده است."
    },
    "ERROR_NOT_VALID": {
        "en": u"Please provide a valid email address!",
        "nl": u"Gelieve een geldig email adres op te geven!",
        "fr": u"Veuillez fournir une adresse email valide!",
        "de": u"Bitte geben Sie eine gültige E-Mail Adresse an!",
        "fa_IR": u"لطفا آدرس ایمیل معتبری ارائه کنید."
    }
}


def translate_flash_message(msg_key, lang):
    msg = flash_messages.get(msg_key, {})
    if lang in msg:
        msg_translated = msg.get(lang, "An error occurred")
    else:
        msg_translated = msg.get("en", "An error occurred")
    return msg_translated


class NewsletterController(HomeController):

    def subscribe(self):
        email = request.params.get('email', None)
        if email and validate_email(email):
            names = name_from_email(email)
            success, msg_key = mailchimp_add_subscriber(names[0], names[1], email, tags=["Mailinglist-user"])
            if success:
                flash_success(translate_flash_message(msg_key, lang()), allow_html=True)
            else:
                flash_error(translate_flash_message(msg_key, lang()), allow_html=True)
        else:
            flash_error(translate_flash_message("ERROR_NOT_VALID", lang()), allow_html=True)
        return super(NewsletterController, self).index()
