from django.contrib import admin

from app.models import Question, User, Answer, Tag, Rating

admin.site.register(Question)
admin.site.register(User)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Rating)
