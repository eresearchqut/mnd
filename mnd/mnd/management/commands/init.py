from rdrf.management.commands.init import Command as RdrfCommand

from ... import initial_data


class Command(RdrfCommand):

    def load_module_data(self, name, **options):
        try:
            module = getattr(initial_data, name)
        except AttributeError:
            self.stderr.write('Unknown dataset "%s".' % name)
            return

        for dep in getattr(module, "deps", []):
            self.load_module_data(dep, **options)

        self.load_data_once(module, **options)
