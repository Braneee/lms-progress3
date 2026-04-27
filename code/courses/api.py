"""
Courses API Endpoints

Public (tanpa auth):
  GET  /api/courses          - List semua course (pagination + filter)
  GET  /api/courses/{id}     - Detail satu course

Protected:
  POST   /api/courses         - Buat course baru (Instructor/Admin)
  PATCH  /api/courses/{id}    - Update course (Owner/Admin)
  DELETE /api/courses/{id}    - Hapus course (Admin only)
"""

from django.db.models import Q
from ninja import Router
from ninja.errors import HttpError

from accounts.auth_bearer import AuthBearer
from accounts.permissions import is_instructor, is_admin, is_owner_or_admin
from .models import Course
from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseFilterSchema,
    CourseOut, CourseListOut, InstructorOut, MessageOut
)

router = Router(tags=["Courses"])


def _course_to_out(course: Course) -> CourseOut:
    """Helper: konversi Course model ke CourseOut schema."""
    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        price=course.price,
        level=course.level,
        is_published=course.is_published,
        instructor=InstructorOut(
            id=course.instructor.id,
            username=course.instructor.username,
            email=course.instructor.email,
        ),
        created_at=course.created_at,
    )


# -----------------------------------------------------------------------------
# GET /api/courses  (Public)
# -----------------------------------------------------------------------------
@router.get("", response=CourseListOut)
def list_courses(request, filters: CourseFilterSchema = CourseFilterSchema()):
    """
    List semua course yang sudah dipublish.
    Mendukung filter: level, min_price, max_price, search (judul).
    Mendukung pagination: page & page_size.
    """
    qs = Course.objects.select_related('instructor').filter(is_published=True)

    # Terapkan filter
    if filters.level:
        qs = qs.filter(level=filters.level)
    if filters.min_price is not None:
        qs = qs.filter(price__gte=filters.min_price)
    if filters.max_price is not None:
        qs = qs.filter(price__lte=filters.max_price)
    if filters.search:
        qs = qs.filter(title__icontains=filters.search)

    # Pagination
    total  = qs.count()
    offset = (filters.page - 1) * filters.page_size
    qs     = qs[offset: offset + filters.page_size]

    return CourseListOut(
        total=total,
        page=filters.page,
        per_page=filters.page_size,
        results=[_course_to_out(c) for c in qs],
    )


# -----------------------------------------------------------------------------
# GET /api/courses/{id}  (Public)
# -----------------------------------------------------------------------------
@router.get("/{course_id}", response={200: CourseOut, 404: MessageOut})
def get_course(request, course_id: int):
    """Detail satu course berdasarkan ID."""
    try:
        course = Course.objects.select_related('instructor').get(id=course_id)
    except Course.DoesNotExist:
        return 404, {"message": "Course tidak ditemukan"}
    return 200, _course_to_out(course)


# -----------------------------------------------------------------------------
# POST /api/courses  (Instructor / Admin)
# -----------------------------------------------------------------------------
@router.post("", response={201: CourseOut, 403: MessageOut}, auth=AuthBearer())
@is_instructor
def create_course(request, data: CourseCreateSchema):
    """
    Buat course baru. Hanya Instructor dan Admin yang bisa.
    Instructor otomatis menjadi pemilik course.
    """
    course = Course.objects.create(
        title=data.title,
        description=data.description,
        price=data.price,
        level=data.level,
        is_published=data.is_published,
        instructor=request.user,
    )
    return 201, _course_to_out(course)


# -----------------------------------------------------------------------------
# PATCH /api/courses/{id}  (Owner / Admin)
# -----------------------------------------------------------------------------
@router.patch("/{course_id}", response={200: CourseOut, 403: MessageOut, 404: MessageOut}, auth=AuthBearer())
def update_course(request, course_id: int, data: CourseUpdateSchema):
    """
    Update course. Hanya pemilik course (instructor) atau Admin yang bisa.
    """
    try:
        course = Course.objects.select_related('instructor').get(id=course_id)
    except Course.DoesNotExist:
        return 404, {"message": "Course tidak ditemukan"}

    # Cek ownership
    if not is_owner_or_admin(request.user, course.instructor_id):
        return 403, {"message": "Kamu bukan pemilik course ini"}

    # Update hanya field yang dikirim (partial update)
    if data.title        is not None: course.title        = data.title
    if data.description  is not None: course.description  = data.description
    if data.price        is not None: course.price        = data.price
    if data.level        is not None: course.level        = data.level
    if data.is_published is not None: course.is_published = data.is_published
    course.save()

    return 200, _course_to_out(course)


# -----------------------------------------------------------------------------
# DELETE /api/courses/{id}  (Admin only)
# -----------------------------------------------------------------------------
@router.delete("/{course_id}", response={200: MessageOut, 403: MessageOut, 404: MessageOut}, auth=AuthBearer())
@is_admin
def delete_course(request, course_id: int):
    """Hapus course. Hanya Admin yang bisa."""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return 404, {"message": "Course tidak ditemukan"}

    course.delete()
    return 200, {"message": f"Course '{course.title}' berhasil dihapus"}
