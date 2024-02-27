from django.db import models
import uuid
import jsonfield
from users.models import User,Business
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone

from django.core.validators import MaxValueValidator, MinValueValidator
PERCENTAGE_CHOICES = (
    (0, "100%"),
    (1, "90%"),
    (2, "75%"),
    (3, "50%"),
    (4, "25%"),
    (5, "0%"),
)
REACHABILITY_CHOICES = (
    (0, "Yes"),
    (1, "Yes with multiple attempts"),
    (2, "Difficult"),
    (3,"No")
)
CAPITAL_ASSET_CHOICES = (
    (0, "Yes"),
    (1, "Moderate"),
    (2, "No")
)
SCORE_CHOICES = (
    (10, "Excellent"),
    (9, "Good"),
    (8, "Average"),
    (7, "Service Delay"),
    (6, "Lack of Post-Sale Support"),
    (5, "Market Disruption/Dispute/UnderCutting "),
    (4, "Payment Delay"),
    (3, "Non-Delivery After Payment"),
    (2, "Payment Defaul"),
    (1, "Fraudulent Activity")
)
REASON_CHOICES = (
    ('NOT_HAVING_ANY_TRANS',  'I am not having any transaction'),
    ('HAVE_PENDING_CREDIT_NOTES',  'I have pending credit notes'),
    ('ALREADY_MADE_THE_PAYMENT',  'I already made the payment'),
    ('OTHERS', 'Others'),
)

TOTAL_OUTSTANDING_CHOICES = (
    (0, "0"),
    (1, "<2 Lakh"),
    (2, "2-5 Lakh"),
    (3, "5-10 Lakh"),
    (4, "10-20 Lakh"),
    (5, "20-50 Lakh"),
    (6, "50-1 Cr"),
    (7,">1 Cr")
)
DSO_CHOICES = (
    (0,"0 Days"),
    (1, "30 Days"),
    (2, "60 Days"),
    (3, "90 Days"),
    (4, "180 Days"),
    (5, "365 Days"),
    (6, "730 Days")

)
# CAPITAL_CHOICES = (
#     (0, "Both are Good"),
#     (1, "Capital is good and Assest is not good"),
#     (2, "Assest is good and capital is not good "),
#     (3, "Both are not Good")
# )
TRANSACTION_PAID_ONTIME_CHOICES = (
    (0, "1 - 5"),
    (1, "6 - 10"),
    (2, "11 - 15"),
    (3, "16 - 25"),
    (4, "25 +")
)
class MyPartner(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          serialize=False, verbose_name='ID')
    is_business_exists = models.BooleanField(default=False)
    business_partner_main = models.ForeignKey(User, on_delete=models.CASCADE, related_name="main_partner")
    business_partner_assoc = models.ForeignKey(User, on_delete=models.CASCADE, related_name="associated_partner")
    score = models.IntegerField(choices=SCORE_CHOICES)
    total_outstanding = models.IntegerField(choices=TOTAL_OUTSTANDING_CHOICES,default=0)
    on_time_Payment = models.IntegerField(
                  choices=PERCENTAGE_CHOICES,
                  blank=True,null=True)
    reachability = models.IntegerField(choices=REACHABILITY_CHOICES, null=True, blank=True)
    recovery_probability =  models.IntegerField(
                  choices=REACHABILITY_CHOICES, blank=True,null=True)
    known_since = models.DateField(blank=True, null=True)
    comments = models.CharField(max_length=2000, default='', blank=True, null=True)
    dso = models.IntegerField(choices=DSO_CHOICES, default=0)
    legal_proceedings = models.BooleanField(default=False)
    # capital = models.IntegerField(choices=CAPITAL_CHOICES, default=0)
    transaction_paid_ontime = models.IntegerField(choices=TRANSACTION_PAID_ONTIME_CHOICES, default=0)
    capital = models.IntegerField(choices=CAPITAL_ASSET_CHOICES, default=0)
    assets = models.IntegerField(choices=CAPITAL_ASSET_CHOICES, default=0)
    is_gst_paid = models.BooleanField(default=False)
    is_raised_dispute = models.BooleanField(default=False)
    pending_receivables = models.IntegerField(choices=TOTAL_OUTSTANDING_CHOICES,default=0)
    updated_on = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('-updated_on',)
        unique_together = ('business_partner_main', 'business_partner_assoc')

    def __str__(self):
        return f"{self.business_partner_main}_{self.business_partner_assoc}"

