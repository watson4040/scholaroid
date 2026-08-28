from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("messagingApp", "0001_initial"),
    ]

    operations = [

        # --------------------------------------------------
        # EXISTING DATABASE -> CURRENT DJANGO MODEL
        #
        # The existing PostgreSQL table uses:
        #   receiver_id
        #   content
        #   timestamp
        #
        # The current Django model uses:
        #   recipient_id
        #   body
        #   created_at
        #
        # Rename the existing columns so existing messages
        # are preserved.
        # --------------------------------------------------

        migrations.RunSQL(
            sql="""
                ALTER TABLE "messagingApp_message"
                RENAME COLUMN "receiver_id" TO "recipient_id";
            """,
            reverse_sql="""
                ALTER TABLE "messagingApp_message"
                RENAME COLUMN "recipient_id" TO "receiver_id";
            """,
        ),

        migrations.RunSQL(
            sql="""
                ALTER TABLE "messagingApp_message"
                RENAME COLUMN "content" TO "body";
            """,
            reverse_sql="""
                ALTER TABLE "messagingApp_message"
                RENAME COLUMN "body" TO "content";
            """,
        ),

        migrations.RunSQL(
            sql="""
                ALTER TABLE "messagingApp_message"
                RENAME COLUMN "timestamp" TO "created_at";
            """,
            reverse_sql="""
                ALTER TABLE "messagingApp_message"
                RENAME COLUMN "created_at" TO "timestamp";
            """,
        ),

        # --------------------------------------------------
        # COLUMNS REQUIRED BY THE CURRENT MESSAGE MODEL
        # --------------------------------------------------

        migrations.RunSQL(
            sql="""
                ALTER TABLE "messagingApp_message"
                ADD COLUMN IF NOT EXISTS "subject"
                varchar(200) NOT NULL DEFAULT 'Message';

                ALTER TABLE "messagingApp_message"
                ADD COLUMN IF NOT EXISTS "message_type"
                varchar(20) NOT NULL DEFAULT 'other';

                ALTER TABLE "messagingApp_message"
                ADD COLUMN IF NOT EXISTS "parent_message_id_id"
                bigint NULL;

                ALTER TABLE "messagingApp_message"
                ADD COLUMN IF NOT EXISTS "updated_at"
                timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP;
            """,
            reverse_sql="""
                ALTER TABLE "messagingApp_message"
                DROP COLUMN IF EXISTS "updated_at";

                ALTER TABLE "messagingApp_message"
                DROP COLUMN IF EXISTS "parent_message_id_id";

                ALTER TABLE "messagingApp_message"
                DROP COLUMN IF EXISTS "message_type";

                ALTER TABLE "messagingApp_message"
                DROP COLUMN IF EXISTS "subject";
            """,
        ),

        # --------------------------------------------------
        # FOREIGN KEY FOR REPLIES
        # --------------------------------------------------

        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname =
                            'messagingApp_message_parent_message_id_id_fk'
                    )
                    THEN
                        ALTER TABLE "messagingApp_message"
                        ADD CONSTRAINT
                            "messagingApp_message_parent_message_id_id_fk"
                        FOREIGN KEY ("parent_message_id_id")
                        REFERENCES "messagingApp_message" ("id")
                        DEFERRABLE INITIALLY DEFERRED;
                    END IF;
                END
                $$;
            """,
            reverse_sql="""
                ALTER TABLE "messagingApp_message"
                DROP CONSTRAINT IF EXISTS
                    "messagingApp_message_parent_message_id_id_fk";
            """,
        ),
    ]