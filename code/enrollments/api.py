"""
Enrollments API Endpoints

POST /api/enrollments                    - Daftar ke course (Student)
GET  /api/enrollments/my-courses         - Lihat course yang sudah didaftar
POST /api/enrollments/{id}/progress      - Tandai lesson selesai
"""

from datetime import datetime, timezone
from ninja import Router
from ninja.errors import HttpError

from accounts.auth_bearer import AuthBearer
from accounts.permissions import is_student
from courses.models import Course, CourseContent
from .models import Enrollment, LessonProgress
from .schemas import (
    EnrollSchema, ProgressSchema,
    EnrollmentOut, CourseSimpleOut, ProgressOut, MessageOut
)

router = Router(tags=["Enrollments"])


def _enrollment_to_out(e: Enrollment) -> EnrollmentOut:
    return EnrollmentOut(
        id=e.id,
        course=CourseSimpleOut(
            id=e.course.id,
            title=e.course.title,
            level=e.course.level,
            price=e.course.price,
        ),
        enrolled_at=e.enrolled_at,
        is_active=e.is_active,
    )


# -----------------------------------------------------------------------------
# POST /api/enrollments  (Student)
# -----------------------------------------------------------------------------
@router.post("", response={201: EnrollmentOut, 400: MessageOut, 404: MessageOut}, auth=AuthBearer())
@is_student
def enroll(request, data: EnrollSchema):
    """Daftar ke sebuah course. Semua user yang login bisa melakukan ini."""
    # Cek course ada
    try:
        course = Course.objects.get(id=data.course_id, is_published=True)
    except Course.DoesNotExist:
        return 404, {"message": "Course tidak ditemukan atau belum dipublish"}

    # Cek sudah enroll
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return 400, {"message": "Kamu sudah terdaftar di course ini"}

    enrollment = Enrollment.objects.create(student=request.user, course=course)
    return 201, _enrollment_to_out(enrollment)


# -----------------------------------------------------------------------------
# GET /api/enrollments/my-courses  (Student)
# -----------------------------------------------------------------------------
@router.get("/my-courses", response=list[EnrollmentOut], auth=AuthBearer())
@is_student
def my_courses(request):
    """Lihat semua course yang sudah kamu daftar."""
    enrollments = (
        Enrollment.objects
        .select_related('course')
        .filter(student=request.user, is_active=True)
    )
    return [_enrollment_to_out(e) for e in enrollments]


# -----------------------------------------------------------------------------
# POST /api/enrollments/{enrollment_id}/progress  (Student)
# -----------------------------------------------------------------------------
@router.post(
    "/{enrollment_id}/progress",
    response={200: ProgressOut, 400: MessageOut, 403: MessageOut, 404: MessageOut},
    auth=AuthBearer()
)
@is_student
def mark_progress(request, enrollment_id: int, data: ProgressSchema):
    """
    Tandai sebuah lesson/konten sebagai selesai atau belum selesai.
    Hanya pemilik enrollment yang bisa update progresnya sendiri.
    """
    # Ambil enrollment, pastikan milik user ini
    try:
        enrollment = Enrollment.objects.select_related('course').get(
            id=enrollment_id,
            student=request.user
        )
    except Enrollment.DoesNotExist:
        return 404, {"message": "Enrollment tidak ditemukan"}

    # Pastikan content ada dan milik course ini
    try:
        content = CourseContent.objects.get(id=data.content_id, course=enrollment.course)
    except CourseContent.DoesNotExist:
        return 404, {"message": "Konten tidak ditemukan di course ini"}

    # Update atau buat progress
    progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        content=content,
    )
    progress.is_complete  = data.is_complete
    progress.completed_at = datetime.now(timezone.utc) if data.is_complete else None
    progress.save()

    return 200, ProgressOut(
        content_id=content.id,
        content_title=content.title,
        is_complete=progress.is_complete,
        completed_at=progress.completed_at,
    )
