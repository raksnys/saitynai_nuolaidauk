from django.db import models

# Create your models here.

DEBT_TYPE = [
    ('fuel', 'Fuel'),
    ('money', 'Money'),
    ('bottles', 'Bottles'),
]

class Debt(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='debts')
    type = models.CharField(max_length=20, choices=DEBT_TYPE)
    amount = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    debtee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='debtee')
    is_confirmed = models.BooleanField(default=False)

class Drinking(models.Model):
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField('users.User', through='Participation')
    raw_or_coctails = models.BooleanField(default=True)
    location = models.ForeignKey('Locations', on_delete=models.CASCADE, null=True, blank=True, related_name='drinkings')

class Participation(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    drinking = models.ForeignKey('Drinking', on_delete=models.CASCADE)
    popped_the_bottle = models.BooleanField(default=False)
    bought_the_bottle = models.BooleanField(default=False)
    bought_snacks = models.BooleanField(default=False)
    drinked_first = models.BooleanField(default=False)
    
class Drinks(models.Model):
    name = models.CharField(max_length=255)
    volume_ml = models.FloatField()
    alcohol_percentage = models.FloatField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Locations(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)