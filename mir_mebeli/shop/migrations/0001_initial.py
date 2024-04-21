# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('shop_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['shop.Category'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, db_index=True)),
            ('name_in_xls', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('basic', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=80, null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(default='', max_length=250)),
            ('count_all', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('count_online', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True)),
            ('search_title', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('search_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True, null=True, blank=True)),
            ('not_on_main_page_carousel', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('never_available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('shop', ['Category'])

        # Adding model 'Good'
        db.create_table('shop_good', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='goods', null=True, to=orm['shop.Collection'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('display_name', self.gf('django.db.models.fields.CharField')(default='', max_length=80, blank=True)),
            ('articul', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('producer', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=0)),
            ('sale', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('dims', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('special', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('is_available', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('shop', ['Good'])

        # Adding M2M table for field categories on 'Good'
        db.create_table('shop_good_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('good', models.ForeignKey(orm['shop.good'], null=False)),
            ('category', models.ForeignKey(orm['shop.category'], null=False))
        ))
        db.create_unique('shop_good_categories', ['good_id', 'category_id'])

        # Adding model 'Color'
        db.create_table('shop_color', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Color'])

        # Adding model 'Colour'
        db.create_table('shop_colour', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('good', self.gf('django.db.models.fields.related.ForeignKey')(related_name='colour', to=orm['shop.Good'])),
            ('first_color', self.gf('django.db.models.fields.related.ForeignKey')(related_name='first_color', to=orm['shop.Color'])),
            ('second_color', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='second_color', null=True, to=orm['shop.Color'])),
        ))
        db.send_create_signal('shop', ['Colour'])

        # Adding model 'Shop'
        db.create_table('shop_shop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('name_in_xls', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, null=True, blank=True)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('online', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('shop', ['Shop'])

        # Adding model 'Buyer'
        db.create_table('shop_buyer', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('mid_name', self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['shop.City'], null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('subscribe', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('shop', ['Buyer'])

        # Adding model 'City'
        db.create_table('shop_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('ordering', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['City'])

        # Adding model 'Delivery'
        db.create_table('shop_delivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.City'])),
            ('method', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('price', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ordering', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Delivery'])

        # Adding unique constraint on 'Delivery', fields ['city', 'method']
        db.create_unique('shop_delivery', ['city_id', 'method'])

        # Adding model 'Order'
        db.create_table('shop_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('buyer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Buyer'])),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('mid_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('payment_method', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('sum', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=0)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['shop.Delivery'], null=True)),
            ('cancel_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('cancel_reason', self.gf('django.db.models.fields.TextField')(default='', max_length=500, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('change_date', self.gf('django.db.models.fields.DateField')(auto_now=True, null=True, blank=True)),
            ('done_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('pay_till', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Order'])

        # Adding model 'OrderedItem'
        db.create_table('shop_ordereditem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['shop.Order'])),
            ('good', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Good'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=0)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('shop', ['OrderedItem'])

        # Adding model 'OrderPayment'
        db.create_table('shop_orderpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Order'])),
            ('operation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['psbank.Payment'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('shop', ['OrderPayment'])

        # Adding model 'Collection'
        db.create_table('shop_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('name_in_xls', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('good', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='is_collection', null=True, blank=True, to=orm['shop.Good'])),
        ))
        db.send_create_signal('shop', ['Collection'])

        # Adding model 'Sale'
        db.create_table('shop_sale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sum', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=0)),
            ('sale', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('shop', ['Sale'])

        # Adding model 'Discount'
        db.create_table('shop_discount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sum', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=0)),
            ('sale', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('shop', ['Discount'])

        # Adding model 'ImportGoods'
        db.create_table('shop_importgoods', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('log', self.gf('django.db.models.fields.TextField')(default='', max_length=5000, blank=True)),
        ))
        db.send_create_signal('shop', ['ImportGoods'])

        # Adding model 'ImportPrices'
        db.create_table('shop_importprices', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('log', self.gf('django.db.models.fields.TextField')(default='', max_length=5000, blank=True)),
            ('is_robot', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('shop', ['ImportPrices'])

        # Adding model 'Available'
        db.create_table('shop_available', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shop'])),
            ('good', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Good'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=0)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('sale', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('shop', ['Available'])

        # Adding model 'PriceRequest'
        db.create_table('shop_pricerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('subscribe', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('good', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Good'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('status_changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['PriceRequest'])

        # Adding model 'PhoneCallRequest'
        db.create_table('shop_phonecallrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('status_changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['PhoneCallRequest'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('shop_category')

        # Deleting model 'Good'
        db.delete_table('shop_good')

        # Removing M2M table for field categories on 'Good'
        db.delete_table('shop_good_categories')

        # Deleting model 'Color'
        db.delete_table('shop_color')

        # Deleting model 'Colour'
        db.delete_table('shop_colour')

        # Deleting model 'Shop'
        db.delete_table('shop_shop')

        # Deleting model 'Buyer'
        db.delete_table('shop_buyer')

        # Deleting model 'City'
        db.delete_table('shop_city')

        # Deleting model 'Delivery'
        db.delete_table('shop_delivery')

        # Removing unique constraint on 'Delivery', fields ['city', 'method']
        db.delete_unique('shop_delivery', ['city_id', 'method'])

        # Deleting model 'Order'
        db.delete_table('shop_order')

        # Deleting model 'OrderedItem'
        db.delete_table('shop_ordereditem')

        # Deleting model 'OrderPayment'
        db.delete_table('shop_orderpayment')

        # Deleting model 'Collection'
        db.delete_table('shop_collection')

        # Deleting model 'Sale'
        db.delete_table('shop_sale')

        # Deleting model 'Discount'
        db.delete_table('shop_discount')

        # Deleting model 'ImportGoods'
        db.delete_table('shop_importgoods')

        # Deleting model 'ImportPrices'
        db.delete_table('shop_importprices')

        # Deleting model 'Available'
        db.delete_table('shop_available')

        # Deleting model 'PriceRequest'
        db.delete_table('shop_pricerequest')

        # Deleting model 'PhoneCallRequest'
        db.delete_table('shop_phonecallrequest')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'psbank.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'authcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'backref': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '250'}),
            'card': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "u'RUB'", 'max_length': '3'}),
            'desc': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'int_ref': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'merch_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'merchant': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'p_sign': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'rc': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rctext': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'result': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rrn': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'blank': 'True'}),
            'terminal': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'trtype': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'shop.available': {
            'Meta': {'object_name': 'Available'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'good': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Good']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '0'}),
            'sale': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shop']"})
        },
        'shop.buyer': {
            'Meta': {'object_name': 'Buyer', '_ormbases': ['auth.User']},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['shop.City']", 'null': 'True', 'blank': 'True'}),
            'mid_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'subscribe': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'shop.category': {
            'Meta': {'object_name': 'Category'},
            'basic': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'count_all': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'count_online': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'db_index': 'True'}),
            'name_in_xls': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'never_available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'not_on_main_page_carousel': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['shop.Category']", 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'search_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'search_title': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'shop.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'shop.collection': {
            'Meta': {'object_name': 'Collection'},
            'good': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'is_collection'", 'null': 'True', 'blank': 'True', 'to': "orm['shop.Good']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'name_in_xls': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'shop.color': {
            'Meta': {'object_name': 'Color'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'shop.colour': {
            'Meta': {'object_name': 'Colour'},
            'first_color': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'first_color'", 'to': "orm['shop.Color']"}),
            'good': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'colour'", 'to': "orm['shop.Good']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second_color': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'second_color'", 'null': 'True', 'to': "orm['shop.Color']"})
        },
        'shop.delivery': {
            'Meta': {'unique_together': "(('city', 'method'),)", 'object_name': 'Delivery'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'shop.discount': {
            'Meta': {'object_name': 'Discount'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sale': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'sum': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '0'})
        },
        'shop.good': {
            'Meta': {'object_name': 'Good'},
            'articul': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'goods'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['shop.Category']"}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'goods'", 'null': 'True', 'to': "orm['shop.Collection']"}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dims': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_available': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '0'}),
            'producer': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sale': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'special': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'shop.importgoods': {
            'Meta': {'object_name': 'ImportGoods'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '5000', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'shop.importprices': {
            'Meta': {'object_name': 'ImportPrices'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_robot': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '5000', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'shop.order': {
            'Meta': {'object_name': 'Order'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'buyer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Buyer']"}),
            'cancel_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'cancel_reason': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'change_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['shop.Delivery']", 'null': 'True'}),
            'done_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'mid_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'pay_till': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'sum': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '0'})
        },
        'shop.ordereditem': {
            'Meta': {'object_name': 'OrderedItem'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'good': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Good']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['shop.Order']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '0'})
        },
        'shop.orderpayment': {
            'Meta': {'object_name': 'OrderPayment'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['psbank.Payment']"}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Order']"})
        },
        'shop.phonecallrequest': {
            'Meta': {'object_name': 'PhoneCallRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'status_changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'shop.pricerequest': {
            'Meta': {'object_name': 'PriceRequest'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'good': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Good']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'status_changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subscribe': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'shop.sale': {
            'Meta': {'object_name': 'Sale'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sale': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'sum': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '0'})
        },
        'shop.shop': {
            'Meta': {'object_name': 'Shop'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'name_in_xls': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['shop']
