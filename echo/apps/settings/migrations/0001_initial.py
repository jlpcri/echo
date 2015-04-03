# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Server'
        db.create_table(u'settings_server', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('address', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('account', self.gf('django.db.models.fields.TextField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'settings', ['Server'])

        # Adding model 'PreprodServer'
        db.create_table(u'settings_preprodserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('address', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('account', self.gf('django.db.models.fields.TextField')()),
            ('application_type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'settings', ['PreprodServer'])


    def backwards(self, orm):
        # Deleting model 'Server'
        db.delete_table(u'settings_server')

        # Deleting model 'PreprodServer'
        db.delete_table(u'settings_preprodserver')


    models = {
        u'settings.preprodserver': {
            'Meta': {'object_name': 'PreprodServer'},
            'account': ('django.db.models.fields.TextField', [], {}),
            'address': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'application_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'settings.server': {
            'Meta': {'object_name': 'Server'},
            'account': ('django.db.models.fields.TextField', [], {}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['settings']