from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from authentication.models import get_government_worker_choices
from client import get_db
from dashboard.forms.widgets import RadioSelect
from dashboard.grm import CHOICE_CONTACT, CITIZEN_TYPE_CHOICES, CONTACT_CHOICES, GENDER_CHOICES, MEDIUM_CHOICES
from grm.utils import (
    get_administrative_region_choices, get_base_administrative_id, get_administrative_regions_by_level,
    get_issue_age_group_choices, get_issue_category_choices, get_issue_citizen_group_1_choices,
    get_issue_citizen_group_2_choices, get_issue_status_choices, get_issue_type_choices, get_region_choices,
    get_prefecture_choices
)

COUCHDB_GRM_DATABASE = settings.COUCHDB_GRM_DATABASE
MAX_LENGTH = 65000


class NewIssueContactForm(forms.Form):
    contact_medium = forms.ChoiceField(label=_('Comment le citoyen souhaite-t-il être contaté?'), widget=RadioSelect,
                                       choices=MEDIUM_CHOICES)
    contact_type = forms.ChoiceField(label='', required=False, choices=CONTACT_CHOICES)
    contact = forms.CharField(label='', required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)

        self.fields['contact'].widget.attrs["placeholder"] = _("SVP Entrer les informations de contact")

        document = grm_db[doc_id]
        if 'contact_medium' in document:
            self.fields['contact_medium'].initial = document['contact_medium']
            if document['contact_medium'] == CHOICE_CONTACT:
                if 'type' in document['contact_information'] and document['contact_information']['type']:
                    self.fields['contact_type'].initial = document['contact_information']['type']
                if 'contact' in document['contact_information'] and document['contact_information']['contact']:
                    self.fields['contact'].initial = document['contact_information']['contact']
            else:
                self.fields['contact'].widget.attrs["class"] = "hidden"


class NewIssuePersonForm(forms.Form):
    citizen = forms.CharField(label=_('Entrer le nom du citoyen'), required=False,
                              help_text=_('Ce champ n\'est pas obligatoire'))
    citizen_type = forms.ChoiceField(label=_(''), widget=RadioSelect, required=False,
                                     choices=CITIZEN_TYPE_CHOICES, help_text=_('Ce champ n\'est pas obligatoire'))
    citizen_age_group = forms.ChoiceField(label=_('Entrer la tranche d\'âge du citoyen'), required=False,
                                          help_text=_('Ce champ n\'est pas obligatoire'))
    gender = forms.ChoiceField(label=_('Choisissez le sexe'), required=False, help_text=_('Ce champ n\'est pas obligatoire'),
                               choices=GENDER_CHOICES)
    citizen_group_1 = forms.ChoiceField(label=_('Nationalité du citoyen'), required=False,
                                        help_text=_('Ce champ n\'est pas obligatoire'))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)

        citizen_age_groups = get_issue_age_group_choices(grm_db)
        self.fields['citizen_age_group'].widget.choices = citizen_age_groups
        self.fields['citizen_age_group'].choices = citizen_age_groups

        citizen_group_1_choices = get_issue_citizen_group_1_choices(grm_db)
        self.fields['citizen_group_1'].widget.choices = citizen_group_1_choices
        self.fields['citizen_group_1'].choices = citizen_group_1_choices

        document = grm_db[doc_id]

        if 'citizen' in document:
            self.fields['citizen'].initial = document['citizen']

        if 'citizen_type' in document:
            self.fields['citizen_type'].initial = document['citizen_type']

        if 'citizen_age_group' in document and document['citizen_age_group']:
            self.fields['citizen_age_group'].initial = document['citizen_age_group']['_id']

        if 'gender' in document:
            self.fields['gender'].initial = document['gender']

        if 'citizen_group_1' in document and document['citizen_group_1']:
            self.fields['citizen_group_1'].initial = document['citizen_group_1']['_id']


class NewIssueDetailsForm(forms.Form):
    intake_date = forms.DateTimeField(label=_('Date du jour'), input_formats=['%d/%m/%Y'],
                                      help_text="Date à laquelle le problème est enregistré")
    issue_date = forms.DateTimeField(label=_('Date du problème'), input_formats=['%d/%m/%Y'],
                                     help_text="Date à laquelle le problème est survenu")
    issue_type = forms.ChoiceField(label=_('Que signalez-vous'))
    category = forms.ChoiceField(label=_('Secteur d\'activité'))
    description = forms.CharField(label=_('Décrivez brièvement le problème'), max_length=2000, widget=forms.Textarea(
        attrs={'rows': '3', 'placeholder': _("S'il vous plaît decriver le problème")}))
    ongoing_issue = forms.BooleanField(label=_('Evénement en cours ou occurrences multiples'),
                                       widget=forms.CheckboxInput, required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)
        types = get_issue_type_choices(grm_db)
        self.fields['issue_type'].widget.choices = types
        self.fields['issue_type'].choices = types
        categories = get_issue_category_choices(grm_db)
        self.fields['category'].widget.choices = categories
        self.fields['category'].choices = categories

        self.fields['intake_date'].widget.attrs['class'] = self.fields['issue_date'].widget.attrs[
            'class'] = 'form-control datetimepicker-input'
        self.fields['intake_date'].widget.attrs['data-target'] = '#intake_date'
        self.fields['issue_date'].widget.attrs['data-target'] = '#issue_date'

        document = grm_db[doc_id]
        if 'description' in document and document['description']:
            self.fields['description'].initial = document['description']
        if 'issue_type' in document and document['issue_type']:
            self.fields['issue_type'].initial = document['issue_type']['_id']
        if 'category' in document and document['category']:
            self.fields['category'].initial = document['category']['_id']
        if 'ongoing_issue' in document:
            self.fields['ongoing_issue'].initial = document['ongoing_issue']


