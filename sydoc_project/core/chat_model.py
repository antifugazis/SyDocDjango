

class ChatMessage(models.Model):
    """
    Model to store messages between users
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Expéditeur'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Destinataire'
    )
    content = models.TextField(verbose_name='Contenu du message')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'envoi')
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    
    class Meta:
        verbose_name = 'Message de Chat'
        verbose_name_plural = 'Messages de Chat'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"De {self.sender.username} à {self.recipient.username}: {self.content[:50]}..."