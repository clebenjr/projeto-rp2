#!/usr/bin/env python3
"""End-to-end smoke test script to run on Heroku dyno.

Creates a test Vendedor, tests login via Django test client, triggers password
reset flow programmatically (generate token), posts new password to the reset
confirm URL, and verifies login with new password.

Prints clear PASS/FAIL messages and exits with non-zero on failures.
"""
import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetoRP2.settings')
import django
django.setup()

from django.contrib.auth.hashers import make_password, check_password
from django.core import signing
from django.urls import reverse
from django.test import Client
from appWeb.models import Vendedor


def fail(msg):
    print('FAIL:', msg)
    sys.exit(2)


def ok(msg):
    print('OK:', msg)


def main():
    test_email = 'heroku-e2e-test@example.com'
    test_password = 'Start1234!'
    new_password = 'Newpass123!'

    # cleanup
    Vendedor.objects.filter(email=test_email).delete()

    # create vendedor (active)
    v = Vendedor(email=test_email, senha=make_password(test_password), is_active=True,
                 nome_completo='E2E Test', nome_venda='E2E')
    v.save()
    print('Created test Vendedor id', v.id)

    client = Client()

    # test login with correct password
    resp = client.post(reverse('login'), {'email': test_email, 'senha': test_password})
    if resp.status_code not in (302, 301):
        print('Login POST did not redirect as expected, status:', resp.status_code)
        print('Response content:', resp.content[:400])
        fail('Login with correct credentials failed')
    ok('Login accepted (redirect)')

    # test login with wrong password (should render login and show message)
    resp2 = client.post(reverse('login'), {'email': test_email, 'senha': 'wrongpass'}, follow=True)
    if resp2.status_code != 200:
        fail('Login with wrong credentials did not return 200')
    content = resp2.content.decode('utf-8')
    if 'E-mail ou senha inválidos' not in content and 'Conta não confirmada' not in content:
        print('Response content snippet:', content[:800])
        fail('Login failure did not show expected error message')
    ok('Login failure displays error message')

    # Password reset flow: generate token and post to confirm view
    token = signing.dumps({'id': v.id}, salt='appWeb-password-reset')
    reset_url = reverse('password_reset_confirm', args=[token])
    resp3 = client.get(reset_url)
    if resp3.status_code != 200:
        print('GET reset page status:', resp3.status_code)
        fail('GET password reset confirm failed')
    ok('Password reset confirm page opened')

    # POST new password
    resp4 = client.post(reset_url, {'senha': new_password, 'senha_conf': new_password}, follow=True)
    if resp4.status_code not in (200, 302):
        fail('POST password reset confirm failed')
    v.refresh_from_db()
    if not check_password(new_password, v.senha):
        fail('Password was not updated in DB')
    ok('Password reset confirmed and saved')

    # verify login with new password
    resp5 = client.post(reverse('login'), {'email': test_email, 'senha': new_password})
    if resp5.status_code not in (301, 302):
        fail('Login after reset failed')
    ok('Login after reset succeeded')

    # cleanup
    Vendedor.objects.filter(email=test_email).delete()
    ok('Cleanup done')
    print('\nALL E2E TESTS PASSED')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(3)
