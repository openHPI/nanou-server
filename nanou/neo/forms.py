from django import forms

from base.widgets import SemanticUISelectMultiple


class NeoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            del kwargs['instance']
        super(NeoForm, self).__init__(*args, **kwargs)


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
