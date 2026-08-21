"""Tests de los shims de compatibilidad con django-q."""

import django_q.core_signing
from django.test import SimpleTestCase
from django.utils import baseconv

from uba_assistant.settings import CompatTimestampSigner


class BaseconvShimTests(SimpleTestCase):
    """El módulo django.utils.baseconv restaurado funciona."""

    def test_base62_round_trip(self):
        self.assertEqual(baseconv.base62.encode(12345), "3D7")
        self.assertEqual(baseconv.base62.decode("3D7"), 12345)


class TimestampSignerShimTests(SimpleTestCase):
    """django-q usa el CompatTimestampSigner parcheado."""

    def test_signer_es_el_compatible(self):
        self.assertIs(django_q.core_signing.TimestampSigner, CompatTimestampSigner)

    def test_round_trip_con_la_convencion_de_django_q(self):
        # django-q llama TimestampSigner(key, salt=salt) en core_signing.loads
        signer = django_q.core_signing.TimestampSigner("clave-secreta", salt="django.core.signing")
        signed = signer.sign(12345)
        self.assertEqual(signer.unsign(signed), "12345")
        self.assertEqual(signer.unsign(signed, max_age=None), "12345")
        self.assertEqual(signer.unsign(signed, max_age=3600), "12345")
