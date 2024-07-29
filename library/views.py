# views.py
import datetime
import re
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
# Create your views here.
def home(request):
    return render(request, "library/index.html", context={})




from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Student

def register(request):
    if request.method == 'POST':
        srn = request.POST['srn']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        branch = request.POST['branch']
        contact_no = request.POST['contact_no']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password1 == password2:
            if Student.objects.filter(username=username).exists():
                print("Username exists")
                messages.info(request, 'Username Taken')
                return redirect('register')
            elif Student.objects.filter(email=email).exists():
                print("Email ID exists!")
                messages.info(request, 'Email ID exists')
                return redirect('register')
            else:
                student = Student(
                    srn=srn,
                    name=f"{first_name} {last_name}",
                    branch=branch,
                    contact_no=contact_no,
                    username=username,
                    password=make_password(password1),
                    email=email
                )
                student.save()
                print('Student created')
                messages.success(request, 'You have registered successfully. Please log in.')
                return redirect('login')
        else:
            print("Passwords do not match!!!")
            messages.info(request, 'Passwords do not match!!!')
            return redirect('register')

    return render(request, 'library/register.html')






from django.contrib.auth import authenticate, login as auth_login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'library/login.html')
    
from django.contrib.auth import logout as auth_logout


def logout(request):
    auth_logout(request)
    return redirect('home')



from .models import *
# library/views.py
from django.shortcuts import render, get_object_or_404

from django.db.models import Q

from django.shortcuts import render
from django.db.models import Q
from .models import Book  # Adjust the import according to your project structure

def book_list(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(genre__icontains=query) |
            Q(language__icontains=query)
        )
    else:
        books = Book.objects.all()
    
    context = {
        'book_list': books,  # Ensure this matches the template variable name
        'query': query
    }
    
    return render(request, 'library/book_list.html', context)






from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]



def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search_book(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'summary','author'])

        book_list= Book.objects.filter(entry_query)

    return render(request,'library/book_list.html',locals() )





from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.utils import timezone


from rest_framework.response import Response
from rest_framework import status




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Borrow
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Student, Borrow



def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library/book_details.html', {'book': book})

@csrf_exempt
def borrow_book(request, pk):
    if request.method == 'POST':
        try:
            book = Book.objects.get(pk=pk)
            if book.available_copies > 0:
                # Assuming you have some way of getting the current user
                student = Student.objects.get(username=request.user.username)  # Adjust as needed
                # Update the book
                book.available_copies -= 1
                book.save()
                # Create a new Borrow record
                Borrow.objects.create(student=student, book=book)
                return JsonResponse({'status': 'success', 'message': 'Book issued successfully!'})
            else:
                return JsonResponse({'error': 'No available copies'}, status=400)
        except Book.DoesNotExist:
            return JsonResponse({'error': 'Book not found'}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Borrow, Book  # Ensure you import the Book model if needed
from datetime import datetime

@csrf_exempt
def return_book(request, pk):
    if request.method == 'POST':
        try:
            borrow_record = Borrow.objects.filter(book_id=pk, return_date__isnull=True).first()
            if borrow_record:
                book = borrow_record.book
                book.available_copies += 1
                book.save()
                borrow_record.return_date = datetime.now()
                borrow_record.save()  # Update the return date without deleting the record
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'No borrow record found'}, status=400)
        except Book.DoesNotExist:
            return JsonResponse({'error': 'Book not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)



def book_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('home')  # Or an appropriate error page

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')  # Redirect to the book list after deletion
    return render(request, 'library/book_confirm_delete.html', {'book': book})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Book


