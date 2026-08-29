from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("messagingApp", "0001_initial"),
    ]

    operations = [
        # --------------------------------------------------
        # PRODUCTION DATABASE ALREADY SYNCHRONIZED
        #
        # The production Supabase database already contains
        # the current Message model schema created by
        # 0001_initial:
        #
        #   recipient_id
        #   body
        #   created_at
        #   subject
        #   message_type
        #   parent_message_id_id
        #   updated_at
        #   sender_id
        #   is_read
        #
        # An older version of this migration attempted to
        # rename legacy columns:
        #
        #   receiver_id -> recipient_id
        #   content     -> body
        #   timestamp   -> created_at
        #
        # Those legacy columns do not exist in the current
        # production database.
        #
        # Therefore this migration intentionally does nothing.
        # It exists only so Django can complete the migration
        # history without attempting to modify the already
        # correct production schema.
        # --------------------------------------------------

        migrations.RunPython(
            code=migrations.RunPython.noop,
            reverse_code=migrations.RunPython.noop,
        ),
    ]