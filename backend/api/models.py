import os
from django.db import models
from django.contrib.auth.models import User

# VectorField only works with PostgreSQL + pgvector extension.
# Fall back to JSONField when using SQLite for local dev/testing.
_DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql')

if _DB_ENGINE == 'sqlite3':
    # JSONField stores the embedding as a JSON array — no vector search, but
    # the app still runs and all other API endpoints work fine for dev testing.
    _EmbeddingField = lambda **kw: models.JSONField(null=True, blank=True)
else:
    from pgvector.django import VectorField
    _EmbeddingField = lambda **kw: VectorField(**kw)


class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=50, unique=True)
    level = models.IntegerField(default=1)  # 1=Low … 5=Urgent

    def __str__(self):
        return self.name


class Ticket(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.RESTRICT)
    priority = models.ForeignKey(Priority, on_delete=models.RESTRICT)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='history', on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"Agent {self.user.username} – {self.department}"


class KnowledgeBase(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=255, blank=True)
    # PostgreSQL: real VectorField for similarity search
    # SQLite: JSONField (stores array, no ANN — for dev only)
    embedding = _EmbeddingField(dimensions=768, null=True, blank=True)

    def __str__(self):
        return self.title
