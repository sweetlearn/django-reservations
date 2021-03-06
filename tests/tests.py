from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from reservations.models import Venue, Field, Reservation
from reservations import rutils


class IndexViewTests(TestCase):
    def test_index_view_basic(self):
        """
        Basic test index view.
        """
        response = self.client.get(reverse('reservations:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservations")


class FieldViewTests(TestCase):
    def setUp(self):
        venue01 = Venue.objects.create(name="VenueFieldTest01")
        Field.objects.create(name="FieldReservationdTest01", venue=venue01)

    def test_field_detail(self):
        response = self.client.get(reverse('reservations:field.detail', kwargs={'field_id':1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservations")

    def test_field_reserve(self):
        url_reserve_5 = reverse('reservations:field.reserve.date',
                                kwargs={'field_id': 1, 'res_date': timezone.now().strftime("%Y-%m-%d"), 'reservation_time': 5,})
        url_reserve_6 = reverse('reservations:field.reserve.date',
                                kwargs={'field_id': 1, 'res_date': timezone.now().strftime("%Y-%m-%d"), 'reservation_time': 6,})
        #get field detail. both links should be present
        response = self.client.get(reverse('reservations:field.detail', kwargs={'field_id':1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, url_reserve_5)
        self.assertContains(response, url_reserve_6)
        #reserve hour 5, links to 5 should not be present anymore in response
        response = self.client.get(reverse('reservations:field.reserve', kwargs={'field_id': 1, 'reservation_time': 5,}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('reservations:field.detail', kwargs={'field_id':1}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, url_reserve_5)
        self.assertContains(response, url_reserve_6)

class ReservationsTest(TestCase):
    def setUp(self):
        venue01 = Venue.objects.create(name="VenueFieldTest01")
        field = Field.objects.create(name="FieldReservationdTest01", venue=venue01)
        rutils.create_reservation(field.id, "2016-06-22", 1, None)

    def test_reservations(self):
        url = reverse('reservations:reservations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reservation_detail(self):
        url = reverse('reservations:reservation.detail', kwargs={'reservation_id':1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reservation_delete(self):
        url = reverse('reservations:reservation.delete', kwargs={'reservation_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class VenuesViewTest(TestCase):
    def setUp(self):
        pass

    def test_no_venue(self):
        response = self.client.get(reverse('reservations:venues'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No venues yet.")

    def test_1_venue(self):
        venue01 = Venue.objects.create(name="VenueFieldTest01")
        venue02= Venue.objects.create(name="VenueFieldTest02")
        venue03 = Venue.objects.create(name="VenueFieldTest03")
        response = self.client.get(reverse('reservations:venues'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No venues yet.")
        self.assertContains(response, "VenueFieldTest01")
        self.assertContains(response, "VenueFieldTest02")
        self.assertContains(response, "VenueFieldTest03")


class VenueDetailViewTest(TestCase):
    def setUp(self):
        venue01 = Venue.objects.create(name="VenueFieldTest01")
        field11 = Field.objects.create(name="FieldReservationdTest11", venue=venue01)
        field12 = Field.objects.create(name="FieldReservationdTest12", venue=venue01)
        venue02 = Venue.objects.create(name="VenueFieldTest02")
        field21 = Field.objects.create(name="FieldReservationdTest21", venue=venue02)

    def test_detail_simple(self):
        response = self.client.get(reverse('reservations:venue.detail', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FieldReservationdTest11")
        self.assertContains(response, reverse('reservations:field.detail', kwargs={'field_id':1}))
        self.assertNotContains(response, "FieldReservationdTest21")
