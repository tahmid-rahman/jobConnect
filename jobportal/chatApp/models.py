from django.db import models
from accounts.models import CustomUser as User

class Thread(models.Model):
    participant1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='participant1')
    participant2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='participant2')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Thread {self.id}'


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender.username} at {self.timestamp}'
