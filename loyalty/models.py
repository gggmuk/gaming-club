from django.db import models

class Client(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    name = models.CharField(max_length=255, verbose_name="Имя")
    rank = models.CharField(max_length=100, verbose_name="Ранг")
    bonus_points = models.IntegerField(default=0, verbose_name="Бонусные баллы")
    total_hours_played = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Всего часов игры"
    )
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name="Реферальный код")
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals', verbose_name="Пригласил")

    def save(self, *args, **kwargs):
        if not self.referral_code:
            import uuid
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.telegram_id})"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
