from celery.result import BaseAsyncResult

from django.shortcuts import render, render_to_response
from django.template import RequestContext

from models import Download

@login_required
def downloads_list(request):
    expected_downloads = Download.objects.filter(user=request.user, status="expected")
    for d in expected_downloads:
        task = BaseAsyncResult(d.task_id)
        if task.ready():
            if task.successful():
                d.file_path = task.result
                d.status = 'complite'
            else:
                # TODO
                status = task.status
                pass
            d.save()

    downloads = Download.objects.filter(user=request.user).order_by('-created')

    return render_to_response("download_list.html", {'downloads': downloads},
        context_instance=RequestContext(request))