from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.index, name='dashboard'),
    
    # user management
    path('add_user', views.user_mgmt_add_user, name='add_user'),
    path('view_user', views.user_mgmt_view_user, name='view_user'),
    path("user/edit/<int:user_id>/", views.user_mgmt_edit_user, name="edit_user"),
    path("user/delete/<int:user_id>/", views.user_mgmt_delete_user, name="delete_user"),
    path("block-user/<int:user_id>/", views.user_mgmt_block_user, name="block_user"),
    path("message-user/<int:user_id>/", views.user_mgmt_send_message, name="message_user"),
    path("clear_message/<int:user_id>/", views.user_mgmt_clear_message, name="clear_message"),
    path("company_details/<int:user_id>/", views.user_mgmt_edit_company_details, name="company_details"),
    path("edit_user_data_fetch/<int:user_id>/", views.user_mgmt_edit_user_data_fetch, name="edit_user_data_fetch"),

    # backup
    path('dbbackup', views.dbbackup, name='dbbackup'),
    path('backupscroll', views.backupscroll, name='backupscroll'),
    path('report', views.report, name='report'),
]