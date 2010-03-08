
from south.db import db
from django.db import models
from spaciblo.sim.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Space'
        db.create_table('sim_space', (
            ('id', orm['sim.Space:id']),
            ('name', orm['sim.Space:name']),
            ('slug', orm['sim.Space:slug']),
            ('state', orm['sim.Space:state']),
            ('max_guests', orm['sim.Space:max_guests']),
            ('scene_document', orm['sim.Space:scene_document']),
        ))
        db.send_create_signal('sim', ['Space'])
        
        # Adding model 'Asset'
        db.create_table('sim_asset', (
            ('id', orm['sim.Asset:id']),
            ('type', orm['sim.Asset:type']),
            ('file', orm['sim.Asset:file']),
        ))
        db.send_create_signal('sim', ['Asset'])
        
        # Adding model 'SpaceMember'
        db.create_table('sim_spacemember', (
            ('id', orm['sim.SpaceMember:id']),
            ('space', orm['sim.SpaceMember:space']),
            ('member', orm['sim.SpaceMember:member']),
            ('is_admin', orm['sim.SpaceMember:is_admin']),
            ('is_editor', orm['sim.SpaceMember:is_editor']),
        ))
        db.send_create_signal('sim', ['SpaceMember'])
        
        # Adding model 'Template'
        db.create_table('sim_template', (
            ('id', orm['sim.Template:id']),
            ('name', orm['sim.Template:name']),
            ('owner', orm['sim.Template:owner']),
            ('last_updated', orm['sim.Template:last_updated']),
            ('seat_position', orm['sim.Template:seat_position']),
            ('seat_orientation', orm['sim.Template:seat_orientation']),
        ))
        db.send_create_signal('sim', ['Template'])
        
        # Adding model 'TemplateChild'
        db.create_table('sim_templatechild', (
            ('id', orm['sim.TemplateChild:id']),
            ('template', orm['sim.TemplateChild:template']),
            ('position', orm['sim.TemplateChild:position']),
            ('orientation', orm['sim.TemplateChild:orientation']),
        ))
        db.send_create_signal('sim', ['TemplateChild'])
        
        # Adding model 'TemplateSetting'
        db.create_table('sim_templatesetting', (
            ('id', orm['sim.TemplateSetting:id']),
            ('key', orm['sim.TemplateSetting:key']),
            ('value', orm['sim.TemplateSetting:value']),
        ))
        db.send_create_signal('sim', ['TemplateSetting'])
        
        # Adding model 'SimulatorPoolRegistration'
        db.create_table('sim_simulatorpoolregistration', (
            ('id', orm['sim.SimulatorPoolRegistration:id']),
            ('ip', orm['sim.SimulatorPoolRegistration:ip']),
            ('port', orm['sim.SimulatorPoolRegistration:port']),
        ))
        db.send_create_signal('sim', ['SimulatorPoolRegistration'])
        
        # Adding model 'TemplateAsset'
        db.create_table('sim_templateasset', (
            ('id', orm['sim.TemplateAsset:id']),
            ('template', orm['sim.TemplateAsset:template']),
            ('asset', orm['sim.TemplateAsset:asset']),
            ('key', orm['sim.TemplateAsset:key']),
        ))
        db.send_create_signal('sim', ['TemplateAsset'])
        
        # Adding ManyToManyField 'TemplateChild.settings'
        db.create_table('sim_templatechild_settings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('templatechild', models.ForeignKey(orm.TemplateChild, null=False)),
            ('templatesetting', models.ForeignKey(orm.TemplateSetting, null=False))
        ))
        
        # Adding ManyToManyField 'Template.settings'
        db.create_table('sim_template_settings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('template', models.ForeignKey(orm.Template, null=False)),
            ('templatesetting', models.ForeignKey(orm.TemplateSetting, null=False))
        ))
        
        # Adding ManyToManyField 'Template.children'
        db.create_table('sim_template_children', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('template', models.ForeignKey(orm.Template, null=False)),
            ('templatechild', models.ForeignKey(orm.TemplateChild, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Space'
        db.delete_table('sim_space')
        
        # Deleting model 'Asset'
        db.delete_table('sim_asset')
        
        # Deleting model 'SpaceMember'
        db.delete_table('sim_spacemember')
        
        # Deleting model 'Template'
        db.delete_table('sim_template')
        
        # Deleting model 'TemplateChild'
        db.delete_table('sim_templatechild')
        
        # Deleting model 'TemplateSetting'
        db.delete_table('sim_templatesetting')
        
        # Deleting model 'SimulatorPoolRegistration'
        db.delete_table('sim_simulatorpoolregistration')
        
        # Deleting model 'TemplateAsset'
        db.delete_table('sim_templateasset')
        
        # Dropping ManyToManyField 'TemplateChild.settings'
        db.delete_table('sim_templatechild_settings')
        
        # Dropping ManyToManyField 'Template.settings'
        db.delete_table('sim_template_settings')
        
        # Dropping ManyToManyField 'Template.children'
        db.delete_table('sim_template_children')
        
    
    
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
            'type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'})
        },
        'sim.simulatorpoolregistration': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'port': ('django.db.models.fields.IntegerField', [], {})
        },
        'sim.space': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_guests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'scene_document': ('django.db.models.fields.TextField', [], {'default': "'<scene />'"}),
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
