
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


# ============================================================
# USER ROLE PROFILE CREATION
# ============================================================

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    """
    Automatically creates the appropriate profile when a new
    User account is created.

    Supported roles:

        admin
        teacher
        pupil
        parent

    IMPORTANT:
    The user-facing role is Pupil.
    The internal Student model is retained for compatibility.

    Multi-school behaviour:
    -----------------------
    User.school is copied to the pupil profile when a pupil
    account is created.

    Teacher and Parent profiles do not currently contain their
    own school ForeignKey, so their school relationship remains
    through User.school.
    """

    if not created:
        return

    try:
        with transaction.atomic():

            # ==================================================
            # ADMIN
            # ==================================================

            if instance.role == "admin":
                logger.info(
                    "Admin user '%s' created. No separate profile required.",
                    instance.username,
                )

            # ==================================================
            # TEACHER
            # ==================================================

            elif instance.role == "teacher":

                teacher, teacher_created = (
                    Teacher.objects.get_or_create(
                        user=instance
                    )
                )

                if teacher_created:
                    logger.info(
                        "Teacher profile created for user '%s'.",
                        instance.username,
                    )

            # ==================================================
            # PUPIL
            # ==================================================

            elif instance.role == "pupil":

                # ------------------------------------------------
                # IMPORTANT:
                #
                # Student.school is REQUIRED.
                #
                # User.school is currently nullable because
                # existing users may not have a school yet.
                #
                # Therefore:
                #
                #   User.school -> Student.school
                #
                # is copied when available.
                # ------------------------------------------------

                if not instance.school_id:
                    logger.warning(
                        "Pupil user '%s' was created without a school. "
                        "Pupil profile was not created because "
                        "Student.school is required.",
                        instance.username,
                    )

                    return

                pupil, pupil_created = (
                    Student.objects.get_or_create(
                        user=instance,
                        defaults={
                            "school_id": instance.school_id,
                            "parent_email": "",
                        },
                    )
                )

                # ------------------------------------------------
                # Existing profile safety
                # ------------------------------------------------

                if not pupil_created:

                    update_fields = []

                    if (
                        pupil.school_id != instance.school_id
                    ):
                        pupil.school_id = instance.school_id
                        update_fields.append("school")

                    if update_fields:
                        pupil.save(
                            update_fields=update_fields
                        )

                if pupil_created:
                    logger.info(
                        "Pupil profile created for user '%s'.",
                        instance.username,
                    )

            # ==================================================
            # PARENT
            # ==================================================

            elif instance.role == "parent":

                parent_profile, parent_created = (
                    Parent.objects.get_or_create(
                        user=instance,
                        defaults={
                            "phone_number": "",
                        },
                    )
                )

                if parent_created:
                    logger.info(
                        "Parent profile created for user '%s'.",
                        instance.username,
                    )

                # ------------------------------------------------
                # AUTOMATIC PUPIL LINKING
                # ------------------------------------------------

                if instance.email:

                    waiting_pupils = Student.objects.filter(
                        parent__isnull=True,
                        parent_email__iexact=instance.email,
                    )

                    linked_count = waiting_pupils.update(
                        parent=parent_profile
                    )

                    if linked_count:
                        logger.info(
                            "Linked %s pupil(s) to parent '%s'.",
                            linked_count,
                            instance.username,
                        )

            # ==================================================
            # UNKNOWN ROLE
            # ==================================================

            else:

                logger.warning(
                    "User '%s' was created with unknown role '%s'.",
                    instance.username,
                    instance.role,
                )

    except Exception:
        logger.exception(
            "Failed creating role profile for user '%s' "
            "with role '%s'.",
            instance.username,
            instance.role,
        )

        # We deliberately do not re-raise here.
        #
        # The User account has already been created.
        # The exception is logged so that the actual problem
        # can be diagnosed without breaking user creation.


# ============================================================
# NOTICE EMAIL NOTIFICATION
# ============================================================

@receiver(post_save, sender=Notice)
def send_notice_email(sender, instance, created, **kwargs):
    """
    Sends a newly created notice to users who have email addresses.

    The signal only runs when the Notice is first created.
    Updating an existing notice does not resend the email.
    """

    if not created:
        return

    recipients = (
        User.objects
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    if not recipients.exists():
        logger.info(
            "Notice %s created but there are no email recipients.",
            instance.id,
        )
        return

    subject = f"Notice: {instance.title}"

    body = (
        "A new notice has been posted.\n\n"
        f"Title: {instance.title}\n\n"
        f"{instance.message}\n\n"
        f"Posted on: "
        f"{instance.created_at:%Y-%m-%d %H:%M}\n\n"
        "Regards,\n"
        "Scholaroid Administration"
    )

    try:

        connection = get_connection(
            fail_silently=False
        )

        emails = []

        for user in recipients:

            greeting_name = (
                user.first_name.strip()
                if user.first_name
                else user.username
            )

            emails.append(
                EmailMessage(
                    subject=subject,
                    body=(
                        f"Hello {greeting_name},\n\n"
                        f"{body}"
                    ),
                    to=[user.email],
                    connection=connection,
                )
            )

        connection.send_messages(emails)

        logger.info(
            "Notice email sent to %s recipient(s) for notice %s.",
            len(emails),
            instance.id,
        )

    except Exception:
        logger.exception(
            "Failed sending notice emails for notice ID %s.",
            instance.id,
        )
