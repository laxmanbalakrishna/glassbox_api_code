from django.contrib import admin
from .models import MyPartner, ScoreDetails,RaisedDisputes, Notification,Payments,GSTinDetails,Subscription
# Register your models here.


class CustomPaymentModelAdmin(admin.ModelAdmin):
    readonly_fields = ('payment_date',)
    list_filter = ('is_success',)
    # fields = ( 'user', 'business', 'payment_amount', 'transaction_id',
    #                 'is_success', 'payment_date')

admin.site.register(MyPartner)
admin.site.register(ScoreDetails)
admin.site.register(RaisedDisputes)
admin.site.register(Notification)
admin.site.register(Payments, CustomPaymentModelAdmin)
admin.site.register(GSTinDetails)
admin.site.register(Subscription)

