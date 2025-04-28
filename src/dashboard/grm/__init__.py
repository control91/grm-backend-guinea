from django.utils.translation import gettext_lazy as _

CHOICE_FACILITATOR = 'facilitator'
CHOICE_ANONYMOUS = 'anonymous'
CHOICE_CONTACT = 'contact'
MEDIUM_CHOICES = [
    (CHOICE_ANONYMOUS, _('Rester anonyme')),
    (CHOICE_FACILITATOR, _('Recevoir les mises à jour de l\'animateur')),
    (CHOICE_CONTACT, _('Recevoir directement les mises à jour')),
]

CHOICE_EMAIL = 'email'
CHOICE_PHONE = 'phone_number'
CHOICE_WHATSAPP = 'whatsapp'
CONTACT_CHOICES = [
    ('', ''),
    (CHOICE_EMAIL, _('Email')),
    (CHOICE_PHONE, _('Numéro de téléphone')),
    (CHOICE_WHATSAPP, 'Whatsapp'),
]

CHOICE_1 = 1
CHOICE_2 = 2
CHOICE_3 = 3
CITIZEN_TYPE_CHOICES = [
    (CHOICE_1, _('Gardez le nom confidentiel. Seule la personne résolvant le problème verra le nom.')),
    (CHOICE_2, _('Il s\'agit d\'un dépôt individuel au nom de quelqu\'un d\'autre.')),
    (CHOICE_3, _('Il s\'agit d\'une organisation qui dépose au nom de quelqu\'un d\'autre.')),
]

CHOICE_0_OR_1_LABEL = _('Complainant')
CITIZEN_TYPE_CHOICES_ALT = [
    (0, CHOICE_0_OR_1_LABEL),
    (CHOICE_1, CHOICE_0_OR_1_LABEL),
    (CHOICE_2, _('Citizen on behalf of others')),
    (CHOICE_3, _('Organization on behalf of others')),
]

CHOICE_MALE = "Masculin"
CHOICE_FEMALE = "Feminin"

GENDER_CHOICES = [
    ('', ''),
    (CHOICE_MALE, _(CHOICE_MALE)),
    (CHOICE_FEMALE, _(CHOICE_FEMALE)),
]
