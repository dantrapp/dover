import csv

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
    help = 'Load the Dover cost-per-hire CSV and recruiter seed data into the local database.'

    def handle(self, *args, **options):
        dataset_path = settings.PLANNER_DATASET_PATH
        BenchmarkHire.objects.all().delete()

        with dataset_path.open(newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            hires = []
            for index, row in enumerate(reader, start=1):
                location = normalize_location(row['Company Location'])
                stage = normalize_stage(row['Company Stage'])
                hires.append(
                    BenchmarkHire(
                        source_row_index=index,
                        role_title=row['Position'],
                        normalized_role_title=normalize_role_title(row['Position']),
                        function=infer_function(row['Position']),
                        seniority=infer_seniority(row['Position']),
                        cost_per_hire_usd=parse_cost_to_usd(row['Cost Per Hire']),
                        cost_per_hire_display=row['Cost Per Hire'],
                        company_stage=stage,
                        stage_rank=stage_rank(stage),
                        company_location=row['Company Location'],
                        normalized_city=location['city'],
                        normalized_region=location['region'],
                        geo_cluster=location['cluster'],
                        notable_investors=row['Notable Investor(s)'],
                        recruiter_name=row['Recruiter Name'],
                    )
                )
        BenchmarkHire.objects.bulk_create(hires, batch_size=250)

        RecruiterProfile.objects.all().delete()
        RecruiterProfile.objects.bulk_create([RecruiterProfile(**profile) for profile in RECRUITER_SEED])

        self.stdout.write(self.style.SUCCESS(f'Loaded {len(hires)} hires and {len(RECRUITER_SEED)} recruiter profiles.'))
