from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('logout/', views.logout, name='logout'),
    path('search/', views.search_book, name='search_b'),
    path('api/borrow/<int:pk>/', views.borrow_book, name='borrow_book'),
    path('api/return/<int:pk>/', views.return_book, name='return_book'),  # Ensure this URL pattern is present
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
]
