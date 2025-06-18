from django.db import models
from datetime import date
class RightbizListing(models.Model):
    id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=500, null=True)
    extra_info = models.TextField(blank=True, null=True)
    type = models.CharField(blank=True, null=True)
    scraped_on = models.DateField(default=date.today)

    class Meta:
        db_table = 'rightbiz_listing_table'


class BusinessForSaleListing(models.Model):
    id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=500, null=True)
    type = models.CharField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
    scraped_on = models.DateField(default=date.today)

    class Meta:
        db_table = 'bussiness_for_sale_listing'