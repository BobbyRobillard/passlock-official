from django.db import models


class ErrorLog(models.Model):
    user = models.CharField(max_length=150)
    date = models.DateField(auto_now=False, auto_now_add=True)
    description = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.date} | {self.user.split('@')[0]} | {self.description[:50]}"