class NewIssueLocationForm(forms.Form):
    region = forms.ChoiceField()
    prefecture = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)

        regions = get_region_choices(grm_db)
        self.fields['region'].label = "Choisr la Région"
        self.fields['region'].choices = regions
        self.fields['region'].widget.choices = regions

        prefectures = get_prefecture_choices(grm_db)
        self.fields['prefecture'].label = "Choisir la prefecture"
        self.fields['prefecture'].choices = prefectures
        self.fields['prefecture'].widget.choices = prefectures

        #eadl_db = get_db()
        #label = get_administrative_regions_by_level(eadl_db)[0]['administrative_level'].title()


        #administrative_region_choices = get_administrative_region_choices(eadl_db)
        #self.fields['administrative_region'].widget.choices = administrative_region_choices
        #self.fields['administrative_region'].choices = administrative_region_choices
        #self.fields['administrative_region'].widget.attrs['class'] = "region"
        #self.fields['administrative_region_value'].widget.attrs['class'] = "hidden"

        #grm_db = get_db(COUCHDB_GRM_DATABASE)
        document = grm_db[doc_id]
        if 'region' in document and document['region']:
            self.fields['region'].initial = document['region']['_id']
        if 'prefecture' in document and document['prefecture']:
            self.fields['prefecture'].initial = document['prefecture']['_id']


class NewIssueConfirmForm(NewIssueLocationForm, NewIssueDetailsForm, NewIssuePersonForm, NewIssueContactForm):

    def __init__(self, *args, **kwargs):
        NewIssueContactForm.__init__(self, *args, **kwargs)
        NewIssuePersonForm.__init__(self, *args, **kwargs)
        NewIssueDetailsForm.__init__(self, *args, **kwargs)
        NewIssueLocationForm.__init__(self, *args, **kwargs)


class SearchIssueForm(forms.Form):
    start_date = forms.DateTimeField(label=_('Start Date'))
    end_date = forms.DateTimeField(label=_('End Date'))
    code = forms.CharField(label=_('ID Number / Access Code'))
    assigned_to = forms.ChoiceField()
    category = forms.ChoiceField()
    type = forms.ChoiceField()
    status = forms.ChoiceField()
    region = forms.ChoiceField()
    prefecture = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)

        self.fields['start_date'].widget.attrs['class'] = self.fields['end_date'].widget.attrs[
            'class'] = 'form-control datetimepicker-input'
        self.fields['start_date'].widget.attrs['data-target'] = '#start_date'
        self.fields['end_date'].widget.attrs['data-target'] = '#end_date'
        self.fields['assigned_to'].widget.choices = get_government_worker_choices()
        self.fields['category'].widget.choices = get_issue_category_choices(grm_db)
        self.fields['type'].widget.choices = get_issue_type_choices(grm_db)
        self.fields['status'].widget.choices = get_issue_status_choices(grm_db)
        self.fields['region'].widget.choices = get_region_choices(grm_db)

        #eadl_db = get_db()
        #label = get_administrative_regions_by_level(eadl_db)[0]['administrative_level'].title()
        #self.fields['administrative_region'].label = label
        #self.fields['administrative_region'].widget.choices = get_administrative_region_choices(eadl_db)
        #self.fields['administrative_region'].widget.attrs['class'] = "region"


class IssueDetailsForm(forms.Form):
    assignee = forms.ChoiceField(label=_('Assigned to'))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)
        self.fields['assignee'].widget.choices = get_government_worker_choices(False)

        document = grm_db[doc_id]
        self.fields['assignee'].initial = document['assignee']['id']


class IssueCommentForm(forms.Form):
    comment = forms.CharField(label='', max_length=MAX_LENGTH, widget=forms.Textarea(
        attrs={'rows': '3', 'placeholder': _('Add comment')}))


class IssueResearchResultForm(forms.Form):
    research_result = forms.CharField(label='', max_length=MAX_LENGTH, widget=forms.Textarea(attrs={'rows': '3'}))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)
        document = grm_db[doc_id]
        self.fields['research_result'].initial = document['research_result'] if 'research_result' in document else ''


class IssueRejectReasonForm(forms.Form):
    reject_reason = forms.CharField(label='', max_length=MAX_LENGTH, widget=forms.Textarea(attrs={'rows': '3'}))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        doc_id = initial.get('doc_id')
        super().__init__(*args, **kwargs)

        grm_db = get_db(COUCHDB_GRM_DATABASE)
        document = grm_db[doc_id]
        self.fields['reject_reason'].initial = document['reject_reason'] if 'reject_reason' in document else ''
