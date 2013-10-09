# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CustomUser'
        db.create_table(u'bioface_customuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('sessionkey', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'bioface', ['CustomUser'])

        # Adding M2M table for field groups on 'CustomUser'
        db.create_table(u'bioface_customuser_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customuser', models.ForeignKey(orm[u'bioface.customuser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'bioface_customuser_groups', ['customuser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'CustomUser'
        db.create_table(u'bioface_customuser_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customuser', models.ForeignKey(orm[u'bioface.customuser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'bioface_customuser_user_permissions', ['customuser_id', 'permission_id'])

        # Adding model 'SavedQuery'
        db.create_table(u'bioface_savedquery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type_query', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='saved_queries', to=orm['bioface.CustomUser'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('organism_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('display_fields', self.gf('jsonfield.fields.JSONField')(default={})),
            ('attributes_list', self.gf('jsonfield.fields.JSONField')(default={})),
            ('filter_fields', self.gf('jsonfield.fields.JSONField')(default={})),
            ('query_str', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'bioface', ['SavedQuery'])

        # Adding model 'Download'
        db.create_table(u'bioface_download', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='downloads', to=orm['bioface.CustomUser'])),
            ('file_path', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True, recursive=True, match='*.zip', path='/Users/zavsnar/web-bioapp/source/../media/downloads/')),
            ('encoding', self.gf('django.db.models.fields.CharField')(default='utf-8', max_length='255')),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'bioface', ['Download'])


    def backwards(self, orm):
        # Deleting model 'CustomUser'
        db.delete_table(u'bioface_customuser')

        # Removing M2M table for field groups on 'CustomUser'
        db.delete_table('bioface_customuser_groups')

        # Removing M2M table for field user_permissions on 'CustomUser'
        db.delete_table('bioface_customuser_user_permissions')

        # Deleting model 'SavedQuery'
        db.delete_table(u'bioface_savedquery')

        # Deleting model 'Download'
        db.delete_table(u'bioface_download')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'bioface.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sessionkey': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'bioface.download': {
            'Meta': {'object_name': 'Download'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'encoding': ('django.db.models.fields.CharField', [], {'default': "'utf-8'", 'max_length': "'255'"}),
            'file_path': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'recursive': 'True', 'match': "'*.zip'", 'path': "'/Users/zavsnar/web-bioapp/source/../media/downloads/'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'downloads'", 'to': u"orm['bioface.CustomUser']"})
        },
        u'bioface.savedquery': {
            'Meta': {'object_name': 'SavedQuery'},
            'attributes_list': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'display_fields': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'filter_fields': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'organism_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'query_str': ('django.db.models.fields.TextField', [], {}),
            'type_query': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'saved_queries'", 'to': u"orm['bioface.CustomUser']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bioface']