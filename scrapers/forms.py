from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter desired job title",
                "aria-label": "Search",
                "aria-describedby": "search-help",
                "autofocus": "autofocus",
            }
        ),
    )
