"""
Forms for the settings_ui app.

Provides a Django ModelForm for creating and editing ProviderConfiguration records.
"""
import json

from django import forms

from apps.providers.models import ProviderConfiguration


class ProviderConfigurationForm(forms.ModelForm):
    """
    Form for creating or editing a ProviderConfiguration.

    The api_key field uses a password widget so the value is not shown
    in the browser's form auto-fill history.
    The parameters field accepts freeform JSON text.
    """

    api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True, attrs={'autocomplete': 'off'}),
        help_text='Leave blank to keep existing key when editing.',
    )

    parameters_json = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'font-mono text-sm'}),
        label='Parameters (JSON)',
        help_text='Optional provider-specific parameters as a JSON object, e.g. {"temperature": 0.3}',
        initial='{}',
    )

    class Meta:
        model = ProviderConfiguration
        fields = ['provider_type', 'category', 'api_key', 'endpoint', 'model', 'is_active']
        widgets = {
            'endpoint': forms.URLInput(attrs={'placeholder': 'https://api.provider.com/v1'}),
            'model': forms.TextInput(attrs={'placeholder': 'e.g. gpt-4o-mini, whisper-1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate parameters_json from instance data if editing
        if self.instance and self.instance.pk and self.instance.parameters:
            self.fields['parameters_json'].initial = json.dumps(
                self.instance.parameters, indent=2
            )

    def clean_parameters_json(self):
        """Validate that parameters_json is valid JSON."""
        raw = self.cleaned_data.get('parameters_json', '').strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise forms.ValidationError('Parameters must be a JSON object ({...}).')
            return parsed
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f'Invalid JSON: {exc}') from exc

    def save(self, commit=True):
        """Save the form, merging parameters_json into the parameters field."""
        instance = super().save(commit=False)
        instance.parameters = self.cleaned_data.get('parameters_json', {})
        if commit:
            instance.save()
        return instance
