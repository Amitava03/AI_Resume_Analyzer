from django import forms

from resumes.models import Resume


class InterviewSetupForm(forms.Form):
    target_role = forms.CharField(max_length=200)
    resume = forms.ModelChoiceField(queryset=Resume.objects.none(), required=False)
    difficulty = forms.ChoiceField(
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        initial="medium",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resume"].queryset = Resume.objects.filter(user=user)


class AnswerForm(forms.Form):
    answer_text = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))
