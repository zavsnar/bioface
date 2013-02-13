#! ../env/bin/python
import os, sys
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    execute_from_command_line(sys.argv)
else:
    # driempie hook. Usage example:
    # $ driempye python
    # >>> import manage
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from django.db.models.loading import get_models
    get_models()
