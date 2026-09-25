"""Instancia compartida del limiter de slowapi, separada de main.py para evitar imports circulares."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
