from datetime import date

from django.db import models


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(default=date.today)
    checked = models.BooleanField(default=False)
    owner = models.ForeignKey(
        "auth.User", related_name="tasks", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Task {self.id}: {self.title}"

    def __repr__(self) -> str:
        return f"Task {self.id}: {self.title}"
