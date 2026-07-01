# ============================================================================
# JAZZMIN ADMIN THEME SETTINGS
# ============================================================================

JAZZMIN_SETTINGS = {
    "site_title": "Scholaroid Admin",
    "site_header": "Scholaroid",
    "site_brand": "Scholaroid School Management",
    "welcome_sign": "Welcome to Scholaroid Admin",
    "copyright": "Scholaroid Ltd",

    "show_sidebar": True,
    "navigation_expanded": True,

    "sidebar_fixed": True,
    "navbar_fixed": True,
    "footer_fixed": False,

    "navigation_sticky": True,
    "navbar_sticky": True,

    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",

    "topmenu_links": [
        {
            "name": "Dashboard",
            "url": "/dashboard/admin/",
            "permissions": ["auth.view_user"]
        },
        {
            "name": "Home",
            "url": "admin:index",
            "permissions": ["auth.view_user"]
        }
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "accountsApp.User": "fas fa-user",
        "studentsApp.Student": "fas fa-user-graduate",
        "teachersApp.Teacher": "fas fa-chalkboard-teacher",
        "parentsApp.Parent": "fas fa-users",
        "classesApp.Class": "fas fa-school",
        "attendanceApp.Attendance": "fas fa-calendar-check",
        "feesApp.Fee": "fas fa-money-bill-wave",
        "examsApp.Exam": "fas fa-file-alt",
        "messagingApp.Message": "fas fa-envelope",
        "resourcesApp.Resource": "fas fa-book",
    },
}