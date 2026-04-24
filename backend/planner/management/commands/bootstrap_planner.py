import json

from django.conf import settings
from django.core.management.base import BaseCommand

from planner.data.recruiters import RECRUITER_SEED
from planner.models import BenchmarkHire, RecruiterProfile
from planner.services.normalize import (
    infer_function,
    infer_seniority,
    normalize_location,
    normalize_role_title,
    normalize_stage,
    parse_cost_to_usd,
    stage_rank,
)


class Command(BaseCommand):
    help = 'Load bundled benchmark hires and recruiter seed data into the local database.'

    def handle(self, *args, **options):
        dataset_path = settings.PLANNER_DATASET_PATH
        BenchmarkHire.objects.all().delete()

        with dataset_path.open(encoding='utf-8') as data_file:
            records = json.load(data_file)

        hires = []
        for index, row in enumerate(records, start=1):
            hires.append(
                BenchmarkHire(
                    source_row_index=row.get('sourceRowIndex', index),
                    role_title=row['roleTitle'],
                    normalized_role_title=row.get('normalizedRoleTitle')
                    or normalize_role_title(row['roleTitle']),
                    function=row.get('function') or infer_function(row['roleTitle']),
                    seniority=row.get('seniority') or infer_seniority(row['roleTitle']),
                    cost_per_hire_usd=row.get('costPerHireUsd')
                    or parse_cost_to_usd(row['costPerHireDisplay']),
                    cost_per_hire_display=row['costPerHireDisplay'],
                    company_stage=row.get('companyStage')
                    or normalize_stage(row.get('company_stage', 'Seed')),
                    stage_rank=row.get('stageRank')
                    or stage_rank(row.get('companyStage') or normalize_stage('Seed')),
                    company_location=row['companyLocation'],
                    normalized_city=row.get('normalizedCity', ''),
                    normalized_region=row.get('normalizedRegion', ''),
                    geo_cluster=row.get('geoCluster', ''),
                    notable_investors=row.get('notableInvestors', ''),
                    recruiter_name=row.get('recruiterName', ''),
                )
            )
        BenchmarkHire.objects.bulk_create(hires, batch_size=250)

        RecruiterProfile.objects.all().delete()
        RecruiterProfile.objects.bulk_create([RecruiterProfile(**profile) for profile in RECRUITER_SEED])

        self.stdout.write(self.style.SUCCESS(f'Loaded {len(hires)} hires and {len(RECRUITER_SEED)} recruiter profiles.'))
