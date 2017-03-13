from django import forms

from base.widgets import SemanticUISelectMultiple


class NeoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
            del kwargs['instance']
        super(NeoForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NeoForm, self).clean()
        msg = 'Cannot reference itself.'
        for field_name, field in self.declared_fields.items():
            if isinstance(field, NeoRelationshipNoSelfRefField):
                cleaned_field_data = cleaned_data.get(field_name)
                if str(self.instance.id) in cleaned_field_data:
                    self.add_error(field_name, msg)


class NeoRelationshipField(forms.ModelMultipleChoiceField):
    def __init__(self, model, label, initial=None, required=False, widget=None):
        self.model = model
        initial = [] if initial is None else initial
        widget = SemanticUISelectMultiple() if widget is None else widget

        super(NeoRelationshipField, self).__init__(
            model,
            label=label,
            initial=initial,
            required=required,
            widget=widget,
        )

    def _get_choices(self):
        return sorted([(m.id, m.name) for m in self.model.all()], key=lambda e: e[0])

    choices = property(_get_choices, forms.ModelMultipleChoiceField._set_choices)

    def clean(self, value):
        value = [int(v) for v in value] if isinstance(value, list) else value
        return self.model.getAll(value)


class NeoRelationshipNoSelfRefField(NeoRelationshipField):
    pass
