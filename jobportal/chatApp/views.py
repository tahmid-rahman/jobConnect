from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Thread, Message
from accounts.models import CustomUser as User
from django.utils.timesince import timesince
import json

def is_participant(thread, user):
    return thread.participant1 == user or thread.participant2 == user

def get_other_participant(thread, user):
    return thread.participant2 if thread.participant1 == user else thread.participant1

# @login_required
# def index(request):
#     threads = (
#         Thread.objects.filter(participant1=request.user) |
#         Thread.objects.filter(participant2=request.user)
#     ).order_by('-updated')

    
#     data = []
#     for thread in threads:
#         last_message = thread.messages.last()
#         other = get_other_participant(thread, request.user)
#         unread = thread.messages.filter(is_read=False).exclude(sender=request.user).exists()
#         data.append({
#             'thread': thread,
#             'participant': other,
#             'has_unread': unread,
#         })

#     return render(request, 'chat/message.html', {
#         'thread_data': data,
#         'first_thread': threads.first()
#     })

@login_required
def index(request):
    threads = (
        Thread.objects.filter(participant1=request.user) |
        Thread.objects.filter(participant2=request.user)
    ).order_by('-updated')
    
    # Get thread_id from URL if exists
    thread_id = request.GET.get('thread_id')
    first_thread = None
    
    if thread_id:
        first_thread = get_object_or_404(Thread, id=thread_id)
        if not is_participant(first_thread, request.user):
            first_thread = None
    
    if not first_thread and threads.exists():
        first_thread = threads.first()
    
    data = []
    for thread in threads:
        other = get_other_participant(thread, request.user)
        unread = thread.messages.filter(is_read=False).exclude(sender=request.user).exists()
        data.append({
            'thread': thread,
            'participant': other,
            'has_unread': unread,
        })
    
    return render(request, 'chat/message.html', {
        'thread_data': data,
        'first_thread': first_thread,
        'next_url': request.GET.get('next', '')
    })


@login_required
def fetch_messages(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if not is_participant(thread, request.user):
        return JsonResponse({'error': 'Not allowed'}, status=403)

    messages = thread.messages.order_by('timestamp')
    response = []

    for msg in messages:
        if msg.sender != request.user and not msg.is_read:
            msg.is_read = True
            msg.save()

        response.append({
            'id': msg.id,
            'content': msg.content,
            'file_url': msg.file.url if msg.file else None,
            'sender_name': msg.sender.username,
            'timestamp': timesince(msg.timestamp),
            'is_me': msg.sender == request.user,
            'is_read': msg.is_read,
            'is_edited': msg.is_edited,
            'pic': msg.sender.profile.profile_picture.url if msg.sender.profile.profile_picture else None,
        })
        # print(msg.sender.profile.profile_picture.url if msg.sender.profile.profile_picture else None)


    return JsonResponse({'messages': response})

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        content_type = request.content_type
        if content_type == 'application/json':
            data = json.loads(request.body)
            thread_id = data.get('thread_id')
            content = data.get('content', '')

            thread = get_object_or_404(Thread, id=thread_id)
            if not is_participant(thread, request.user):
                return JsonResponse({'error': 'Not a participant'}, status=403)

            message = Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )

            thread.updated = message.timestamp
            thread.save()

            return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
@login_required
def delete_message(request, msg_id):
    message = get_object_or_404(Message, id=msg_id, sender=request.user)
    message.delete()
    return JsonResponse({'status': 'deleted'})

@csrf_exempt
@login_required
def edit_message(request, msg_id):
    if request.method == 'POST':
        message = get_object_or_404(Message, id=msg_id, sender=request.user)
        data = json.loads(request.body)
        new_content = data.get('content', '')
        message.content = new_content
        message.is_edited = True
        message.save()
        return JsonResponse({'status': 'edited'})
    return JsonResponse({'error': 'Invalid'}, status=400)

@csrf_exempt
@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES:
        thread_id = request.POST.get('thread_id')
        file = request.FILES.get('file')
        thread = get_object_or_404(Thread, id=thread_id)

        if not is_participant(thread, request.user):
            return JsonResponse({'error': 'Not allowed'}, status=403)

        Message.objects.create(
            thread=thread,
            sender=request.user,
            file=file,
        )
        thread.save()

        return JsonResponse({'status': 'uploaded'})
    return JsonResponse({'error': 'Invalid'}, status=400)

@login_required
def get_thread_updates(request):
    threads = (
        Thread.objects.filter(participant1=request.user) |
        Thread.objects.filter(participant2=request.user)
    ).order_by('-updated').select_related('participant1__profile', 'participant2__profile')
    
    data = []
    for thread in threads:
        other = get_other_participant(thread, request.user)
        last_message = thread.messages.last()
        unread = thread.messages.filter(is_read=False).exclude(sender=request.user).exists()
        
        # Improved name handling
        name = ""
        if hasattr(other, 'profile'):
            if other.profile.first_name or other.profile.last_name:
                name = f"{other.profile.first_name or ''} {other.profile.last_name or ''}".strip()
        
        if not name:
            name = other.username  # Fallback to username if no profile name
        
        data.append({
            'id': thread.id,
            'participant': {
                'name': name,
                'picture': other.profile.profile_picture.url if hasattr(other, 'profile') and other.profile.profile_picture else None,
                'username': other.username
            },
            'last_message': {
                'content': last_message.content[:30] + '...' if last_message else "",
                'timestamp': timesince(last_message.timestamp) if last_message else ""
            },
            'has_unread': unread,
            'updated': timesince(thread.updated)
        })
    
    return JsonResponse({'threads': data})  


@login_required
def create_new_chat(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Check if thread already exists
        thread = (
        Thread.objects.filter(participant1=request.user, participant2=recipient) |
        Thread.objects.filter(participant1=recipient, participant2=request.user)
        ).first()
        
        if not thread:
            thread = Thread.objects.create(
                participant1=request.user,
                participant2=recipient
            )
        
        return JsonResponse({'thread_id': thread.id})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# @login_required
# def start_direct_chat(request, recipient_id):
#     recipient = get_object_or_404(User, id=recipient_id)
    
#     # Check if thread already exists
#     thread = (
#             Thread.objects.filter(participant1=request.user, participant2=recipient) |
#             Thread.objects.filter(participant1=recipient, participant2=request.user)
#         ).first()
    
#     if not thread:
#         thread = Thread.objects.create(
#             participant1=request.user,
#             participant2=recipient
#         )
    
#     return redirect('chatApp:index')  # Redirect to chat page which will open the thread

@login_required
def start_direct_chat(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    
    # Check if thread already exists
    thread = (
            Thread.objects.filter(participant1=request.user, participant2=recipient) |
            Thread.objects.filter(participant1=recipient, participant2=request.user)
        ).first()
    
    if not thread:
        thread = Thread.objects.create(
            participant1=request.user,
            participant2=recipient
        )
    
    # Redirect back or to chat page with thread opened
    next_url = request.GET.get('next', reverse('chatApp:index'))
    redirect_url = f"{reverse('chatApp:index')}?thread_id={thread.id}"
    
    if next_url != reverse('chatApp:index'):
        redirect_url += f"&next={next_url}"
    
    return redirect(redirect_url)



@login_required
def get_unread_count(request):
    unread_count = Message.objects.filter(
        thread__in=(
            Thread.objects.filter(participant1=request.user) |
            Thread.objects.filter(participant2=request.user)
        ),
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': unread_count})