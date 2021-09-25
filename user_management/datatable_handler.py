from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.models import User

# from admin_panel.models import Frame_edit_request
from dataframe.models import Frame_edit_request

from django.apps import apps

from django.utils.html import escape

class TestModelListJson(BaseDatatableView):

    model = Frame_edit_request
   
    columns = ['user', 'id', 'frame', 'col_name', 'old_val', 'new_val']


    max_display_length = 200

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'user':
            # escape HTML for security reasons
            return escape('{0} {1}'.format(row.user.username, row.user.username))
        else:
            return super(TestModelListJson, self).render_column(row, column)

    
    # def get_initial_queryset(self):
    #     frame = self.kwargs['profile']
    #     model = apps.get_model('admin_panel', frame)
    #     return model.objects.all()

    def filter_queryset(self, qs):
        verified = self.request.GET.get('verified', None)
        print(verified)
        qs = qs.filter(verified=verified)
        # search = self.request.GET.get('search[value]', None)
        # if search:
        #     qs = qs.filter(name__istartswith=search)
        # more advanced example using extra parameters
        # filter_customer = self.request.GET.get('customer', None)


    #     if filter_customer:
    #         customer_parts = filter_customer.split(' ')
    #         qs_params = None
    #         for part in customer_parts:
    #             q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
    #             qs_params = qs_params | q if qs_params else q
    #         qs = qs.filter(qs_params)
        return qs