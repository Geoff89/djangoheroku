from django.contrib import admin
from .models import Author, Book, Genre, BookInstance, Language

# Register your models here.
class BookInlineAuthor(admin.TabularInline):
    model = Book 
    extra = 0   

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] 
    inlines = [BookInlineAuthor]
    
#Register the admin casses for book using the decorator
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
   

#Register the admin classes for book instance usign the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', id)
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {'fields': ('book', 'imprint', 'id')}),
        ('Availability', { 'fields': ('status', 'due_back')}),
    )


admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Language)

#admin.site.register(Book)
#register the admn class with the associated model

#admin.site.register(BookInstance)