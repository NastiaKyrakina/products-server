from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

from products.models.security_settings import SecuritySettings


# Наявність букв, знаків пунктуації та знаків арифметичних операцій.
class SymbolsIncludesValidator:
    def validate(self, password, user=None):
        if not self.validation_enabled():
            return
        pattern_letter = re.compile('[a-zA-Z]+')
        pattern_punctuation_mark = re.compile('[\.,\-:;?!]+')
        pattern_arithmetic_op= re.compile('[><+\-*\/]+')
        valid_password = pattern_letter.search(password) and pattern_punctuation_mark.search(password) and pattern_arithmetic_op.search(password)

        if not valid_password:
            raise ValidationError(
                _("This password must contain at least one letter, punctuation mark and sign of arithmetic operation"),
                code='password_miss_symbols'
            )

    def get_help_text(self):
        if not self.validation_enabled():
            return ""
        return "Your password must contain at least one letter, punctuation mark and sign of arithmetic operation"


    def validation_enabled(self):
        validation_enabled = SecuritySettings.objects.get(name='PasswordSymbolsCheck')
        return validation_enabled and validation_enabled.enabled
