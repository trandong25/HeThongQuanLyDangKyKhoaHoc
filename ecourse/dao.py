from ecourse.models import MonHoc

def load_courses():
    return MonHoc.query.all()