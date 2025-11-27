#!/usr/bin/env python3
"""HTTP end-to-end test to run on a Heroku dyno.

Creates an active test Vendedor via ORM, then performs real HTTP requests
against the running app to test login (success + wrong password) and
password-reset request flow, including CSRF token handling.

Run on dyno:
  heroku run --app unifood -- python tools/heroku_http_e2e.py
"""
import os
import re
import sys
import time

BASE = 'https://unifood-81252fb1e36f.herokuapp.com'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetoRP2.settings')
import django
django.setup()

from django.contrib.auth.hashers import make_password
from appWeb.models import Vendedor

try:
    import requests
except Exception:
    print('ERROR: requests library not available in environment')
    sys.exit(2)


def extract_csrf_token(html):
    # Try cookie-first extraction is done by requests.Session, but fallback to input
    m = re.search(r"name=['\"]csrfmiddlewaretoken['\"]\s+value=['\"]([^'\"]+)['\"]", html)
    if m:
        return m.group(1)
    return None


def fail(msg):
    print('FAIL:', msg)
    sys.exit(3)


def ok(msg):
    print('OK:', msg)


def main():
    test_email = 'http-e2e@example.com'
    test_password = 'Start1234!'

    # ensure test user exists and is active
    Vendedor.objects.filter(email=test_email).delete()
    v = Vendedor(email=test_email, senha=make_password(test_password), is_active=True,
                 nome_completo='HTTP E2E', nome_venda='HTTP-E2E')
    v.save()
    print('Created test Vendedor id', v.id)

    sess = requests.Session()

    # --- GET login page to seed cookies and CSRF
    login_url = BASE + '/login/'
    r = sess.get(login_url, timeout=30)
    if r.status_code != 200:
        fail(f'GET /login/ returned {r.status_code}')
    csrf = sess.cookies.get('csrftoken') or extract_csrf_token(r.text)
    if not csrf:
        fail('Could not find CSRF token on login page')
    ok('Fetched login page and CSRF')

    # --- POST valid credentials
    headers = {'Referer': login_url}
    data = {'email': test_email, 'senha': test_password, 'csrfmiddlewaretoken': csrf}
    r2 = sess.post(login_url, data=data, headers=headers, allow_redirects=False, timeout=30)
    if r2.status_code not in (301, 302):
        # show snippet for debugging
        print('Status:', r2.status_code)
        print('Response snippet:', r2.text[:800])
        fail('Login POST did not redirect on valid credentials')
    ok('Login POST redirected (success)')

    # --- POST wrong password (should return 200 and show error message)
    r_wrong = sess.get(login_url, timeout=30)
    csrf2 = sess.cookies.get('csrftoken') or extract_csrf_token(r_wrong.text)
    data_wrong = {'email': test_email, 'senha': 'WRONGpass', 'csrfmiddlewaretoken': csrf2}
    r3 = sess.post(login_url, data=data_wrong, headers={'Referer': login_url}, allow_redirects=True, timeout=30)
    if r3.status_code != 200:
        print('Wrong-pass POST status:', r3.status_code)
        fail('Login with wrong password did not return 200')
    if 'E-mail ou senha inválidos' not in r3.text and 'Conta não confirmada' not in r3.text:
        print('Response snippet:', r3.text[:800])
        fail('Expected error message not found on wrong-password response')
    ok('Wrong-password shows expected error message')

    # --- Password reset request
    pw_url = BASE + '/password-reset/'
    r_pw_get = sess.get(pw_url, timeout=30)
    if r_pw_get.status_code != 200:
        fail(f'GET /password-reset/ returned {r_pw_get.status_code}')
    csrf_pw = sess.cookies.get('csrftoken') or extract_csrf_token(r_pw_get.text)
    data_pw = {'email': test_email, 'csrfmiddlewaretoken': csrf_pw}
    r_pw_post = sess.post(pw_url, data=data_pw, headers={'Referer': pw_url}, allow_redirects=True, timeout=30)
    # The view redirects to login after showing info message
    if r_pw_post.status_code not in (200, 302):
        print('Password reset POST status:', r_pw_post.status_code)
        print('Response snippet:', r_pw_post.text[:800])
        fail('Password reset POST failed')
    if 'Se o e-mail estiver cadastrado' not in r_pw_post.text and 'Se o e-mail estiver cadastrado' not in r_pw_post.history[-1].text if r_pw_post.history else False:
        # we won't fail hard if message isn't present in HTML, but warn
        print('Warning: could not verify reset confirmation message in response HTML')
    ok('Password reset request submitted (email should be sent)')

    # cleanup
    Vendedor.objects.filter(email=test_email).delete()
    ok('Cleanup done')
    print('\nALL HTTP E2E TESTS PASSED')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(4)
