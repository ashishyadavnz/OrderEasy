#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyMeal.settings.production')
    
    if os.environ['DJANGO_SETTINGS_MODULE']=='EasyMeal.settings.production':
        print("You are running on \033[1m"+"Production Environment"+'\033[0;0m')
    if os.environ['DJANGO_SETTINGS_MODULE']=='EasyMeal.settings.local':
        print("You are running on \033[1m"+"Local Environment"+'\033[0;0m')
    if os.environ['DJANGO_SETTINGS_MODULE']=='EasyMeal.settings.staging':
        print("You are running on \033[1m"+"Staging Environment"+'\033[0;0m')
    if os.environ['DJANGO_SETTINGS_MODULE']=='EasyMeal.settings.testing':
        print("You are running on \033[1m"+"Testing Environment"+'\033[0;0m')
    if os.environ['DJANGO_SETTINGS_MODULE']=='EasyMeal.settings.circleci':
        print("You are running on \033[1m"+"Circleci Environment"+'\033[0;0m')

    if '--dev' in sys.argv:
        os.environ['DJANGO_SETTINGS_MODULE'] = "EasyMeal.settings.local"
    elif '--test' in sys.argv:
        os.environ['DJANGO_SETTINGS_MODULE'] = "EasyMeal.settings.testing"
    else:
        f = open(".git/HEAD", "r")
        if 'ref: refs/heads/testing' in f.read() and 'EasyMeal.settings.local' != os.environ['DJANGO_SETTINGS_MODULE']:
            os.environ['DJANGO_SETTINGS_MODULE'] = "EasyMeal.settings.testing"
        f.close()

    try:
        sys.argv.remove('--dev')
    except Exception as e:
        pass
    
    try:
        sys.argv.remove('--test')
    except Exception as e:
        pass
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
