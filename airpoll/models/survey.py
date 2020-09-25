from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from . import Client, Interviewee, Interviewer


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
    brief = models.FileField(upload_to='uploads/', null=True)

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


class Response(models.Model):

    """
        A Response object is a collection of questions and answers with a
        unique interview uuid.
    """

    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="responses")
    user = models.ForeignKey(Interviewee, on_delete=models.SET_NULL, verbose_name=_("User"), null=True, blank=True)
    interviewer = models.ForeignKey(Interviewer, on_delete=models.SET_NULL, verbose_name=_("Interviewer"), null=True, blank=True)
    interview_uuid = models.CharField(_("Interview unique identifier"), max_length=36)

    class Meta:
        verbose_name = _("Set of answers to surveys")
        verbose_name_plural = _("Sets of answers to surveys")

    def __str__(self):
        msg = "Response to {} by {}".format(self.survey, self.user)
        msg += " on {}".format(self.created)
        return msg


class Answer(models.Model):

    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Question"), related_name="answers")
    response = models.ForeignKey(Response, on_delete=models.CASCADE, verbose_name=_("Response"), related_name="answers")
    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    body = models.TextField(_("Content"), blank=True, null=True)

    def __init__(self, *args, **kwargs):
        try:
            question = Question.objects.get(pk=kwargs["question_id"])
        except KeyError:
            question = kwargs.get("question")
        body = kwargs.get("body")
        if question and body:
            self.check_answer_body(question, body)
        super(Answer, self).__init__(*args, **kwargs)

    @property
    def values(self):
        if self.body is None:
            return [None]
        if len(self.body) < 3 or self.body[0:3] != "[u'":
            return [self.body]
        #  We do not use eval for security reason but it could work with :
        #  eval(self.body)
        #  It would permit to inject code into answer though.
        values = []
        raw_values = self.body.split("', u'")
        nb_values = len(raw_values)
        for i, value in enumerate(raw_values):
            if i == 0:
                value = value[3:]
            if i + 1 == nb_values:
                value = value[:-2]
            values.append(value)
        return values

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == "[":
                    answers = []
                    for i, part in enumerate(body.split("'")):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = "Impossible answer '{}'".format(body)
                    msg += " should be in {} ".format(choices)
                    raise ValidationError(msg)

    def __str__(self):
        return "{} to '{}' : '{}'".format(self.__class__.__name__, self.question, self.body)
