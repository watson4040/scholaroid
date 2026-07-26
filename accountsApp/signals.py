import logging

from django.core.mail import EmailMessage, get_connection
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from accountsApp.models import Notice, User
from parentsApp.models import Parent
from studentsApp.models import Student
from teachersApp.models import Teacher

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    """
    Automatically creates the appropriate profile for a newly created user.

    Roles:
        - admin
        - teacher
        - pupil
        - parent
    """

    if not created:
        return

    try:
        with transaction.atomic():

            # -----------------------------
            # Teacher
            # -----------------------------
            if instance.role == "teacher":
                Teacher.objects.get_or_create(user=instance)

            # -----------------------------
            # Pupil
            # -----------------------------
            elif instance.role == "pupil":

                Student.objects.get_or_create(
                    user=instance,
                    defaults={
                        "parent_email": ""
                    }
                )

            # -----------------------------
            # Parent
            # -----------------------------
            elif instance.role == "parent":

                parent_profile, created_parent = Parent.objects.get_or_create(
                    user=instance,
                    defaults={
                        "phone_number": ""
                    }
                )

                # Automatically connect pupils waiting for this parent
                if instance.email:

                    waiting_pupils = Student.objects.filter(
                        parent__isnull=True,
                        parent_email__iexact=instance.email
                    )

                    for pupil in waiting_pupils:
                        pupil.parent = parent_profile
                        pupil.save(update_fields=["parent"])

    except Exception:
        logger.exception(
            "Failed creating profile for user '%s' (%s)",
            instance.username,
            instance.role,
        )
        raise


@receiver(post_save, sender=Notice)
def send_notice_email(sender, instance, created, **kwargs):
    """
    Sends a notice email to every user that has an email address.
    """

    if not created:
        return

    recipients = User.objects.exclude(email__isnull=True).exclude(email="")

    if not recipients.exists():
        return

    subject = f"Notice: {instance.title}"

    body = (
        f"A new notice has been posted.\n\n"
        f"Title: {instance.title}\n\n"
        f"{instance.message}\n\n"
        f"Posted on: {instance.created_at:%Y-%m-%d %H:%M}\n\n"
        f"Regards,\n"
        f"Scholaroid Administration"
    )

    try:

        connection = get_connection(fail_silently=False)

        emails = []

        for user in recipients:

            personalised_body = (
                f"Hello {user.first_name or user.username},\n\n"
                f"{body}"
            )

            emails.append(
                EmailMessage(
                    subject=subject,
                    body=personalised_body,
                    to=[user.email],
                    connection=connection,
                )
            )

        connection.send_messages(emails)

    except Exception:
        logger.exception(
            "Failed sending notice emails for notice ID %s",
            instance.id,
        )