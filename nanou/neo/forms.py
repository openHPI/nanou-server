from django import forms


class NeoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            del kwargs['instance']
        return super(NeoForm, self).__init__(*args, **kwargs)
