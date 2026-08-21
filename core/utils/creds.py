"""Resolución de credenciales del campus UBA para los comandos CLI."""

import os
from getpass import getpass

from django.core.management.base import CommandError


def resolve_creds(ci_arg, password_arg):
    """Devuelve (ci, password) usando --ci/--password o las vars de .env.

    - ci: --ci, o UBA_USER_CI; si falta, CommandError.
    - password: --password, o UBA_USER_PASSWD, o prompt seguro.
    """
    ci = ci_arg or os.getenv("UBA_USER_CI")
    if not ci:
        raise CommandError("Debe indicar --ci o definir UBA_USER_CI en .env")

    password = password_arg or os.getenv("UBA_USER_PASSWD") or getpass("Contraseña del campus: ")
    return ci, password
