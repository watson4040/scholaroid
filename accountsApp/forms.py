from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation

from parentsApp.models import Parent
from .models import Notice


User = get_user_model()


# ============================================================
# ADMIN REGISTRATION
# ============================================================

class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()

        if "@" not in email:
            raise forms.ValidationError(
                "Enter a valid email address."
            )

        local_part = email.split("@", 1)[0].lower()

        if ".admin" not in local_part:
            raise forms.ValidationError(
                "Not an authorized admin email."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = "admin"
        user.is_staff = True
        user.is_superuser = True

        if commit:
            user.save()

        return user


# ============================================================
# TEACHER REGISTRATION
# ============================================================

class TeacherRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()

        if "@" not in email:
            raise forms.ValidationError(
                "Enter a valid email address."
            )

        local_part = email.split("@", 1)[0].lower()

        if ".teacher" not in local_part:
            raise forms.ValidationError(
                "Not an authorized teacher email."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = "teacher"

        if commit:
            user.save()

        return user


# ============================================================
# PUPIL REGISTRATION
# ============================================================

class StudentRegistrationForm(UserCreationForm):
    """
    The internal class name remains StudentRegistrationForm
    for compatibility.

    IMPORTANT:
    The actual User role is "pupil", never "student".
    """

    parent_email = forms.EmailField(
        required=False,
        label="Parent Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Parent's email (optional)",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "parent_email",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        # IMPORTANT:
        # User.ROLE_CHOICES uses "pupil".
        user.role = "pupil"

        if commit:
            user.save()

            # A signal should normally create the Student/Pupil
            # profile automatically after the user is saved.
            from studentsApp.models import Student

            parent_email = self.cleaned_data.get("parent_email")

            if parent_email:
                try:
                    pupil = Student.objects.get(user=user)

                    pupil.parent_email = parent_email.strip().lower()
                    pupil.save(update_fields=["parent_email"])

                except Student.DoesNotExist:
                    # The user was created successfully, but the
                    # pupil profile has not yet been created.
                    # Do not destroy the user account.
                    pass

        return user


# ============================================================
# PARENT REGISTRATION
# ============================================================

class ParentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = "parent"

        if commit:
            user.save()

        return user


# ============================================================
# NOTICE FORM
# ============================================================

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = [
            "title",
            "message",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Notice title",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Write your notice...",
                }
            ),
        }


# ============================================================
# PROFILE FORM
# ============================================================

class ProfileForm(forms.ModelForm):

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Mobile Number",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter mobile number",
            }
        ),
    )

    profile_photo = forms.ImageField(
        required=False,
        label="Profile Photo",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "profile_photo",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.instance

        if user and getattr(user, "role", None) == "parent":

            try:
                parent = Parent.objects.get(user=user)

                self.fields["phone_number"].initial = (
                    parent.phone_number
                )

            except Parent.DoesNotExist:
                pass

        else:
            self.fields.pop("phone_number", None)

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")

        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Image must be 5MB or smaller."
            )

        return photo

    def save(self, commit=True):
        user = super().save(commit=commit)

        if (
            getattr(user, "role", None) == "parent"
            and "phone_number" in self.cleaned_data
        ):
            parent, _ = Parent.objects.get_or_create(
                user=user
            )

            parent.phone_number = (
                self.cleaned_data.get("phone_number") or ""
            )

            parent.save()

        return user


# ============================================================
# CHANGE PASSWORD FORM
# ============================================================

class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter current password",
            }
        ),
        required=True,
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new password",
            }
        ),
        required=True,
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
            }
        ),
        required=True,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data.get(
            "current_password"
        )

        if not self.user.check_password(current_password):
            raise forms.ValidationError(
                "Current password is incorrect."
            )

        return current_password

    def clean(self):
        cleaned_data = super().clean()

        current_password = cleaned_data.get(
            "current_password"
        )

        password1 = cleaned_data.get(
            "new_password1"
        )

        password2 = cleaned_data.get(
            "new_password2"
        )

        if password1 and password2:

            if password1 != password2:
                self.add_error(
                    "new_password2",
                    "Passwords do not match.",
                )

            if (
                current_password
                and password1 == current_password
            ):
                self.add_error(
                    "new_password1",
                    "New password cannot be the same as the current password.",
                )

            if not self.errors.get("new_password1"):
                password_validation.validate_password(
                    password1,
                    self.user,
                )

        return cleaned_data