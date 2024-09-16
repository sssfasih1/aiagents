from django.http import HttpResponse,JsonResponse
from .models import University,Professor,FundingOpportunity,Country,State,ResearchInterest,Department
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.management import call_command
from django.core.files.storage import FileSystemStorage
import json
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from together import Together

# Create your views here.
# Sign-Up View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords don't match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
        else:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user)  # Log the user in after sign-up
            return redirect('university_search')  # Redirect to a main page after login

    return render(request, 'nexus/signup.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('university_search')  # Redirect to main page after login
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'nexus/login.html')


# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


client = Together(api_key="*******")


# Define chatbot API view

@csrf_exempt
def chatbot_interaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', 'You are a mentor who guides students for graduate admissions, you focus on graduate assistantships available in universities of USA. You help students in availing RA/TA positions by telling the procedure and giving instructions. Give answers in 5 lines max. ')

        if user_message:
            # Send the user message to the chatbot API
            stream = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=[{"role": "user", "content": user_message}],
                stream=False,
            )

            # Debugging: Print the stream response
            print(stream.choices[0])

            # Extract the response correctly based on the actual structure
            chatbot_response = stream.choices[0].message.content  # Adjust this based on the response

            # Return the response as JSON
            return JsonResponse({'response': chatbot_response}, status=200)
        else:
            return JsonResponse({'error': 'No message provided'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def index(request):
    name= 'Fasih'
    # return HttpResponse(f"Welcome to Opportunities Nexus!")
    return render(request,'nexus/index.html',{'name':name})


@login_required
def university_search(request):
    name_query = request.GET.get('name', '')
    public_private_filter = request.GET.get('public_private', '')
    country_filter = request.GET.get('country', '')
    state_filter = request.GET.get('state', '')

    # Filter universities based on the search criteria
    universities = University.objects.select_related('state__country').all()

    if name_query:
        universities = universities.filter(name__icontains=name_query)
    if public_private_filter:
        universities = universities.filter(public_private=public_private_filter)
    if country_filter:
        universities = universities.filter(state__country__name=country_filter)
    if state_filter:
        universities = universities.filter(state__name=state_filter)

    # Add pagination - display 10 universities per page
    paginator = Paginator(universities, 10)
    page_number = request.GET.get('page')
    universities_page = paginator.get_page(page_number)

    context = {
        'universities': universities_page,
        'countries': Country.objects.all(),
        'states': State.objects.all(),
        'name_query': name_query,
        'public_private_filter': public_private_filter,
        'country_filter': country_filter,
        'state_filter': state_filter,
    }
    return render(request, 'nexus/university_search.html', context)

@login_required
def professor_search(request):
    name_query = request.GET.get('name', '')
    research_interests_query = request.GET.getlist('research_interests')
    country_filter = request.GET.get('country', '')
    state_filter = request.GET.get('state', '')
    university_filter = request.GET.get('university', '')
    department_filter = request.GET.get('department', '')

    professors = Professor.objects.select_related(
        'department__university__state__country'
    ).prefetch_related('research_interests').all()

    if name_query:
        professors = professors.filter(name__icontains=name_query)
    if research_interests_query:
        professors = professors.filter(research_interests__id__in=research_interests_query).distinct()
    if country_filter:
        professors = professors.filter(department__university__state__country__name=country_filter)
    if state_filter:
        professors = professors.filter(department__university__state__name=state_filter)
    if university_filter:
        professors = professors.filter(department__university__name__icontains=university_filter)
    if department_filter:
        professors = professors.filter(department__name__icontains=department_filter)

    context = {
        'professors': professors,
        'countries': Country.objects.all(),
        'states': State.objects.all(),
        'universities': University.objects.all(),
        'departments': Department.objects.all(),
        'research_interests': ResearchInterest.objects.all(),
        'name_query': name_query,
        'research_interests_query': research_interests_query,
        'country_filter': country_filter,
        'state_filter': state_filter,
        'university_filter': university_filter,
        'department_filter': department_filter,
    }
    return render(request, 'nexus/professor_search.html', context)


@login_required
def opportunity_search(request):
    title_query = request.GET.get('title', '')
    country_filter = request.GET.get('country', '')
    state_filter = request.GET.get('state', '')
    university_filter = request.GET.get('university', '')
    min_grant_amount = request.GET.get('min_grant_amount', '')
    max_grant_amount = request.GET.get('max_grant_amount', '')
    funding_percentage_filter = request.GET.get('funding_percentage', '')
    opportunities = FundingOpportunity.objects.all()

    if title_query:
        opportunities = opportunities.filter(title__icontains=title_query)
    if country_filter:
        opportunities = opportunities.filter(country__icontains=country_filter)
    if state_filter:
        opportunities = opportunities.filter(state__icontains=state_filter)
    if university_filter:
        opportunities = opportunities.filter(university__name__icontains=university_filter)
    if min_grant_amount:
        opportunities = opportunities.filter(grant_amount__gte=min_grant_amount)
    if max_grant_amount:
        opportunities = opportunities.filter(grant_amount__lte=max_grant_amount)
    if funding_percentage_filter:
        opportunities = opportunities.filter(funding_percentage=funding_percentage_filter)

    context = {
        'opportunities': opportunities,
        'title_query': title_query,
        'country_filter': country_filter,
        'state_filter': state_filter,
        'university_filter': university_filter,
        'min_grant_amount': min_grant_amount,
        'max_grant_amount': max_grant_amount,
        'funding_percentage_filter': funding_percentage_filter,
    }
    return render(request, 'nexus/opportunity_search.html', context)

@login_required
def university_detail(request, university_id):
    university = get_object_or_404(University, id=university_id)
    departments = university.departments.all()

    context = {
        'university': university,
        'departments': departments,
    }
    return render(request, 'nexus/university_detail.html', context)


@login_required
def department_detail(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    professors_list = department.professors.prefetch_related('research_interests').all()
    paginator = Paginator(professors_list, 10)  # Show 10 professors per page

    page_number = request.GET.get('page')
    professors = paginator.get_page(page_number)

    context = {
        'department': department,
        'professors': professors,
    }
    return render(request, 'nexus/department_detail.html', context)

@login_required
def professor_detail(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    context = {
        'professor': professor,
    }
    return render(request, 'nexus/professor_detail.html', context)


# Shortlist a university
@login_required
def shortlist_university(request, university_id):
    university = get_object_or_404(University, id=university_id)
    user = request.user
    user.shortlisted_universities.add(university)  # Add the university to the user's shortlist
    return redirect('university_search')  # Redirect back to university search or detail page

# Remove a university from shortlist
@login_required
def remove_shortlist_university(request, university_id):
    university = get_object_or_404(University, id=university_id)
    user = request.user
    user.shortlisted_universities.remove(university)  # Remove the university from the shortlist
    return redirect('profile')  # Redirect back to the profile page

# My Profile Page (Shortlisted Universities)
@login_required
def profile_view(request):
    user = request.user
    shortlisted_universities = user.shortlisted_universities.all()  # Get all shortlisted universities
    context = {
        'shortlisted_universities': shortlisted_universities,
    }
    return render(request, 'nexus/profile.html', context)


# Allow only superusers to export data
@user_passes_test(lambda u: u.is_superuser)
def export_data(request):
    # Dump all the data in JSON format
    data = serializers.serialize('json', User.objects.all())  # Export the User model

    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="backup.json"'

    return response

# Allow only superusers to import data
@user_passes_test(lambda u: u.is_superuser)
def import_data(request):
    if request.method == 'POST' and request.FILES['backup']:
        # Save the uploaded file
        backup_file = request.FILES['backup']
        fs = FileSystemStorage()
        filename = fs.save(backup_file.name, backup_file)
        file_path = fs.path(filename)

        try:
            # Load the data from the file using loaddata
            call_command('loaddata', file_path)
            return HttpResponse("Data successfully imported.", status=200)
        except Exception as e:
            return HttpResponse(f"Error importing data: {str(e)}", status=500)

    return HttpResponse("No file uploaded.", status=400)