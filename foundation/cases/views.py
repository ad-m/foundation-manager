from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from braces.views import (SelectRelatedMixin, LoginRequiredMixin, FormValidMessageMixin,
                          UserFormKwargsMixin)
from django.core.urlresolvers import reverse_lazy
from django_filters.views import FilterView
from atom.views import DeleteMessageMixin, FormInitialMixin
from .models import Case
from .forms import CaseForm, NewCaseForm
from .filters import CaseFilter
from foundation.letters.models import Letter


class CaseListView(SelectRelatedMixin, FilterView):
    filterset_class = CaseFilter
    model = Case
    select_related = ['created_by', 'office', 'office__jst']
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        qs = super(CaseListView, self).get_queryset(*args, **kwargs)
        return qs


class CaseDetailView(SelectRelatedMixin, DetailView):
    model = Case
    select_related = ['created_by', 'office']

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        context['letter_list'] = Letter.objects.filter(case=self.object).for_list().all()
        return context


class CaseCreateView(LoginRequiredMixin, FormInitialMixin, UserFormKwargsMixin, CreateView):
    model = Case
    form_class = NewCaseForm

    def get_form_valid_message(self):
        return _("{0} created!").format(self.object)


class CaseUpdateView(LoginRequiredMixin, UserFormKwargsMixin,  FormValidMessageMixin,
                     UpdateView):
    model = Case
    form_class = CaseForm

    def get_form_valid_message(self):
        return _("{0} updated!").format(self.object)


class CaseDeleteView(LoginRequiredMixin, DeleteMessageMixin, DeleteView):
    model = Case
    success_url = reverse_lazy('cases:list')

    def get_success_message(self):
        return _("{0} deleted!").format(self.object)
