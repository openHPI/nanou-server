from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView

from utils import NeoGraph, get_neo_object_or_404


class NeoListView(ListView):
    def get_queryset(self):
        with NeoGraph() as graph:
            return self.model.select(graph)


class NeoDetailView(DetailView):
    def get_object(self):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            return get_neo_object_or_404(self.model, pk, graph)


class NeoDeleteView(DeleteView):
    def get_object(self):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            return get_neo_object_or_404(self.model, pk, graph)

    def post(self, request, *args, **kwargs):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            obj = get_neo_object_or_404(self.model, pk, graph)
            graph.delete(obj)
            return HttpResponseRedirect(self.success_url)


class NeoCreateView(CreateView):
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'form': form,
            'new_instance': True,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            with NeoGraph() as graph:
                obj = self.model()
                [setattr(obj, k, v) for k, v in form.cleaned_data.items()]
                graph.create(obj)
                return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class NeoUpdateView(UpdateView):
    def get(self, request, *args, **kwargs):
        with NeoGraph() as graph:
            pk = int(self.kwargs.get(self.pk_url_kwarg))
            obj = get_neo_object_or_404(self.model, pk, graph)
            form = self.form_class(obj.value_dict())
            return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            with NeoGraph() as graph:
                pk = int(self.kwargs.get(self.pk_url_kwarg))
                obj = get_neo_object_or_404(self.model, pk, graph)
                for k, v in form.cleaned_data.items():
                    obj.update_prop(k, v)
                graph.push(obj)
                return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})
