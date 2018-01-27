import gspread
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import crypt
from django.core.management.base import BaseCommand
from django.utils import timezone
from moderation.settings import GOOGLE_DOCS_API_PRIVATE_KEY, GOOGLE_DOCS_API_SERVICE_ACCOUNT_EMAIL
from moderations.stats import get_leaderboard
from moderations.utils import timedelta_to_str


class Command(BaseCommand):

    def handle(self, *args, **options):

        def get_hour_fraction(timedelta_object):
            """
            Convert seconds to hour fraction. i. e. 1 hour and 60 seconds are 1,016~ hours.
            """
            hours = timedelta_object.days * 24
            seconds = timedelta_object.seconds
            fraction_of_hour = seconds / 3600.0

            return hours + fraction_of_hour

        leaderboard = get_leaderboard()

        avg_time_first_mod_rev_all = get_hour_fraction(leaderboard['avg']['all_time']['review'][0])
        avg_time_first_mod_rev_week = get_hour_fraction(leaderboard['avg']['seven_days']['review'][0])
        avg_time_mod_res_all = get_hour_fraction(leaderboard['avg']['all_time']['resolution'][0])
        avg_time_mod_res_week = get_hour_fraction(leaderboard['avg']['seven_days']['resolution'][0])

        signer = crypt.Signer.from_string(GOOGLE_DOCS_API_PRIVATE_KEY)
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials(GOOGLE_DOCS_API_SERVICE_ACCOUNT_EMAIL, signer, scopes=scope,
                                          private_key_id=None, client_id=None, user_agent=None,
                                          token_uri='https://www.googleapis.com/oauth2/v4/token',
                                          revoke_uri='https://accounts.google.com/o/oauth2/revoke')

        client = gspread.authorize(creds)

        sheet = client.open('cv-mod-stats').sheet1

        # The list of the values that stores the stats needed (should be in this order)
        timestamp = timezone.now().strftime('%Y-%m-%d')
        values = (timestamp,
                  avg_time_first_mod_rev_week, avg_time_first_mod_rev_all,
                  avg_time_mod_res_week, avg_time_mod_res_all)

        # Insert at index 2 (index 1 is the header)
        sheet.insert_row(values, 2)
