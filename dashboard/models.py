from django.db import models


class ActivityLog(models.Model):
    entity_id = models.IntegerField()
    entity_class = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=255)
    action = models.TextField()
    data = models.TextField(blank=True, null=True)
    is_status_updated = models.IntegerField(blank=True, null=True)
    updated_by = models.IntegerField()
    created_at = models.DateTimeField()
    status = models.IntegerField()
    company_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'activity_log'


class Teams(models.Model):
    lead_id = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.IntegerField()
    company_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'teams'


class User(models.Model):
    username = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=32)
    password_hash = models.CharField(max_length=255)
    password_reset_token = models.CharField(unique=True, max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255)
    status = models.SmallIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    mobile = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    role = models.IntegerField()
    user_type = models.IntegerField()
    entity_id = models.IntegerField(blank=True, null=True)
    pin = models.IntegerField(blank=True, null=True)
    client_list = models.TextField(blank=True, null=True)
    company_id = models.IntegerField()
    google_auth_migration_out = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user'
