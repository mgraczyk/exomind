from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from app.site import render_with_globals
from app.users import User

def profile_edit_view(request):
  if request.user.id is None:
    return HttpResponseRedirect('/login')

  update_attempted = False
  update_successful = False

  if request.method == 'GET':
    pass
  elif request.method == 'POST':
    data = request.POST
    update_attempted = True
    try:
      allowed_update_keys = {'username'}
      request.user, _ = User.objects.filter().update_or_create(
          id=request.user.id,
          defaults={k: v for k, v in data.items()if k in allowed_update_keys},
      )
      update_successful = True
    except Exception as e:
      update_successful = False
      print(e)
  else:
    raise HttpResponseForbidden()


  context = {
      'profile_user': request.user,
      'update_attempted': update_attempted,
      'update_successful': update_successful,
  }

  return render_with_globals(request, 'edit_profile.html', context)
