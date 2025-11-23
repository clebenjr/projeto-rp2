#!/usr/bin/env python3
import os
import traceback
import socket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetoRP2.settings')
import django
django.setup()

from django.conf import settings

def print_settings():
    print('---- Django email settings ----')
    print('EMAIL_BACKEND:', getattr(settings, 'EMAIL_BACKEND', None))
    print('DEFAULT_FROM_EMAIL:', getattr(settings, 'DEFAULT_FROM_EMAIL', None))
    print('EMAIL_HOST (from settings):', getattr(settings, 'EMAIL_HOST', None))
    print('EMAIL_PORT (from settings):', getattr(settings, 'EMAIL_PORT', None))
    print('EMAIL_HOST_USER (from settings):', getattr(settings, 'EMAIL_HOST_USER', None))
    print('EMAIL_HOST_PASSWORD_PRESENT:', bool(os.environ.get('EMAIL_HOST_PASSWORD')))
    print('SENDGRID_API_KEY present:', bool(os.environ.get('SENDGRID_API_KEY')))

def try_send_mail():
    from django.core.mail import send_mail
    try:
        print('\nCalling send_mail()...')
        n = send_mail('Teste UniFood', 'Corpo do teste', settings.DEFAULT_FROM_EMAIL, ['email.unifood@gmail.com'], fail_silently=False)
        print('send_mail returned:', n)
    except Exception:
        print('--- send_mail exception traceback ---')
        traceback.print_exc()

def tcp_tests():
    for host, port in [('smtp.gmail.com', 587), ('smtp.gmail.com', 465)]:
        try:
            print('\nTesting TCP connect to %s:%s' % (host, port))
            s = socket.create_connection((host, port), 10)
            print('TCP connected from', s.getsockname())
            s.close()
        except Exception:
            print('--- TCP exception for %s:%s ---' % (host, port))
            traceback.print_exc()

def main():
    print_settings()
    try_send_mail()
    tcp_tests()

if __name__ == '__main__':
    main()
