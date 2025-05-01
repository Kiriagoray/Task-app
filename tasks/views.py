from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Comment
from .forms import CommentForm, TaskForm, UserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q  # For search queries
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.views.decorators.http import require_POST

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # Get the task
    comments = task.comments.all()  # Fetch related comments for this task

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # Associate the logged-in user with the comment
            comment.task = task  # Associate the comment with the specific task
            comment.save()
            return redirect('task_detail', task_id=task.id)  # Redirect to the same task detail page
    else:
        form = CommentForm()  # If GET request, just initialize an empty form

    return render(request, 'task_detail.html', {'task': task, 'comments': comments, 'form': form})


# Registration View
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # ✅ specify backend as string
            return redirect('home')  # or wherever you want to go after registering
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

# Home View with search and filter
@login_required
def home(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    tasks = Task.objects.all().order_by('-id')

    # Search functionality
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(student_name__icontains=query)
        )

    # Filter by status (completed or incomplete)
    if status_filter == 'completed':
        tasks = tasks.filter(completed=True)
    elif status_filter == 'incomplete':
        tasks = tasks.filter(completed=False)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority')
        student_name = request.POST.get('student_name')

        task = Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            student_name=student_name
        )

        # Send the email notification after creating a new task
        send_task_notification(task)

        return redirect('home')

    return render(request, 'home.html', {
        'tasks': tasks,
        'query': query,
        'status_filter': status_filter
    })


# Edit Task View
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)  # Bind the form to the task instance
        if form.is_valid():
            form.save()  # Save the updated task

            # Send the email notification after updating the task
            send_task_notification(task)

            return redirect('/')  # Redirect to home after saving
    else:
        form = TaskForm(instance=task)  # Get the current task data in the form

    return render(request, 'edit_task.html', {'form': form, 'task': task})


# Complete Task View
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = True
    task.save()

    # Send notification for task completion (optional)
    send_task_notification(task)

    return redirect('home')


# Delete Task View
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('home')


# Post Task View
@login_required
def post_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new task
            return redirect('home')  # Redirect to the home page after posting
    else:
        form = TaskForm()  # Create an empty form for GET request

    return render(request, 'post_task.html', {'form': form})


# Function to send email notification for task
def send_task_notification(task):
    subject = f'New Task Assigned: {task.title}'
    message = f'You have been assigned a new task: {task.description}\nDue Date: {task.due_date}'

    recipient_emails = []
    if task.assigned_team:  # ✅ Prevent AttributeError if no team assigned
        recipient_emails = [
            member.email for member in task.assigned_team.members.all() if member.email
        ]

    if recipient_emails:
        send_mail(
            subject,
            message,
            'from-email@example.com',  # Replace with your actual sender email
            recipient_emails,
            fail_silently=False,
        )

@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')