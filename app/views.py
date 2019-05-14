from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.db.models import Avg

from .models import Book, Review
from .forms import CustomUserCreationForm, AddBookForm, PostReviewForm
from .service import get_book_info


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'app/signup.html'


def index(request):
    review_list = Review.objects.order_by('-reviewed_at')
    context = {'reviews_page': 'active', 'review_list': review_list}
    return render(request, 'app/index.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    context = {'reviews_page': 'active', 'review': review}
    return render(request, 'app/review_detail.html', context)


def books(request):
    if request.method == "POST":
        add_book_form = AddBookForm(request.POST)
        if add_book_form.is_valid():
            # 新規本追加処理
            book = get_book_info(add_book_form.save(commit=False))
            messages.success(request, '『{0}』を追加しました'.format(book.title))
            return redirect('books')
    add_book_form = AddBookForm()
    book_list = Book.objects.order_by('title').annotate(ave_score=Avg('review__score'))
    context = {'books_page': 'active', 'book_list': book_list, 'add_book_form': add_book_form}
    return render(request, 'app/books.html', context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == "POST":
        # レビュー登録処理
        post_review_form = PostReviewForm(request.POST)
        if post_review_form.is_valid():
            review = post_review_form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'レビューが投稿されました')
        return redirect('book_detail', book_id=book_id)
    post_review_form = PostReviewForm()
    context = {
        'books_page': 'active',
        'book': book,
        'ave_score': book.review_set.aggregate(Avg('score'))['score__avg'],
        'post_review_form': post_review_form
    }
    return render(request, 'app/book_detail.html', context)
