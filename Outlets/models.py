# Outlets/models.py
from django.db import models
from django.conf import settings
from AzBusiness.models import BusinessProfile

class Outlet(models.Model):
    """Physical store branches belonging to a specific business corporation"""
    business = models.ForeignKey(
        BusinessProfile, 
        on_delete=models.CASCADE, 
        related_name='outlets'
    )
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.city}"


class OutletStaff(models.Model):
    """Assigns local operation managers and employees to an outlet branch"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='staff_assignment'
    )
    outlet = models.ForeignKey(
        Outlet, 
        on_delete=models.CASCADE, 
        related_name='staff_roster'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} mapped to {self.outlet.name}"