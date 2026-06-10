from django.db import models
import qrcode
from io import BytesIO
import base64
from django.utils.safestring import mark_safe

class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'


class Employee(models.Model):
    full_name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

class Equipment(models.Model):
    STATUS_CHOICES = [
        ('active', 'В эксплуатации'),
        ('repair', 'На ремонте'),
        ('written_off', 'Списано'),
    ]

    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Техника'
        verbose_name_plural = 'Техники'

    def save(self, *args, **kwargs):
        if self.pk:
            old = Equipment.objects.get(pk=self.pk)

            if old.department != self.department:
                MovementHistory.objects.create(
                    equipment=self,
                    from_department=old.department,
                    to_department=self.department,
                    responsible=None
                )

        super().save(*args, **kwargs)

    def qr_code(self):
        data = f"""
    Название: {self.name}
    Серийный номер: {self.serial_number}
    Статус: {self.get_status_display()}
    Отдел: {self.department}
    """

        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        img_str = base64.b64encode(buffer.getvalue()).decode()

        return mark_safe(
            f'<img src="data:image/png;base64,{img_str}" width="150"/>')


class MovementHistory(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    from_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='from_movements'
    )
    to_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='to_movements'
    )
    responsible = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment} → {self.to_department}"

    class Meta:
        verbose_name = 'История перемещения'
        verbose_name_plural = 'стория перемещения'