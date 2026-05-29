# AzBusiness/models.py
from django.db import models
from django.conf import settings

class BusinessProfile(models.Model):
    # Links the business record directly to the Business Owner User account
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='business_profile'
    )
    company_name = models.CharField(max_length=255)
    business_email = models.EmailField(unique=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name