from django import forms

from .models import Resume


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["title", "file", "target_role"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Software Engineer Resume"}),
            "target_role": forms.TextInput(attrs={"placeholder": "e.g. Python Developer"}),
            "file": forms.FileInput(attrs={"accept": ".pdf,.docx,.doc"}),
        }

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        name = uploaded.name.lower()
        if not (name.endswith(".pdf") or name.endswith(".docx") or name.endswith(".doc")):
            raise forms.ValidationError("Only PDF and DOCX files are supported.")
        if uploaded.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 5 MB.")
        return uploaded


class JobMatchForm(forms.Form):
    job_title = forms.CharField(max_length=200)
    job_description = forms.CharField(widget=forms.Textarea(attrs={"rows": 8}))
