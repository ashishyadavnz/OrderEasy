from django.http import HttpResponse
from django.apps import apps
from django.contrib import admin
from django.db.models import CharField, TextField, ForeignKey, BooleanField, ManyToManyField, PositiveBigIntegerField, BigIntegerField, ImageField
from django.contrib.sessions.models import Session
from django.db.migrations.recorder import MigrationRecorder
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from restaurant.models import *
import csv

class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    fields = ('user', 'address')
    raw_id_fields = ['user']
    classes = ['collapse']

class FoodItemInline(admin.StackedInline):
    model = FoodItem
    extra = 0
    fields = ('restaurant', 'cuisine','title','category', 'price', 'start', 'available', 'keyword', 'meta_title', 'meta_description', 'status')
    raw_id_fields = ['restaurant', 'cuisine', 'category']
    classes = ['collapse']

INLINE_CONFIG = {
    User: [AddressInline],
    Cuisine: [FoodItemInline],
    Restaurant: [FoodItemInline],
}

class ListAdminMixin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        exclude_fields = {'track', 'utrack', 'locate', 'password', 'id', 'last_login', 'date_joined'}
        readonly_field = {'id', 'timestamp', 'utimestamp', 'track', 'utrack', 'locate'}
        priority_fields = {'title', 'name', 'username'}
        fk_priority = {'user',}
        st_priority = {'status',}
        priority = []
        fkpriority_fields = []
        stpriority = []
        char_fields = []
        fk_fields = []
        boolean_fields = []
        other_fields = []
        status_fields = []
        search_fields = []
        list_filters = []
        raw_id_fields = []
        readonly_fields = []
        radio_fields = {}

        for field in model._meta.fields:
            if field.name in readonly_field:
                readonly_fields.append(field.name)
            if field.name in exclude_fields:
                continue
            
            if isinstance(field, TextField) or isinstance(field, ManyToManyField):
                continue
            
            if isinstance(field, CharField):
                if field.choices:
                    if field.name in st_priority:
                        stpriority.append(field.name)
                    else:
                        status_fields.append(field.name)
                    list_filters.append(field.name)
                    radio_fields[field.name] = admin.HORIZONTAL
                else:
                    if field.name in priority_fields:
                        priority.append(field.name)
                    else:
                        method_name = f'get_{field.name}_short'
                        def truncation_method(self, obj, field_name=field.name):
                            value = getattr(obj, field_name)
                            if value and len(value) > 20:
                                return value[:20] + '...'
                            return value
                        truncation_method.short_description = field.verbose_name
                        setattr(self.__class__, method_name, truncation_method)
                        char_fields.append(method_name)
                    search_fields.append(field.name)
            elif isinstance(field, ImageField):
                def image_tag(self, obj, field_name=field.name):
                    image_url = getattr(obj, field_name)
                    if image_url:
                        return mark_safe('<img src="%s" width="50" height="50"/>' % (image_url.url))
                    else:
                        return '-'
                method_name = f'get_{field.name}_short'
                image_tag.short_description = field.verbose_name
                image_tag.allow_tags = True
                setattr(self.__class__, method_name, image_tag)
                char_fields.append(method_name)
            elif isinstance(field, ForeignKey):
                if field.name in fk_priority:
                    fkpriority_fields.append(field.name)
                else:
                    fk_fields.append(field.name)
                search_fields.append(f"{field.name}__id")
                raw_id_fields.append(field.name)
            elif isinstance(field, BooleanField):
                boolean_fields.append(field.name)
                list_filters.append(field.name)
            elif isinstance(field, PositiveBigIntegerField) or isinstance(field, BigIntegerField):
                other_fields.append(field.name)
                search_fields.append(field.name)
            else:
                other_fields.append(field.name)
        
        self.list_display = priority + fkpriority_fields + fk_fields + char_fields + boolean_fields + other_fields + status_fields + stpriority
        self.search_fields = search_fields
        self.list_filter = list_filters
        self.raw_id_fields = raw_id_fields
        self.readonly_fields = readonly_fields
        self.radio_fields = radio_fields

        if model == Session:
            self.list_display.append('_session_data')
  
        super().__init__(model, admin_site)

        self.inlines = INLINE_CONFIG.get(model, [])
    
    def _session_data(self, obj):
        return obj.get_decoded()
    _session_data.short_description = 'Session Data'
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        exclude_fields = ['password', 'timestamp', 'utimestamp', 'track', 'utrack', 'locate', 'identifier','date_joined','last_login']
        field_names = [field.name for field in meta.fields if field.name not in exclude_fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field_name in field_names:
                row.append(getattr(obj, field_name))
            writer.writerow(row)
        return response
    export_as_csv.short_description = "Export Selected to CSV"
    
    actions = ['export_as_csv']

class CustomUserAdmin(ListAdminMixin, UserAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

    add_fieldsets = (
		(None, {
            'classes': ('wide', 'extrapretty'),
            'fields': ('username', 'password1', 'password2','mobile','email' ),
        }),
	)

    fieldsets = [
        ('Personal info', {
            'fields': (
                'referrer', 'country', 'state', 'city', 'mobile', 'gender', 'dob', 'image', 'address', 'postcode', 'identifier', 'otp', 'source', 'status'
            ),
        }),
        ('Permissions', {
            'classes': ('collapse', ),
            'fields': ('notification', 'multilogin', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'classes': ('collapse', ),
            'fields': ('last_login', 'date_joined'),
        }),
        ('Location', {
            'classes': ('collapse', ),
            'fields': ('latitude','longitude')
        }),
        ('Track Record', {
            'classes': ('collapse', ),
            'fields': ('timestamp', 'utimestamp', 'track', 'utrack', 'locate'),
        }),
    ]

models = apps.get_models()

for model in models:
    if model == User:
        admin_class = CustomUserAdmin
    else:
        admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass

class MigrationRecorderAdmin(ListAdminMixin, admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'content',)
    search_fields = ('name',)
    readonly_fields = ('track', 'utrack',)


admin.site.register(MigrationRecorder.Migration, MigrationRecorderAdmin)
