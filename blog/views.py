from django.shortcuts import render, redirect
from .models import Post, BlogComment
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
import math
from django.core.paginator import Paginator    # this for pagination


# Create your views here.
#def bloghome(request):
#    allposts = Post.objects.all()
#    context = {'allPosts': allposts}
#    return render(request, "blog/blogHome.html", context)


def bloghome(request):
    no_of_posts = 2
    #if request.GET("pageno")
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)


    """
    1: 0-3
    2: 3-6
    3: 6-9
    
    1: 0 to  0 + no_of_posts
    2: no_of_posts to no_of_posts + no_of_posts
    3: no_of_posts + no_of_posts to no_of_posts+ no_of_posts +no_of_posts

    (page -1)* no_of_posts to page* no_of_posts
    """

    allposts = Post.objects.all()
    length = len(allposts)
    allposts = allposts[(page-1)*no_of_posts: page* no_of_posts]
    if page>1:
        prev = page - 1
    else:
        prev = None

    if page<math.ceil(length / no_of_posts):
        nxt = page + 1
    else: nxt = None
    
    context = {'allPosts': allposts, 'prev': prev, 'nxt': nxt}
    return render(request, "blog/blogHome.html", context)

def search(request):
    query = request.GET['query']
    if len(query) > 78:
        allPosts = Post.objects.none()
    else:
        allPostsTitle = Post.objects.filter(title__icontains=query)
        allPostsAuthor = Post.objects.filter(author__icontains=query)
        allPostsContent = Post.objects.filter(content__icontains=query)
        allPosts = allPostsTitle.union(allPostsContent, allPostsAuthor)

        # next for pagination...
        paginator = Paginator(allPosts, 1) # Show 5 posts per page.
        page_number = request.GET.get('page')   
        page_obj = paginator.get_page(page_number)

    if allPosts.count() == 0:
        messages.warning(request, "No search results found. Please refine your query.")
    params = {'allPosts': allPosts, 'query': query, 'page_obj': page_obj}
    return render(request, 'blog/search.html', params)


def blogPost(request, slug):
    post = Post.objects.filter(slug=slug).first()
    post.views = post.views + 1
    post.save()

    comments = BlogComment.objects.filter(post=post, parent=None)
    replies = BlogComment.objects.filter(post=post).exclude(parent=None)
    replyDict = {}
    for reply in replies:
        if reply.parent.sno not in replyDict.keys():
            replyDict[reply.parent.sno] = [reply]
        else:
            replyDict[reply.parent.sno].append(reply)
    context = {'post': post, 'comments': comments, 'user': request.user, 'replyDict': replyDict}

    return render(request, "blog/blogPost.html", context)


def postComment(request):
    if request.method == "POST":
        comment = request.POST.get('comment')
        user = request.user
        postSno = request.POST.get('postSno')
        post = Post.objects.get(sno=postSno)
        parentSno = request.POST.get('parentSno')
        if parentSno == "":
            comment = BlogComment(comment=comment, user=user, post=post)
            comment.save()
            messages.success(request, "Your comment has been posted successfully")
        else:
            parent = BlogComment.objects.get(sno=parentSno)
            comment = BlogComment(comment=comment, user=user, post=post, parent=parent)
            comment.save()
            messages.success(request, "Your reply has been posted successfully")

    return redirect(f"/blog/{post.slug}/")