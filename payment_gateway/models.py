from django.db import models
from users.models import User
# Create your models here.
class Transaction(models.Model):
    payment_id = models.CharField(max_length=100,verbose_name="Payment Id")
    order_id = models.CharField(max_length=100,verbose_name="Order Id")
    signature = models.CharField(max_length=100,verbose_name="Signature")
    amount = models.IntegerField(verbose_name="Amount")
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True, max_length=500)
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.order_id}'
