# search_app/admin.py

from django.contrib import admin
from .models import Country, State, University, Department, ResearchInterest, Professor, FundingOpportunity

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'public_private', 'acceptance_rate')
    list_filter = ('public_private', 'state__country', 'state')
    search_fields = ('name', 'state__name', 'state__country__name')
    autocomplete_fields = ('state',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'ielts_requirement', 'duolingo_score', 'gre_requirement')
    search_fields = ('name', 'university__name')
    list_filter = ('university__state__country', 'university')
    autocomplete_fields = ('university',)

@admin.register(ResearchInterest)
class ResearchInterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'email')
    list_filter = ('department__university__state__country', 'department__university')
    search_fields = ('name', 'department__name', 'department__university__name', 'email')
    autocomplete_fields = ('department', 'research_interests')

@admin.register(FundingOpportunity)
class FundingOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'university', 'grant_amount', 'funding_percentage', 'deadline')
    list_filter = ('funding_percentage', 'university__state__country', 'university')
    search_fields = ('title', 'university__name', 'description')
    autocomplete_fields = ('university', 'state', 'country')
