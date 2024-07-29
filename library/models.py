from django.db import models



from django.contrib.auth.models import User




from django.contrib.auth.hashers import make_password

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character ISBN number')
    genre = models.CharField(max_length=200, help_text="Enter a book genre")
    language = models.CharField(max_length=200, help_text="Enter the book's natural language")
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()
    pic = models.ImageField(blank=True, null=True, upload_to='library/pics/')

    def __str__(self):
        return f"{self.title} by {self.author}"

class Student(models.Model):
    
    srn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=10)
    branch = models.CharField(max_length=3)
    contact_no = models.CharField(max_length=10)
    total_books_due = models.IntegerField(default=0)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=128)  # Storing the hashed password

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.srn

class Borrow(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)  # Allow null temporarily
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.name} borrowed {self.book.title}"
