
from south.db import db
from django.db import models
from spaciblo.person.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Photo'
        db.create_table('person_photo', (
            ('id', orm['person.Photo:id']),
            ('image', orm['person.Photo:image']),
            ('created', orm['person.Photo:created']),
        ))
        db.send_create_signal('person', ['Photo'])
        
        # Adding model 'InviteRequest'
        db.create_table('person_inviterequest', (
            ('id', orm['person.InviteRequest:id']),
            ('email', orm['person.InviteRequest:email']),
            ('created', orm['person.InviteRequest:created']),
        ))
        db.send_create_signal('person', ['InviteRequest'])
        
        # Adding model 'UserProfile'
        db.create_table('person_userprofile', (
            ('id', orm['person.UserProfile:id']),
            ('user', orm['person.UserProfile:user']),
            ('photo', orm['person.UserProfile:photo']),
            ('full_name', orm['person.UserProfile:full_name']),
            ('location', orm['person.UserProfile:location']),
            ('bio', orm['person.UserProfile:bio']),
            ('url', orm['person.UserProfile:url']),
            ('email_validated', orm['person.UserProfile:email_validated']),
        ))
        db.send_create_signal('person', ['UserProfile'])
        
        # Adding model 'Invite'
        db.create_table('person_invite', (
            ('id', orm['person.Invite:id']),
            ('secret', orm['person.Invite:secret']),
            ('sent_to', orm['person.Invite:sent_to']),
            ('used_by', orm['person.Invite:used_by']),
            ('created', orm['person.Invite:created']),
        ))
        db.send_create_signal('person', ['Invite'])
        
        # Adding ManyToManyField 'UserProfile.invites'
        db.create_table('person_userprofile_invites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm.UserProfile, null=False)),
            ('invite', models.ForeignKey(orm.Invite, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Photo'
        db.delete_table('person_photo')
        
        # Deleting model 'InviteRequest'
        db.delete_table('person_inviterequest')
        
        # Deleting model 'UserProfile'
        db.delete_table('person_userprofile')
        
        # Deleting model 'Invite'
        db.delete_table('person_invite')
        
        # Dropping ManyToManyField 'UserProfile.invites'
        db.delete_table('person_userprofile_invites')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'person.invite': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'default': "'DGzd8hfucWUCmLUEnSkx'", 'max_length': '1024'}),
            'sent_to': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'used_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'origin_invites'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'person.inviterequest': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'person.photo': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'person.userprofile': {
            'bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email_validated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['person.Invite']", 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['person.Photo']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['person']
