from django.db import models
from apps.users.models import User


class Tweet(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tweets'
    )
    content = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.tweet.id}'