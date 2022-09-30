from django.test import TestCase
from django.contrib.auth.decorators import user_passes_test

# Create your tests here.


def group_required(*group_names):
    def in_groups(user):
        if bool(user.groups.filter(name__in=group_names)) | user.is_superuser:
            return True

    return user_passes_test(in_groups, login_url='/login/')
