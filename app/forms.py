from django import forms
from app.models import Question, User, Answer


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username:
            raise forms.ValidationError('username contains whitespace')
        return username


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = User(**self.cleaned_data)
        if commit:
            user.save()
        return user


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

    def __init__(self, author, question, *args, **kwargs):
        self.author = author
        self.question = question
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = Answer(author=self.author, question=self.question, **self.cleaned_data)
        if commit:
            answer.save()
        return answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']

    def __init__(self, author, *args, **kwargs):
        self.author = author
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        tags = self.cleaned_data.pop('tags')
        question = Question(author=self.author, **self.cleaned_data)
        if commit:
            question.save()
            question.tags.set(tags)
        return question
