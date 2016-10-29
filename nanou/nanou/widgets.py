from django import forms
from django.utils.safestring import mark_safe


class SemanticUISelectMultiple(forms.widgets.SelectMultiple):
    class Media:
        js = ('semantic-ui/dist/semantic.min.js',)

    def render(self, name, value, attrs=None):
        html = super(SemanticUISelectMultiple, self).render(name, value, attrs)
        script = '<script type="text/javascript"> \
                $(function() { \
                    $("#%s").dropdown(); \
                }); \
            </script>' % (attrs['id'],)
        return mark_safe(''.join(html + script))
