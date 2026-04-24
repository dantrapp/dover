from django.db import models


class BenchmarkHire(models.Model):
    source_row_index = models.PositiveIntegerField(unique=True)
    role_title = models.CharField(max_length=255)
    normalized_role_title = models.CharField(max_length=255, db_index=True)
    function = models.CharField(max_length=64, db_index=True)
    seniority = models.CharField(max_length=64, blank=True)
    cost_per_hire_usd = models.PositiveIntegerField()
    cost_per_hire_display = models.CharField(max_length=16)
    company_stage = models.CharField(max_length=32, db_index=True)
    stage_rank = models.PositiveSmallIntegerField(db_index=True)
    company_location = models.CharField(max_length=255)
    normalized_city = models.CharField(max_length=128, blank=True, db_index=True)
    normalized_region = models.CharField(max_length=128, blank=True, db_index=True)
    geo_cluster = models.CharField(max_length=64, blank=True, db_index=True)
    notable_investors = models.TextField(blank=True)
    recruiter_name = models.CharField(max_length=128)

    class Meta:
        ordering = ['source_row_index']

    def __str__(self):
        return f"{self.role_title} ({self.company_stage}, {self.company_location})"


class RecruiterProfile(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    years_experience = models.PositiveSmallIntegerField()
    headline = models.CharField(max_length=255)
    bio = models.TextField()
    functions = models.JSONField(default=list)
    stage_focus = models.JSONField(default=list)
    geo_focus = models.JSONField(default=list)
    hiring_priority_focus = models.JSONField(default=list)
    sample_role = models.CharField(max_length=255)
    sample_cost_display = models.CharField(max_length=16)
    sample_stage = models.CharField(max_length=32)
    accent = models.CharField(max_length=32, default='forest')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
