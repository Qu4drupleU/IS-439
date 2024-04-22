from django.test import TestCase
from .models import Period, Year, Semester, Course, Instructor, Student, Section, Registration
from django.urls import reverse
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.http import HttpResponseForbidden


# Assume importing your models and forms if necessary


class PeriodModelTest(TestCase):
    def setUp(self):
        Period.objects.create(period_sequence=1, period_name="Spring")

    def test_period_str(self):
        period = Period.objects.get(period_sequence=1)
        self.assertEqual(str(period), "Spring")


class YearModelTest(TestCase):
    def setUp(self):
        Year.objects.create(year=2024)

    def test_year_str(self):
        year = Year.objects.get(year=2024)
        self.assertEqual(str(year), "2024")


class SemesterModelTest(TestCase):
    def setUp(self):
        year = Year.objects.create(year=2024)
        period = Period.objects.create(period_sequence=1, period_name="Fall")
        Semester.objects.create(year=year, period=period)

    def test_semester_str(self):
        semester = Semester.objects.get(year__year=2024, period__period_name="Fall")
        self.assertEqual(str(semester), "2024 - Fall")


class CourseModelTest(TestCase):
    def setUp(self):
        Course.objects.create(course_number="IS439", course_name="Web Development Using Application Frameworks")

    def test_course_str(self):
        course = Course.objects.get(course_number="IS439")
        self.assertEqual(str(course), "IS439 - Web Development Using Application Frameworks")


class InstructorModelTest(TestCase):
    def setUp(self):
        Instructor.objects.create(first_name="Kevin", last_name="Trainor")

    def test_semester_str(self):
        instructor = Instructor.objects.get(first_name="Kevin")
        self.assertEqual(str(instructor), "Trainor, Kevin")


class StudentModelTest(TestCase):
    def setUp(self):
        Student.objects.create(first_name="Maison", last_name="Wu")

    def test_semester_str(self):
        student = Student.objects.get(first_name="Maison")
        self.assertEqual(str(student), "Wu, Maison")


class InstructorListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Instructor.objects.create(first_name="Kevin", last_name="Trainor")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/instructor/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(response.status_code, 200)

    def test_list_instructors(self):
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertTrue('instructor_list' in response.context)
        self.assertEqual(len(response.context['instructor_list']), 1)


class InstructorDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instructor = Instructor.objects.create(
            first_name="Kevin",
            last_name="Trainor",
            disambiguator=""
        )

    def test_instructor_detail_view_status_code(self):
        # Test the HTTP status code returned by the view.
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern',
                                           args=[self.instructor.instructor_id]))
        self.assertEqual(response.status_code, 200)

    def test_instructor_detail_view_template(self):
        # Test the template used by the view.
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern',
                                           args=[self.instructor.instructor_id]))
        self.assertTemplateUsed(response, 'courseinfo/instructor_detail.html')

    def test_instructor_detail_view_context_data(self):
        # Test the context data passed to the template.
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern',
                                           args=[self.instructor.instructor_id]))
        self.assertEqual(response.context['instructor'].instructor_id, self.instructor.instructor_id)
        self.assertEqual(str(response.context['instructor']),
                         f"{self.instructor.last_name}, {self.instructor.first_name}")


class RegistrationListAuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user', password='test123')
        cls.admin = User.objects.create_user(username='admin', password='test123')
        permission = Permission.objects.get(codename='view_registration')
        cls.admin.user_permissions.add(permission)

    def test_logged_in_with_wrong_password(self):
        self.client.login(username='admin', password='test111')
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_no_permission(self):
        self.client.login(username='user', password='test123')
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        self.client.login(username='admin', password='test123')
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 200)

    def test_list_only_accessible_by_permitted_user(self):
        self.client.login(username='admin', password='test123')
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='user', password='test123')
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 403)
