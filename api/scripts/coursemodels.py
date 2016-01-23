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

# This is pretty dumb, but it beats hard coding these values in the
# databaes I suppose.
class BannerDepartment(EmbeddedDocument):
    code = StringField(required=True, min_length=3, max_length=4)
    desc = StringField(required=True)


class BannerCourse(DynamicDocument):
    creation_date = DateTimeField()
    semester = StringField(required=True)
    number = StringField(required=True)
    full_number = StringField(required=True)
    dept = EmbeddedDocumentField(BannerDepartment, required=True)
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