# class Ratings(models.Model):
#
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
#                           serialize=False, verbose_name='ID')
#     partner = models.ForeignKey(MyPartner, on_delete=models.CASCADE, related_name="partner")
#     score = models.IntegerField(choices=SCORE_CHOICES)
#     total_outstanding = models.IntegerField(choices=TOTAL_OUTSTANDING_CHOICES,default=0)
#     on_time_Payment = models.IntegerField(
#                   choices=PERCENTAGE_CHOICES,
#                   blank=True,null=True)
#     reachability = models.IntegerField(choices=REACHABILITY_CHOICES, null=True, blank=True)
#     recovery_probability =  models.IntegerField(
#                   choices=REACHABILITY_CHOICES, blank=True,null=True)
#     known_since = models.DateField(blank=True, null=True)
#     comments = models.CharField(max_length=2000, default='', blank=True, null=True)
#     dso = models.IntegerField(choices=DSO_CHOICES, default=0)
#     capital = models.IntegerField(choices=CAPITAL_CHOICES, default=0)
#     transaction_paid_ontime = models.IntegerField(choices=TRANSACTION_PAID_ONTIME_CHOICES, default=0)
#     capital = models.IntegerField(choices=CAPITAL_ASSET_CHOICES, default=0)
#     assets = models.IntegerField(choices=CAPITAL_ASSET_CHOICES, default=0)
#     is_gst_paid = models.BooleanField(default=False)
#     is_raised_dispute = models.BooleanField(default=False)
#     pending_receivables = models.IntegerField(default=0)
#     updated_on = models.DateTimeField(auto_now=True)
#
#
#     class Meta:
#         ordering = ('-updated_on',)
#         unique_together = ('business_partner_main', 'business_partner_assoc')
#
#     def __str__(self):
#         return f"{self.business_partner_main}_{self.business_partner_assoc}"


class ScoreDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pres_avg_score = models.FloatField(default=0)
    prev_avg_score = models.FloatField(default=0)
    raise_or_fall_percent = models.FloatField(default=0)
    is_raised = models.BooleanField(default=False)
    total_partners = models.IntegerField(default=0)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_on',)

    def __str__(self):
        return f"{self.user}_{self.pres_avg_score}_{self.prev_avg_score}"


class RaisedDisputes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="main_user")
    raised_on_user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name="associated_user")
    reason_option = models.CharField(choices=REASON_CHOICES, blank=True,null=True, max_length=100)
    reason = models.TextField(max_length=2000)
    response = models.TextField(max_length=2000, blank=True, null=True)
    raised_on = models.DateTimeField(blank=True, null=True)
    resolved_on = models.DateTimeField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)


    class Meta:
        ordering = ('-raised_on',)

    def __str__(self):
        return f"{self.user}_{self.raised_on_user}"

NOTIFICATION_TYPE_CHOICES = (
    (1, "Raised Dispute"),
    (2, "Myrating"),
    (3, "Others"))

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          serialize=False, verbose_name='ID')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPE_CHOICES)
    type_id = models.CharField(max_length=100)
    title = models.CharField(max_length=400)
    description = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"From {self.sender} to {self.recipient}-{self.notification_type}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

class Subscription(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    validity = models.IntegerField(default=1)
    description = models.JSONField(default=[])
    is_active = models.BooleanField(default=True)
    display_text = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name



class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='transactions', unique=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE,related_name='transactions')
    payment_amount = models.BigIntegerField()
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,related_name='transactions')
    transaction_id = models.CharField(max_length=255)
    is_success = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)

    def is_subscription_active(self):
        years = self.subscription.validity
        one_year_later = self.payment_date + timedelta(days=365 * years)

        # Check if the current date is before 'one_year_later'
        return timezone.now() < one_year_later

    def update_user_premium_status(self):
        user = self.user
        if Payments.objects.filter(user=user, is_success=True).exists():
            user.is_premium_user = True
        else:
            user.is_premium_user = False
        user.save()


    class Meta:
        ordering = ('-payment_date',)
    def __str__(self):
        return f"{self.user.first_name} - {self.business.name} : {self.transaction_id}"

@receiver(post_save, sender=Payments)
def update_user_premium_status(sender, instance, **kwargs):
    instance.update_user_premium_status()

class GSTinDetails(models.Model):
    incorporation_date = models.DateField()
    company = models.CharField(max_length=256)
    gstin = models.CharField(max_length=15,unique=True)
    state = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    business_name = models.CharField(max_length=500)
    fullname = models.CharField(max_length=200)
    industry = jsonfield.JSONField(default=[])

    def __str__(self):
        return f"{self.gstin}: {self.business_name}"


