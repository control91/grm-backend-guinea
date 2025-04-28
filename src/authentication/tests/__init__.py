import factory
from django.utils import timezone

from authentication import ADL, MAJOR
from client import get_db

tzinfo = timezone.get_current_timezone()


class Attachment:
    def __init__(self, name, url, url_local, file_id, uploaded):
        self.name = name
        self.url = url
        self.url_local = url_local
        self.file_id = file_id
        self.uploaded = uploaded

    def __str__(self):
        return self.name


class AttachmentFactory(factory.Factory):
    class Meta:
        model = Attachment

    name = factory.Faker('file_name')
    url = ""
    url_local = factory.Faker('file_path')
    file_id = factory.Faker('uuid4')
    uploaded = False


class Task:
    def __init__(self, ordinal, doc_type, title, status, notes, due_at, attachments):
        self.ordinal = ordinal
        self.doc_type = doc_type
        self.title = title
        self.status = status
        self.notes = notes
        self.due_at = due_at
        self.attachments = attachments

    def __str__(self):
        return self.title


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    doc_type = 'list_activity'
    title = factory.Faker('text')
    status = factory.Iterator(['not-stated', 'in-progress', 'completed'], cycle=True, getter=lambda s: s[0])
    notes = factory.Faker('paragraph', nb_sentences=3)
    due_at = factory.Faker('iso8601', tzinfo=tzinfo)
    attachments = factory.List([factory.SubFactory(AttachmentFactory) for _ in range(3)])


class Phase:
    def __init__(self, ordinal, title, opened_at, closed_at, due_at, tasks):
        self.ordinal = ordinal
        self.title = title
        self.opened_at = opened_at
        self.closed_at = closed_at
        self.due_at = due_at
        self.tasks = tasks

    def __str__(self):
        return self.title


class PhaseFactory(factory.Factory):
    class Meta:
        model = Phase

    title = factory.Faker('text')
    opened_at = factory.Faker('iso8601', tzinfo=tzinfo)
    closed_at = factory.Faker('iso8601', tzinfo=tzinfo)
    due_at = factory.Faker('iso8601', tzinfo=tzinfo)
    tasks = factory.List([factory.SubFactory(TaskFactory, ordinal=ordinal) for ordinal in range(3)])


class CouchdbUser:
    def __init__(self, email, password, name, doc_type, is_active, photo, phone, birthday, data, doc):
        self.email = email
        self.password = password
        self.name = name
        self.doc_type = doc_type
        self.is_active = is_active
        self.photo = photo
        self.phone = phone
        self.birthday = birthday
        self.data = data
        self.doc = doc

    def __str__(self):
        return f'{self.email} {self.doc_type}'


class CouchdbUserFactory(factory.Factory):
    class Meta:
        model = CouchdbUser

    email = factory.Faker('email')
    password = ''
    name = factory.Faker('name')
    doc_type = factory.Iterator([ADL, MAJOR])
    is_active = True
    photo = factory.Faker('image_url')
    phone = factory.Faker('phone_number')
    birthday = factory.Faker('date_of_birth')

    @factory.lazy_attribute
    def data(self):
        return {
            'type': self.doc_type,
            'representative': {
                'email': self.email,
                'password': self.password,
                'name': self.name,
                'is_active': self.is_active,
                'photo': self.photo,
                'phone': self.phone,
                'birthday': str(self.birthday)
            }
        }

    @factory.lazy_attribute
    def doc(self):
        eadl_db = get_db()
        return eadl_db.create_document(self.data)


class CouchdbADL(CouchdbUser):
    def __init__(self, email, password, name, doc_type, is_active, photo, phone, birthday, phases, data, doc):
        CouchdbUser.__init__(self, email, password, name, doc_type, is_active, photo, phone, birthday, data, doc)
        self.phases = phases

    def __str__(self):
        return f'{self.email} {self.doc_type}'


class CouchdbADLFactory(CouchdbUserFactory):
    class Meta:
        model = CouchdbADL

    phases = factory.List([factory.SubFactory(PhaseFactory, ordinal=ordinal) for ordinal in range(3)])

    @factory.lazy_attribute
    def doc(self):
        self.data['type'] = ADL
        self.data['phases'] = [
            {
                'ordinal': phase.ordinal,
                'title': phase.title,
                'opened_at': phase.opened_at,
                'closed_at': phase.closed_at,
                'due_at': phase.due_at,
                'tasks': [
                    {
                        'ordinal': task.ordinal,
                        'type': task.doc_type,
                        'title': task.title,
                        'status': task.status,
                        'notes': task.notes,
                        'due_at': task.due_at,
                        'attachments': [
                            {
                                'name': attachment.name,
                                "url": attachment.url,
                                "url_local": attachment.url_local,
                                "id": attachment.file_id,
                                "uploaded": attachment.uploaded,
                            } for attachment in task.attachments
                        ],
                    } for task in phase.tasks
                ],
            } for phase in self.phases
        ]
        eadl_db = get_db()
        return eadl_db.create_document(self.data)


class CouchdbMajorFactory(CouchdbUserFactory):

    @factory.lazy_attribute
    def doc(self):
        self.data['type'] = MAJOR
        eadl_db = get_db()
        return eadl_db.create_document(self.data)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'authentication.User'

    email = factory.Faker('email')
    phone_number = factory.Faker('phone_number')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class Issue:
    def __init__(self, doc_id, attachments, doc_type, data, doc):
        self.doc_id = doc_id
        self.attachments = attachments
        self.doc_type = doc_type
        self.data = data
        self.doc = doc
        self.doc = doc

    def __str__(self):
        return f'{self.doc_id} {self.doc_type}'


class IssueFactory(factory.Factory):
    class Meta:
        model = Issue

    doc_id = factory.Sequence(int)
    attachments = factory.List([factory.SubFactory(AttachmentFactory) for _ in range(3)])
    doc_type = 'issue'

    @factory.lazy_attribute
    def data(self):
        return {
            'type': self.doc_type,
            'id': self.doc_id
        }

    @factory.lazy_attribute
    def doc(self):
        self.data['attachments'] = [
            {
                'name': attachment.name,
                "url": attachment.url,
                "url_local": attachment.url_local,
                "id": attachment.file_id,
                "uploaded": attachment.uploaded,
            } for attachment in self.attachments
        ]
        eadl_db = get_db()
        return eadl_db.create_document(self.data)
