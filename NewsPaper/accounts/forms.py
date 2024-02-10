from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_users = Group.objects.get(name="general group")
        user.groups.add(common_users)
        return user
