from django.shortcuts import render, redirect
from .models import Users
import subprocess
import tempfile
import os
from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Users
from django.db.models import Q
import json
from pathlib import Path
from django.shortcuts import get_object_or_404, redirect
from .get_backup import backup_mysql
from datetime import datetime
from django.contrib import messages
from django.core.paginator import Paginator


BACKUP_JSON_PATH = Path("backup_data/backups.json")

def index(request):
    return render(request, 'dashboard/index.html')

def view_user(request):
    query = request.GET.get('q', '')
    
    # Filter users if search query exists
    if query:
        users_list = Users.objects.filter(customer_name__icontains=query)
    else:
        users_list = Users.objects.all()
    
    # Paginate the queryset (10 users per page, adjust as needed)
    paginator = Paginator(users_list, 7)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    return render(request, "dashboard/view_user.html", {'users':users})

def block_user(request, user_id):

    user = get_object_or_404(Users, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect("view_user")
    
    
def dbbackup(request):
        q = request.GET.get("q", "").strip()
    
        users_list = Users.objects.all()
    
        if q:
            users_list = users_list.filter(
                Q(software_name__icontains=q) |
                Q(customer_name__icontains=q) |
                Q(ip_address__icontains=q)
            )
    
        # load backup metadata
        backup_lookup = {}
    
        if BACKUP_JSON_PATH.exists():
            with open(BACKUP_JSON_PATH, "r") as f:
                items = json.load(f)
            for item in items:
                ts = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")
                backup_lookup[item["database"]] = ts
    
        
        # attach last_backup property to each user obj
        for u in users_list:
            db = u.db_name
            print(db)             
            u.last_backup = backup_lookup.get(db)
            print(u.last_backup)
        paginator = Paginator(users_list, 7)
        page_number = request.GET.get("page")
        users = paginator.get_page(page_number)
    
        return render(request, "dashboard/dbbackup.html", {"users": users})

def add_user(request):
    if request.method == "POST":
        Users.objects.create(
            customer_name=request.POST.get("customer_name"),
            software_name=request.POST.get("software_name"),
            ip_address=request.POST.get("ip_address"),
            db_username=request.POST.get("db_username"),
            db_name=request.POST.get("db_name"),
            db_pass=request.POST.get("db_pass"),
        )
        return redirect("add_user")

    return render(request, "dashboard/add_user.html")

def edit_user(request, user_id):
    user = get_object_or_404(Users, id=user_id)

    if request.method == "POST":
        user.customer_name = request.POST.get("customer_name")
        user.software_name = request.POST.get("software_name")
        user.ip_address = request.POST.get("ip_address")
        user.db_username = request.POST.get("db_username")
        user.db_name = request.POST.get("db_name")
        user.db_pass = request.POST.get("db_pass")
        user.save()

        messages.success(request, "User updated successfully")
        return redirect("view_user") 
    return render(request, "dashboard/edit_user.html", {'user':user})

def delete_user(request, user_id):
    user = get_object_or_404(Users, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully")
    return redirect("view_user")


def dbbackup(request):
    q = request.GET.get("q", "").strip()

    users_list = Users.objects.all()

    if q:
        users_list = users_list.filter(
            Q(software_name__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(ip_address__icontains=q)
        )

    # load backup metadata
    backup_lookup = {}

    if BACKUP_JSON_PATH.exists():
        with open(BACKUP_JSON_PATH, "r") as f:
            items = json.load(f)

        for item in items:
            ts = datetime.strptime(item["timestamp"], "%Y%m%d_%H%M%S")
            backup_lookup[item["database"]] = ts

    
    # attach last_backup property to each user obj
    for u in users_list:
        db = u.db_name
        u.last_backup = backup_lookup.get(db)
    paginator = Paginator(users_list, 7)
    page_number = request.GET.get("page")
    users = paginator.get_page(page_number)

    return render(request, "dashboard/dbbackup.html", {"users": users})


def backupscroll(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = get_object_or_404(Users, id=user_id)
        ip_address = user.ip_address
        db_name = user.db_name
        db_user = user.db_username
        db_pass = user.db_pass


        backup_mysql(
            ip_address,
            db_name,
            db_user,
            db_pass
        )

        return redirect("dbbackup")
    
def report(request):
    if BACKUP_JSON_PATH.exists():
        with BACKUP_JSON_PATH.open() as f:
            backups = json.load(f)
    else:
        backups = []

    date_filter = request.GET.get("date")
    search_query = request.GET.get("q", "").strip().lower()

    filtered = backups

    # filter by date
    if date_filter:
        temp = []
        for b in filtered:
            ts = datetime.strptime(b["timestamp"], "%Y%m%d_%H%M%S")
            formatted_date = ts.strftime("%Y-%m-%d")
            if formatted_date == date_filter:
                temp.append(b)
        filtered = temp

    # filter by search text
    if search_query:
        filtered = [
            b for b in filtered
            if search_query in b["database"].lower()
            or search_query in b["file_name"].lower()
            or search_query in b["file_path"].lower()
            or search_query in b["timestamp"].lower()
        ]

    for b in filtered:
        try:
            dt = datetime.strptime(b["timestamp"], "%Y%m%d_%H%M%S")
            b["display_timestamp"] = dt.strftime("%d %b %Y %H:%M:%S")
        except:
            b["display_timestamp"] = b["timestamp"]

    # pagination
    paginator = Paginator(filtered, 6) 
    page_number = request.GET.get("page") 
    page_obj = paginator.get_page(page_number) 

    return render(request, "dashboard/report.html", {"backups": page_obj})