from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.text import slugify 
# from E_learning_API.profiles.models import Student, Instructor
from django.core.validators import MaxValueValidator, validate_comma_separated_integer_list
from django.core.exceptions import ValidationError


class TimestampedModel(models.Model):
    """
    Base class with `created` and `modified` fields.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Subject(TimestampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    def __str__(self):
        return self.title


class Course(TimestampedModel):
    # instructor = models.ForeignKey(Instructor, related_name='courses_created',
    #                                on_delete=models.CASCADE,)
    subject = models.ForeignKey(Subject, related_name='courses', 
                                on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
   
    

    def __str__(self):
        return self.title


class Quiz(TimestampedModel):
    FORM_CHOICES = ( 
    ("1", "1"), 
    ("2", "2"), 
    ("3", "3"), 
    ("4", "4"), )
    level = models.CharField(choices=FORM_CHOICES, max_length=20)
    # subject = models.ForeignKey(Subject, related_name='quizzes', 
    #                             on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    single_attempt = models.BooleanField(blank=False, default=False, 
                                         help_text=(" only one attempt"),
                                         verbose_name=("Single Attempt"))
    pass_mark = models.SmallIntegerField(blank=True, default=0,
                                         verbose_name=("Pass Mark"), 
                                         help_text=("Score required to pass exam."),
                                         validators=[MaxValueValidator(100)])
    success_text = models.TextField(
        blank=True, help_text=_("Displayed if user passes."),default="Hurray you have passed",
        verbose_name=_("Success Text"))

    fail_text = models.TextField(
        verbose_name=_("Fail Text"),default="Hurray you have failed",
        blank=True, help_text=_("Displayed if user fails."))

    draft = models.BooleanField(
        blank=True, default=False,
        verbose_name=_("Draft"))

    duration = models.DurationField(default=timedelta(minutes=40))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Quiz, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
   

class Badge(TimestampedModel):
    Quiz = models.OneToOneField(Quiz,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.title
    

class Question(TimestampedModel):
    quiz = models.ForeignKey("Quiz", related_name="questions",
                             on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1024, unique=True)
    hint = models.CharField(max_length=1024, blank=True)

   
    @property
    def no_choices(self):
        count=self.choices.count()
        print(count)
        return count

   


    
    
    def __str__(self):
        return self.question_text


class Choice(TimestampedModel):
    choice_position = ( 
    ("a", "a"), 
    ("b", "b"), 
    ("c", "c"), 
    ("d", "d"), )

    question = models.ForeignKey("Question", related_name="choices", 
                                 on_delete=models.CASCADE)
    position = models.CharField(choices=choice_position, max_length=50)                             
    choice = models.CharField("Choice", max_length=50)
   
    is_correct = models.BooleanField('Correct choice', default=False)

    class Meta:
        unique_together = [
            # no duplicated choice per question
            ("question", "choice"), 
            # no duplicated position per question 
            ("question", "position") 
        ]
        ordering = ("position",)

    def __str__(self):
        return '%s: %s' % (self.position, self.choice)


# class StudentAnswer(TimestampedModel):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_answers')
#     answer = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='student_answers')
