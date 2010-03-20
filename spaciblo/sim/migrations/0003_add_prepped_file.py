
from south.db import db
from django.db import models
from spaciblo.sim.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Asset.prepped_file'
        db.add_column('sim_asset', 'prepped_file', orm['sim.asset:prepped_file'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Asset.prepped_file'
        db.delete_column('sim_asset', 'prepped_file')
        
    
    
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
        'sim.asset': {
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prepped_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'})
        },
        'sim.simulatorpoolregistration': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'port': ('django.db.models.fields.IntegerField', [], {})
        },
        'sim.space': {
            'default_body': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Template']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_guests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'scene_document': ('django.db.models.fields.TextField', [], {'default': '\'{"type":"Scene", "thing":{"type":"Thing", "attributes": { "id":"0" } } }\''}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '1000', 'db_index': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'admin_only'", 'max_length': '20'})
        },
        'sim.spacemember': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_editor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Space']"})
        },
        'sim.template': {
            'assets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sim.Asset']", 'null': 'True', 'blank': 'True'}),
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sim.TemplateChild']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'A Template'", 'max_length': '1000'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'seat_orientation': ('django.db.models.fields.CharField', [], {'default': "'1,0,0,0'", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'seat_position': ('django.db.models.fields.CharField', [], {'default': "'0,0,0'", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'settings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sim.TemplateSetting']", 'null': 'True', 'blank': 'True'})
        },
        'sim.templateasset': {
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Asset']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'templateassets'", 'to': "orm['sim.Template']"})
        },
        'sim.templatechild': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orientation': ('django.db.models.fields.CharField', [], {'default': "'1,0,0,0'", 'max_length': '1000'}),
            'position': ('django.db.models.fields.CharField', [], {'default': "'0,0,0'", 'max_length': '1000'}),
            'settings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sim.TemplateSetting']", 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sim.Template']"})
        },
        'sim.templatesetting': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['sim']
