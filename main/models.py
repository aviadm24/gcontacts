from django.db import models

# https://stackoverflow.com/questions/15454008/how-to-reset-db-in-django-i-get-a-command-reset-not-found-error
class User_tokens(models.Model):
    name = models.CharField(max_length=100)
    crmuserid = models.CharField(max_length=20)  #, unique=True
    refresh_token = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    state_key = models.CharField(max_length=100)


    def __str__(self):
        return self.crmuserid
