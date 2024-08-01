from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    IMPORTANCE_CHOICES = [
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]

    user=models.ForeignKey (User, on_delete=models.CASCADE)
    title=models.CharField(max_length=300)
    description=models.CharField(max_length=500)
    completed=models.BooleanField()
    duration=models.PositiveIntegerField()
    importance=models.CharField(max_length=6, choices=IMPORTANCE_CHOICES)


    def __str__(self) -> str:
        return self.title
    
class APIKey(models.Model):
    key = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.key