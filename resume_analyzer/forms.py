from django import forms


class UploadResumeForm(forms.Form):
    file = forms.FileField(
        label=False,
        required=False,
        widget=forms.FileInput(
            attrs={
                "type": "file",
                "id": "resume",
                "accept": ".pdf",
                "class": "hidden",
                "aria-describedby": "resume-help",
            }
        ),
    )
