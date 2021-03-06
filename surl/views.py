from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _

from surl.models import Surl, Profile


def index_view(request):
    if request.user.is_authenticated():
        try:
            request.user.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=request.user)
    return render(request, 'surl/index.html', {})


def api_create_surl(request):
    url = request.POST.get('url')
    if not url:
        return JsonResponse({'error': 'empty URL'})
    if '.' not in url:
        return JsonResponse({'error': 'Invalid URL'})
    if '//' not in url:
        url = 'http://{}'.format(url)
    password = request.POST.get('password', '')
    surl = Surl.create_surl(url=url, user_id=request.user.pk, password=password)
    return JsonResponse({'surl': surl.slug})


def create_surl_view(request):  # If javascript is not enabled, fall back to this view
    if request.method == 'GET':
        return HttpResponse('Not Allowed', status=405)
    url = request.POST.get('url')
    password = request.POST.get('password', '')
    if not url:
        messages.add_message(request, messages.WARNING, _('URL cannot be empty'))
        return HttpResponseRedirect(reverse('index'))
    if '.' not in url:
        messages.add_message(request, messages.WARNING, _('URL is invalid'))
        return HttpResponseRedirect(reverse('index'))
    if '//' not in url:
        url = 'http://{}'.format(url)
    surl = Surl.create_surl(url=url, user_id=request.user.pk, password=password)
    return render(request, 'surl/index.html', {'surl': surl})


def my_surl_view(request):
    if not request.user.is_authenticated():
        messages.add_message(request, messages.error, _('Please log in first'))
        return HttpResponseRedirect(reverse('auth_login'))
    try:
        request.user.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user)
    return render(request, 'surl/my.html', {'title': _('My short URLs')})


def go_to_url(request, slug):
    explicit_redirect = getattr(settings, 'EXPLICIT_REDIRECT', False)
    surl = Surl.objects.filter(slug=slug).first()
    if not surl:
        return HttpResponseRedirect('/')
    else:
        surl.increase_count()
    if explicit_redirect:
        return render(request, 'surl/redirect.html', {'title': _('Redirecting'), 'surl': surl})
        # pass  # TODO: explicit redirection
    else:
        return HttpResponseRedirect(surl.url)
