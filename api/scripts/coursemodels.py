from mongoengine import *


class CourseMeeting(EmbeddedDocument):
    days_of_week = ListField(StringField(max_length=1))
    start_time = StringField()
    end_time = StringField()
    duration = ListField(StringField())
    location = StringField()


# TODO: What is the best way to do this? References?
class CourseInstructor(EmbeddedDocument):
    name = StringField()
    email = StringField()
    isPrimary = BooleanField()


class BannerCourse(DynamicDocument):
    creation_date = DateTimeField()
    number = StringField(required=True)
    full_number = StringField(required=True)
    dept = StringField(required=True, min_length=3, max_length=4)
    title = StringField(required=True)
    seats_available = IntField()
    seats_total = IntField()
    meeting = ListField(EmbeddedDocumentField(CourseMeeting))
    description = StringField(required=True)
    instructors = ListField(EmbeddedDocumentField(CourseInstructor))
    prerequisites = StringField()
    exam_time = StringField()
    exam_date = StringField()
    exam_location = StringField()
    exam_group = StringField()
    critical_review = StringField()


class BannerDepartment(DynamicDocument):
    code = StringField(required=True, min_length=3, max_length=4)
    title = StringField(required=True)
