from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from . import Client


CHOICES_HELP_TEXT = _(
    """The choices field is only used if the question type
if the question type is 'radio', 'select', or
'select multiple' provide a comma-separated list of
options for this question ."""
)

class Survey(models.Model):
    referent = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=400)
    description = models.TextField(_("Description"))

    class SurveyStatus(models.TextChoices):
        DRAFT = 'DR', _('Draft')
        SUBMITTED = 'SU', _('Submitted')
        READY = 'RE', _('Ready')
        RUNNING = 'RU', _('Running')
        COMPLETED = 'CO', _('Completed')

    status = models.CharField(
        max_length=2,
        choices=SurveyStatus.choices,
        default=SurveyStatus.DRAFT,
    )

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __str_(self):
        return "{} - {}".format(self.referent.name, self.name)

def validate_choices(choices):
    """  Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(',')
    empty = 0
    for value in values:
        if value.replace(" ", "") == "":
            empty += 1
    if len(values) < 2 + empty:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain more than one item."
        raise ValidationError(msg)

    


class Question(models.Model):
    TEXT = "text"
    SHORT_TEXT = "short-text"
    RADIO = "radio"
    SELECT = "select"
    SELECT_IMAGE = "select_image"
    SELECT_MULTIPLE = "select-multiple"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"

    QUESTION_TYPES = (
        (TEXT, _("text (multiple line)")),
        (SHORT_TEXT, _("short text (one line)")),
        (RADIO, _("radio")),
        (SELECT, _("select")),
        (SELECT_MULTIPLE, _("Select Multiple")),
        (SELECT_IMAGE, _("Select Image")),
        (INTEGER, _("integer")),
        (FLOAT, _("float")),
        (DATE, _("date")),
    )

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="questions")
    text = models.TextField(_("Text"))
    order = models.IntegerField(_("Order"))
    required = models.BooleanField(_("Required"))
    type = models.CharField(_("Type"), max_length=200, choices=QUESTION_TYPES, default=TEXT)
    choices = models.TextField(_("Choices"), blank=True, null=True, help_text=CHOICES_HELP_TEXT)

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ("survey", "order")

    def get_clean_choices(self):
        """ Return split and stripped list of choices with no null values. """
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(','):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list


    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        msg = "Question '{}' ".format(self.text)
        if self.required:
            msg += "(*) "
        msg += "{}".format(self.get_clean_choices())
        return msg