from django.db import models
from django.contrib.auth.models import User

# Team model to store team information
class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)  # Users can belong to multiple teams

    def __str__(self):
        return self.name

# Task model with the assigned team field
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # New description field
    due_date = models.DateField()
    priority = models.CharField(
        max_length=20,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        default='Medium'
    )  # New priority field
    assigned_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    student_name = models.CharField(max_length=100, blank=True)  # Optional field to assign individual student
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def assigned_to(self):
        """ Returns a formatted string to indicate whether the task is assigned to a team or a student. """
        if self.assigned_team:
            return f"Team: {self.assigned_team.name}"
        return f"Student: {self.student_name}"

# Comment model to store comments for tasks
class Comment(models.Model):
    task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.task}"
