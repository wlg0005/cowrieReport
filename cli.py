import click
from reduce.log import Log, write_report
from pathlib import Path

class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is mutually exclusive with %s' %
            self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, self.not_required_if))
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)

@click.command(help='Remove noisy sets of commands in a cowrie json log using regular expressions', no_args_is_help=True)
@click.option('-d', '--dir', default=None, help='Specify directory containing cowrie json logs', cls=NotRequiredIf, not_required_if='log')
@click.option('-l', '--log', default=None, help='Specify a cowrie json log file', cls=NotRequiredIf, not_required_if='dir')
@click.option('-e', '--exclude', required=True, help='Specify an exclusions file (regular expressions on each line)')
@click.option('-o', '--output', required=False, default="./", help="Specify output directory to store report")
def reduce_noise(log, exclude, output, dir):
    if dir != None:
        files = Path(dir).glob('*')
        for file in files:
            obj = Log(log_filename=file, exclusions_filename=exclude)
            write_report(log_filename=file, exclusions=obj.exclusions, good_sessions=obj.good_sessions, entries=obj.entries, output_dir=output)
    else:
        obj = Log(log_filename=log, exclusions_filename=exclude)
        write_report(log_filename=log, exclusions=obj.exclusions, good_sessions=obj.good_sessions, entries=obj.entries, output_dir=output)
        click.echo("Done!")

if __name__ == "__main__":
    reduce_noise()