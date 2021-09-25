from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from user_management.models import UserProfile
# from admin_panel.models import Frame_edit_request
from dataframe.models import Frame_edit_request
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,get_object_or_404
from user_management.forms import UserForm, UserUpdateForm, UserProfileForm


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect
from rolepermissions.roles import assign_role
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from rolepermissions.permissions import grant_permission, revoke_permission
from rolepermissions.checkers import has_permission

from django.conf import settings

from admin_panel.views.admin_view import render_permission_denied

def get_user_list(request):
    users = User.objects.filter(is_superuser=0).exclude(id=request.user.id)
    # users = User.objects.all()
    return users

def list(request):
    # users = User.objects.all()
    if has_permission(request.user, 'list_user'):
        users = get_user_list(request)
        return render(request, 'user_management/user_list.html', {'users': users})
    else:
        return render_permission_denied(request)

def save_user_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            permissions = available_perm_status(user).keys()
            req_permissions = request.POST.getlist('permissions[]')
            req_role = request.POST.get('role')
            print(permissions)
            print(req_permissions)
            print(req_role)
            if req_role:
                assign_role(user, req_role)
            for one_permission in permissions:
                if(one_permission in req_permissions):
                    grant_permission(user, one_permission)
                else:
                    revoke_permission(user, one_permission)
            data['form_is_valid'] = True
            users = get_user_list(request)
            data['html_user_list'] = render_to_string('user_management/includes/users/partial_user_list.html', {
                'users': users
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def create(request):
    # print(settings.ROLEPERMISSIONS_MODULE)
    if request.method == 'POST':
        form = UserForm(request.POST)
    else:
        form = UserForm()
    return save_user_form(request, form, 'user_management/includes/users/partial_user_create.html')

def update(request, pk):
    user = get_object_or_404(User, pk=pk)
    # print(dir(get_user_roles(user)))
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
    else:
        form = UserUpdateForm(instance=user)
    if not request.GET._mutable:
        request.GET._mutable = True
    # now you can edit it
    request.GET['permissions'] = available_perm_status(user)
    return save_user_form(request, form, 'user_management/includes/users/partial_user_update.html')

def delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    data = dict()
    if request.method == 'POST':
        user.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        users = get_user_list(request)
        data['html_user_list'] = render_to_string('user_management/includes/users/partial_user_list.html', {
            'users': users
        })
    else:
        context = {'user': user}
        data['html_form'] = render_to_string('user_management/includes/users/partial_user_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)



def edit_profile(request):
    user = get_object_or_404(User, pk=pk)
    data = dict()
    if request.method == 'POST':
        user.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        users = get_user_list(request)
        data['html_user_list'] = render_to_string('user_management/includes/users/partial_user_list.html', {
            'users': users
        })
    else:
        context = {'user': user}
        data['html_form'] = render_to_string('user_management/includes/users/partial_user_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)


def view_profile(request):
    if request.method == 'POST':
        c_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if c_form.is_valid() and p_form.is_valid():
            user = c_form.save()
            profile = p_form.save(commit = False)
            print(profile)
            profile.user = user
            profile.save()
    else:
        if not hasattr(request.user, 'userprofile'):
            UserProfile.objects.create(user=request.user)

        c_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=request.user.userprofile)

    template = loader.get_template('user_management/profile.html')
    context = {'user': request.user, 'cform':c_form, 'pform':p_form}
    response = HttpResponse(template.render(context, request))
    return response


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    template = loader.get_template('user_management/profile.html')
    context = {'user': request.user, 'pass_change_form':form}
    response = HttpResponse(template.render(context, request))
    return response


def edit_requests(request):
    print("dabish"*300)
    if request.method == "POST":
        instance = get_object_or_404(Frame_edit_request, pk=request.POST['pk'])
        user = instance.user.username
        instance.verified = request.POST['verified']
        instance.comment = request.POST['comment']
        instance.save()
        # instance.update(verified=request.POST['verified'], comment=request.POST['comment'])
        return JsonResponse({"user":user})
    else:
        if has_permission(request.user, 'list_user'):
            return render(request, 'user_management/edit_requests.html', {})
        else:
            return render_permission_denied(request)