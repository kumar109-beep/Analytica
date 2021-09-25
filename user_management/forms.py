from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class UserForm(UserCreationForm):
    username = forms.CharField(max_length=30,label='Username*', )
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.',widget=forms.TextInput(attrs={'autocomplete':'off'}))
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.',widget=forms.TextInput(attrs={'autocomplete':'off'}))
    password1 = forms.CharField(label=("Password*"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation*"), widget=forms.PasswordInput)
    email = forms.EmailField(max_length=254,label='Email*', help_text='Required. Inform a valid email address.')
    role = forms.CharField(
    required=True,
    label='Role*',
    widget=forms.Select(
        choices= [('','')]
        )
     )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget.choices = [('', '--Select Role--')] + [(group.name, group.name.title() ) for group in Group.objects.all()]
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'email', 'password1', 'password2', )

    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError('This email address is already Exist')
        else:
            return self.cleaned_data['email']

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        # Add all the fields you want a user to change
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError('This email address is already Exist')
        else:
            return self.cleaned_data['email']
        


from django.core.files.images import get_image_dimensions

from user_management.models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 800
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels or smaller.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')

            #validate file size
            if len(avatar) > (100 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 100k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar
