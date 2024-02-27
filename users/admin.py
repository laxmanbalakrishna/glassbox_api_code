from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from users.models import User, UserType, Industry, CompanyType, Business, Verification

class CustomUserAdmin(UserAdmin):
    ordering = ('first_name',)

    list_display = ('id', 'first_name', 'last_name', 'email','user_type',
                    'phone_number','pan_number','masked_pan','business','created_by','is_premium_user', 'is_active', 'is_staff')
    list_display_links = ('id', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff',)

    fieldsets = (
        (None, {'fields': ('password', 'email', 'pan_number', 'masked_pan')}),
        ('Personal info', {'fields': ( 'first_name', 'last_name', 'phone_number')}),
        ('User Details', {'fields': ('is_active','business', 'created_by','is_premium_user','user_type','is_staff', 'groups')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','pan_number', 'first_name', 'last_name',
                       'phone_number', 'password1', 'password2', 'business','created_by'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserType)
admin.site.register(CompanyType)
admin.site.register(Industry)
admin.site.register(Business)
admin.site.register(Verification)