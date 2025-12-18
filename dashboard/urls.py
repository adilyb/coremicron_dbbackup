from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.index, name='dashboard'),
    path('add_user', views.add_user, name='add_user'),
    path('dbbackup', views.dbbackup, name='dbbackup'),
    path('backupscroll', views.backupscroll, name='backupscroll'),
    path('report', views.report, name='report'),
    path('user_view', views.view_user, name='view_user'),
    path("user/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("user/delete/<int:user_id>/", views.delete_user, name="delete_user"),


]