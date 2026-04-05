#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings_local')
sys.path.insert(0, 'd:\\TicketManagement\\backend')

django.setup()

from django.contrib.auth.models import User

users_data = [
    {'username': 'customer_demo', 'password': 'Demo@12345', 'is_staff': False},
    {'username': 'staff_demo', 'password': 'Demo@12345', 'is_staff': True},
    {'username': 'admin_demo', 'password': 'Demo@12345', 'is_staff': True},
]

for user_info in users_data:
    if not User.objects.filter(username=user_info['username']).exists():
        User.objects.create_user(
            username=user_info['username'],
            password=user_info['password'],
            is_staff=user_info['is_staff'],
            is_superuser=(user_info['username'] == 'admin_demo')
        )
        print(f"✓ Created: {user_info['username']}")
    else:
        user = User.objects.get(username=user_info['username'])
        user.set_password(user_info['password'])
        user.is_staff = user_info['is_staff']
        user.is_superuser = (user_info['username'] == 'admin_demo')
        user.save()
        print(f"✓ Updated: {user_info['username']}")

print("\nAll test users ready!")
