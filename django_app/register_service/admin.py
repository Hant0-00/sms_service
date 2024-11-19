from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Number
from django import forms


@admin.register(Number)
class NumberAdmin(admin.ModelAdmin):
    list_display = ['number']
    change_list_template = "admin/numbers/message_change_list.html"

    # Добавляем кастомный URL для импорта номеров
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-numbers/', self.admin_site.admin_view(self.import_numbers), name='import_numbers'),
        ]
        return custom_urls + urls

    # Определяем форму для загрузки файла
    class ImportNumbersForm(forms.Form):
        file = forms.FileField(label='Выберите файл .txt')

    # Создаем представление для импорта номеров
    def import_numbers(self, request):
        if request.method == "POST":
            form = self.ImportNumbersForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                # Обработка файла
                imported, skipped = self.handle_uploaded_file(file)
                messages.success(request, f"Импорт завершен. Добавлено: {imported}, Пропущено: {skipped}")
                return redirect('..')  # Возврат на страницу списка
        else:
            form = self.ImportNumbersForm()

        context = {
            'form': form,
            'title': 'Импорт номеров из файла',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        return render(request, "admin/numbers/import_numbers.html", context)

    # Метод для обработки загруженного файла
    def handle_uploaded_file(self, file):
        import io

        imported = 0
        skipped = 0
        error_lines = []

        # Читаем файл построчно
        for line_number, line in enumerate(io.TextIOWrapper(file, encoding='utf-8'), start=1):
            number = line.strip()
            if not number:
                skipped += 1
                continue  # Пропускаем пустые строки

            # Валидация номера: только цифры и длина 12 символов
            if not number.isdigit() or len(number) != 12:
                skipped += 1
                error_lines.append((line_number, number))
                continue

            # Проверяем, существует ли уже номер
            if not Number.objects.filter(number=number).exists():
                Number.objects.create(number=number)
                imported += 1
            else:
                skipped += 1  # Пропускаем дубликаты

        # Логируем ошибки, если есть
        if error_lines:
            for line_num, num in error_lines:
                messages.warning(self.request, f"Строка {line_num}: неверный формат номера '{num}' пропущен.")

        return imported, skipped