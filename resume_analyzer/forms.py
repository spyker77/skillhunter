from django import forms


class UploadResumeForm(forms.Form):
    resume = forms.FileField(
        label=False,
        required=False,
        widget=forms.HiddenInput(
            attrs={
                "type": "file",
                "id": "resume",
                "accept": ".pdf",
                "class": "hidden",
            }
        ),
    )
