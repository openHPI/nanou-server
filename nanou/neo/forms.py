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


class NeoRelationshipField(forms.MultipleChoiceField):
    def __init__(self, model, label, initial=None, required=False, widget=None):
        initial = [] if initial is None else initial
        widget = SemanticUISelectMultiple() if widget is None else widget

        super(NeoRelationshipField, self).__init__(
            label=label,
            choices=[(m.id, m.name) for m in model.all()],
            initial=initial,
            required=required,
            widget=widget,
        )

    def clean(self, value):
        value = [int(v) for v in value] if isinstance(value, list) else value
        return super(NeoRelationshipField, self).clean(value)


class NeoRelationshipNoSelfRefField(NeoRelationshipField):
    pass
