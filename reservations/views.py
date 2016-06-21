from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone, dateparse
from .models import Reservation, Field
from reservations import rutils
from datetime import datetime, timedelta


def index(request):
    fields = Field.objects.all()
    return render(request, 'reservations/index.html', {'fields': fields, })


class FieldDetailViewModel():
    def __init__(self, res_date):
        self.res_date = res_date
        self.today = dateparse.parse_date(res_date) if res_date else timezone.now()
        self.res_date_previous = timezone.datetime(self.today.year, self.today.month, self.today.day-1, 0).strftime("%Y-%m-%d")
        self.res_date_next = timezone.datetime(self.today.year, self.today.month, self.today.day+1, 0).strftime("%Y-%m-%d")


def field_detail(request, field_id):
    return field_detail_date(request, field_id, None)


def field_detail_date(request, field_id, res_date):
    field = Field.objects.get(id=field_id)
    reservations = rutils.get_reservations(field_id, res_date)
    fdvm = FieldDetailViewModel(res_date)
    hours2res = dict.fromkeys(range(24))
    for reservation in reservations:
        hours2res[reservation.time.hour] = reservation
    return render(request, 'reservations/field_detail.html', {'field_id': field_id, 'field': field, 'res_date': res_date,
                                                              'hours2res':hours2res, 'fdvm':fdvm })


def field_reserve(request, field_id, reservation_time):
    return field_reserve_date(request, field_id, None, reservation_time)


def field_reserve_date(request, field_id, res_date, reservation_time):
    rutils.create_reservation(field_id, res_date, reservation_time, None if request.user.is_anonymous() else request.user)
    if res_date:
        return HttpResponseRedirect(reverse('reservations:field.detail.date', kwargs={'field_id': field_id, 'res_date':res_date}))
    else :
        return HttpResponseRedirect(reverse('reservations:field.detail', kwargs={'field_id': field_id}))

