from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView

from utils import NeoGraph, get_neo_object_or_404


class NeoListView(ListView):
    def get_queryset(self):
        with NeoGraph() as graph:
            return self.model.select(graph)


class NeoDetailView(DetailView):
    def get_object(self, queryset=None):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            return get_neo_object_or_404(self.model, pk, graph)


class NeoDeleteView(DeleteView):
    def get_object(self, queryset=None):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            return get_neo_object_or_404(self.model, pk, graph)


class NeoCreateView(CreateView):
    def get_context_data(self, **kwargs):
        if 'is_new_instance' not in kwargs:
            kwargs['is_new_instance'] = True
        return super(NeoCreateView, self).get_context_data(**kwargs)


    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(request.POST)
        if form.is_valid():
            with NeoGraph() as graph:
                model = self.model
                obj = model()
                for k, v in form.cleaned_data.items():
                    obj.update_prop(k, v)
                graph.create(obj)
                return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class NeoUpdateView(UpdateView):
    def get_object(self, queryset=None):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            return get_neo_object_or_404(self.model, pk, graph)

    def get_initial(self):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            obj = get_neo_object_or_404(self.model, pk, graph)
            return obj.value_dict()

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(request.POST)
        if form.is_valid():
            with NeoGraph() as graph:
                obj = self.get_object()
                for k, v in form.cleaned_data.items():
                    obj.update_prop(k, v)
                graph.push(obj)
                return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})
