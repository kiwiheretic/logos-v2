from django.core.management.base import BaseCommand, CommandError
from room_manage.models import NickHistory, NickSummary

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
            for rec in NickHistory.objects.all():
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

            self.stdout.write('Successfully finished addung data to NickSummary table.')
