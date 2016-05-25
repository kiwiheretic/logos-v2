from django.core.management.base import BaseCommand, CommandError
from room_manage.models import NickHistory, NickSummary
from django.db import transaction

class Command(BaseCommand):
    help = 'Builds the NickSummary table from NickHistory'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?')
        

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand:
            pass
            self.stdout.write('Nothing done')
        else:
            self.create_summary()
            self.stdout.write('Successfully finished adding data to NickSummary table.')

    @transaction.atomic
    def create_summary(self):
        last_rec = NickSummary.objects.order_by('last_seen').last()
        if last_rec:
            last_rec_dt = last_rec.last_seen
            self.stdout.write(str(last_rec_dt))
            qs = NickHistory.objects.filter(time_seen__gte = last_rec_dt).order_by('time_seen')
        else:
            qs = NickHistory.objects.all().order_by('time_seen')

        for rec in qs:
            network = rec.network
            nick = rec.nick
            host_mask = rec.host_mask
            time_seen = rec.time_seen
            try:
                obj = NickSummary.objects.get(
                    network = network,
                    nick = nick,
                    host_mask = host_mask)
                
                if time_seen > obj.last_seen:
                    obj.last_seen = time_seen
                    obj.save()
            except NickSummary.DoesNotExist:
                obj = NickSummary(network = network,
                        nick = nick,
                        host_mask = host_mask,
                        last_seen = time_seen)
                obj.save()

