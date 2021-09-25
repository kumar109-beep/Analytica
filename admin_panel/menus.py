from django.core.urlresolvers import reverse
# from django.urls import reverse
# from menu import Menu, MenuItem


Menu.add_item("main", MenuItem("Reports Index",
                               reverse("admin_panel.views.admin_view.get_head_vals")))

# Menu.add_item("main", MenuItem("Staff Only",
#                                reverse("reports.views.staff"),
#                                check=lambda request: request.user.is_staff))

# Menu.add_item("main", MenuItem("Superuser Only",
#                                reverse("reports.views.superuser"),
#                                check=lambda request: request.user.is_superuser))



# from django.urls import reverse
# reverse("admin_panel.views.admin_view.get_head_vals")