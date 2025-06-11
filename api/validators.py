import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat


def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
    if not ext in valid_extensions:
        raise ValidationError(
            _('Неподдерживаемый формат изображения. Разрешены: jpg, jpeg, png, gif, bmp, webp, svg.')
        )


def validate_image_size(value):
    filesize = value.size
    max_size = 5 * 1024 * 1024  # 5MB
    if filesize > max_size:
        raise ValidationError(
            _('Размер файла не должен превышать %s. Текущий размер: %s') % (
                filesizeformat(max_size),
                filesizeformat(filesize)
            )
        )


def validate_svg_content(value):
    if value.name.endswith('.svg'):
        try:
            content = value.read().decode('utf-8')
            if '<script' in content.lower():
                raise ValidationError(_('SVG файл содержит запрещенные скрипты'))
        except UnicodeDecodeError:
            raise ValidationError(_('Некорректный SVG файл'))
