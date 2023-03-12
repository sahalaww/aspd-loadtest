from locust import HttpUser, task, between, events
from locust.clients import HttpSession
from pyquery import PyQuery as pq


class HttpSessionClass(HttpSession):
    def __init__(self, request_event, user):
        super().__init__(base_url='https://localhost',
                         request_event=request_event, user=user)


class MyUser(HttpUser):
    wait_time = between(1, 2)
    client = None
    is_login = False

    def view_login_token(self):
        re = self.client.get('/auth/login', verify=False)
        doc = pq(re._content)
        token = doc('input:hidden').val()
        return token

    @task
    def login(self):
        self.client = HttpSessionClass(request_event=events.request, user=self)
        before_post = self.client.get("/auth/login", verify=False)
        doc = pq(before_post._content)
        token = doc('input:hidden').val()

        with self.client.post("/auth/login", {"username": "", "password": "", "csrf_token": token},
                              verify=False, allow_redirects=True, catch_response=True) as response:
            if response.status_code >= 200 and response.status_code <= 300 and 'Admin' in response.text:
                self.is_login = True
                response.success()

            else:
                response.failure("Login failed")

    @task
    def visit_exam_page(self):
        if self.is_login:
            with self.client.get("/exam/", verify=False, catch_response=True) as response:
                if response.status_code >= 200 and 'Admin' in response.text:
                    response.success()
                else:
                    response.failure("Visit Page Exam Failed")
        else:
            self.login()
