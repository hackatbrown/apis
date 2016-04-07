import mongoengine as me


class CourseMeeting(me.EmbeddedDocument):
    day_of_week = me.StringField(max_length=1)
    start_time = me.IntField(min_value=0, max_value=86400)
    end_time = me.IntField(min_value=0, max_value=86400)
    # duration = ListField(StringField())
    location = me.StringField()


# TODO: What is the best way to do this? References?
class CourseInstructor(me.EmbeddedDocument):
    name = me.StringField()
    email = me.StringField()
    isPrimary = me.BooleanField()


# This is pretty dumb, but it beats hard coding these values in the
# databaes I suppose.
class BannerDepartment(me.EmbeddedDocument):
    code = me.StringField(required=True, min_length=3, max_length=4)
    desc = me.StringField(required=True)


class BannerCourse(me.DynamicDocument):
    creation_date = me.DateTimeField()
    semester = me.StringField(required=True)
    number = me.StringField(required=True)
    full_number = me.StringField(required=True)
    crn = me.StringField(required=True)
    dept = me.EmbeddedDocumentField(BannerDepartment, required=True)
    title = me.StringField(required=True)
    seats_available = me.IntField()
    seats_total = me.IntField()
    meeting = me.ListField(me.EmbeddedDocumentField(CourseMeeting))
    description = me.StringField(required=True)
    instructors = me.ListField(me.EmbeddedDocumentField(CourseInstructor))
    prerequisites = me.StringField()
    exam_time = me.StringField()
    exam_date = me.StringField()
    exam_location = me.StringField()
    exam_group = me.StringField()
    critical_review_website = me.StringField()


class NonconflictEntry(me.DynamicDocument):
    course_id = me.ObjectIdField(required=True)
    non_conflicting = me.ListField(me.ObjectIdField())
