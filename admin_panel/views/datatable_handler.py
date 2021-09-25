from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.models import User

from django.apps import apps

class TestModelListJson(BaseDatatableView):

    model = User
   
    # def get_initial_queryset(self):
    #     frame = self.kwargs['profile']
    #     model = apps.get_model('admin_panel', frame)
    #     return model.objects.all()

    # def filter_queryset(self, qs):
    #     search = self.request.GET.get('search[value]', None)
    #     if search:
    #         qs = qs.filter(name__istartswith=search)

    #     # more advanced example using extra parameters
    #     filter_customer = self.request.GET.get('customer', None)


    #     if filter_customer:
    #         customer_parts = filter_customer.split(' ')
    #         qs_params = None
    #         for part in customer_parts:
    #             q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
    #             qs_params = qs_params | q if qs_params else q
    #         qs = qs.filter(qs_params)
    #     return qs