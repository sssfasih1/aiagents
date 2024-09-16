# search_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    shortlisted_universities = models.ManyToManyField('University', blank=True, related_name='shortlisted_by')

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    class Meta:
        unique_together = ('name', 'country')

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class University(models.Model):
    PUBLIC_PRIVATE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    name = models.CharField(max_length=200)
    website = models.URLField()
    public_private = models.CharField(max_length=7, choices=PUBLIC_PRIVATE_CHOICES)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='universities')
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def country(self):
        return self.state.country


class Department(models.Model):
    name = models.CharField(max_length=200)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='departments')
    ielts_requirement = models.CharField(max_length=50, null=True, blank=True)
    duolingo_score = models.CharField(max_length=50, null=True, blank=True)
    gre_requirement = models.CharField(max_length=50, null=True, blank=True)
    faculty_page = models.URLField(null=True, blank=True)
    other_requirements = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} at {self.university.name}"


class ResearchInterest(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Professor(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='professors')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    website = models.URLField(null=True, blank=True)  # Add this line
    research_interests = models.ManyToManyField(ResearchInterest, related_name='professors')

    def __str__(self):
        return self.name

    @property
    def university(self):
        return self.department.university

    @property
    def state(self):
        return self.department.university.state

    @property
    def country(self):
        return self.department.university.state.country
class FundingOpportunity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateField()
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='opportunities')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    grant_amount = models.DecimalField(max_digits=12, decimal_places=2)
    FUNDING_PERCENTAGE_CHOICES = [
        ('100', 'Fully Funded'),
        ('75', '75% Funded'),
        ('50', '50% Funded'),
        ('other', 'Others'),
    ]
    funding_percentage = models.CharField(max_length=5, choices=FUNDING_PERCENTAGE_CHOICES)

    def __str__(self):
        return self.title
