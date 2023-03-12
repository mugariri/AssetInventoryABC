import json
from datetime import datetime, date

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Call any function or class method in django project without using shell'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('callable', nargs=1, type=str)
        parser.add_argument('function-arguments', nargs='*', type=str, help='Positional arguments')
        parser.add_argument('--p', nargs='+', type=str, help='Keyword arguments to function')
        parser.add_argument('--verbose', action='store_true', help='Show parsed function arguments')

    def get_callable(self, path):
        def import_from(module, name):
            module = __import__(module, fromlist=[name])
            return getattr(module, name)

        def import_name(string):
            string = string.strip()
            tokens = string.split(".")
            if len(tokens) == 1:
                return __import__(string)
            elif len(tokens) > 1:
                return import_from(".".join(tokens[:-1]).strip(), tokens[-1].strip())
            else:
                raise ImportError('Invalid import string: {}'.format(string))

            return import_from(tokens)

        x_tokens = []
        while True:
            try:
                x_callable = import_name(path)
                if callable(x_callable) and not x_tokens:
                    return (True, x_callable)
                else:
                    for token in x_tokens:
                        x_callable = getattr(x_callable, token)
                    if callable(x_callable):
                        return (True, x_callable)
                    else:
                        return (False, None)
            except ImportError:
                tokens = path.split(".")
                if len(tokens) == 1:
                    raise
                elif len(tokens) > 1:
                    path = ".".join(tokens[:-1]).strip()
                    x_tokens = [tokens[-1].strip()] + x_tokens

    def check(self, *args, **kwargs):
        pass

    def handle(self, *args, **options):
        def cast(value):
            if value.startswith("'") and value.endswith("'") or value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            if value.isnumeric():
                return int(value)
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False
            if value.lower() == "none":
                return None

            convertors = [float, date, datetime.fromisoformat]
            for c in convertors:
                try:
                    return c(value)
                except BaseException as e:
                    pass
            return value

        from django.conf import settings

        print("\nStarting...\n")
        function_path = options['callable'][0]
        function_path = getattr(settings, 'UTILITY_COMMANDS', {}).get(function_path, function_path)

        arguments = options.get('function-arguments', [])
        kwargs = options.get('p', {})
        if kwargs is None:
            kwargs = {}
        if arguments is None:
            arguments = []

        success, x_collable = self.get_callable(function_path)
        if not success:
            print("\nCould not find specified callable:{}".format(function_path))
        else:
            arguments = [cast(x) for x in arguments]
            kwargs = {x.split('=')[0]: cast(x.split('=')[1]) for x in kwargs}
            if options.get('verbose', False):
                print("\nPositional args\n{}\n".format(
                    json.dumps({i + 1: str(x) if isinstance(x, datetime) else x for i, x in enumerate(arguments)},
                               indent=True)))
                print("\nKeyword args\n{}\n".format(
                    json.dumps({x: str(kwargs[x]) if isinstance(kwargs[x], datetime) else kwargs[x] for x in kwargs},
                               indent=True)))
            print("\nReturn:{}".format(x_collable(*arguments, **kwargs)))
