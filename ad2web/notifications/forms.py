# -*- coding: utf-8 -*-

import json
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList,
        SelectMultipleField)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)
from wtforms.widgets import ListWidget, CheckboxInput
from .constants import (NOTIFICATIONS, NOTIFICATION_TYPES, SUBSCRIPTIONS, DEFAULT_SUBSCRIPTIONS, EMAIL, GOOGLETALK)
from .models import NotificationSetting

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=True)
    option_widget = CheckboxInput()

class CreateNotificationForm(Form):
    type = SelectField(u'Notification Type', choices=[nt for t, nt in NOTIFICATIONS.iteritems()])

    submit = SubmitField(u'Next')

class EditNotificationMessageForm(Form):
    id = HiddenField()
    text = TextAreaField(u'Message Text', [Required(), Length(max=255)])

    submit = SubmitField(u'Save')

class EditNotificationForm(Form):
    type = HiddenField()
    description = TextField(u'Description', [Required(), Length(max=255)], description=u'Brief description of this notification')
    subscriptions = MultiCheckboxField(u'Notify on..', choices=[(str(k), v) for k, v in SUBSCRIPTIONS.iteritems()])

    def populate_settings(self, settings, id=None):
        settings['subscriptions'] = self.populate_setting('subscriptions', json.dumps({str(k): True for k in self.subscriptions.data}))

    def populate_from_settings(self, id):
        subscriptions = self.populate_from_setting(id, 'subscriptions')
        if subscriptions:
            self.subscriptions.data = [k if v == True else False for k, v in json.loads(subscriptions).iteritems()]

    def populate_setting(self, name, value, id=None):
        if id is not None:
            setting = NotificationSetting.query.filter_by(notification_id=id, name=name).first()
        else:
            setting = NotificationSetting(name=name)

        setting.value = value

        return setting

    def populate_from_setting(self, id, name, default=None):
        ret = default

        setting = NotificationSetting.query.filter_by(notification_id=id, name=name).first()
        if setting is not None:
            ret = setting.value

        return ret

class EmailNotificationForm(EditNotificationForm):
    source = TextField(u'Source Address', [Required(), Length(max=255)], default='root@localhost', description=u'Emails will originate from this address')
    destination = TextField(u'Destination Address', [Required(), Length(max=255)], description=u'Emails will be sent to this address')

    server = TextField(u'Email Server', [Required(), Length(max=255)], default='localhost', description=u'Email server to use for sending')
    username = TextField(u'Username', [Optional(), Length(max=255)], description=u'Optional: Username for the email server')
    password = PasswordField(u'Password', [Optional(), Length(max=255)], description=u'Optional: Password for the email server')

    submit = SubmitField(u'Save')

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)

        settings['source'] = self.populate_setting('source', self.source.data)
        settings['destination'] = self.populate_setting('destination', self.destination.data)
        settings['server'] = self.populate_setting('server', self.server.data)
        settings['username'] = self.populate_setting('username', self.username.data)
        settings['password'] = self.populate_setting('password', self.password.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)

        self.source.data = self.populate_from_setting(id, 'source')
        self.destination.data = self.populate_from_setting(id, 'destination')
        self.server.data = self.populate_from_setting(id, 'server')
        self.username.data = self.populate_from_setting(id, 'username')
        self.password.data = self.populate_from_setting(id, 'password')

class GoogleTalkNotificationForm(EditNotificationForm):
    source = TextField(u'Source Address', [Required(), Length(max=255)], default='root@localhost', description=u'Messages will originate from this address')
    password = PasswordField(u'Password', [Required(), Length(max=255)], description=u'Password for the source account')
    destination = TextField(u'Destination Address', [Required(), Length(max=255)], description=u'Messages will be sent to this address')

    submit = SubmitField(u'Save')

    def populate_settings(self, settings, id=None):
        settings['source'] = self.populate_setting('source', self.source.data)
        settings['password'] = self.populate_setting('password', self.password.data)
        settings['destination'] = self.populate_setting('destination', self.destination.data)

    def populate_from_settings(self, id):
        self.source.data = self.populate_from_setting(id, 'source')
        self.password.data = self.populate_from_setting(id, 'password')
        self.destination.data = self.populate_from_setting(id, 'destination')
