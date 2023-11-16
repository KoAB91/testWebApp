import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
from tinydb import TinyDB, Query
import json
import re


def create_template_form_db():
    db = TinyDB('db.json')
    if not db.all():
        db.insert({"name": "Email registration form",
                   "field_name_1": "email",
                   "field_type_1": "EMAIL",
                   "field_name_2": "user_name",
                   "field_type_2": "TEXT"})
        db.insert({"name": "Phone registration form",
                   "field_name_1": "phone",
                   "field_type_1": "PHONE",
                   "field_name_2": "user_name",
                   "field_type_2": "TEXT",})
        db.insert({"name": "Order form",
                   "field_name_1": "order_date",
                   "field_type_1": "DATE",
                   "field_name_2": "order_number",
                   "field_type_2": "TEXT"})
        db.insert({"name": "Contact form",
                   "field_name_1": "email",
                   "field_type_1": "EMAIL",
                   "field_name_2": "phone",
                   "field_type_2": "PHONE"})


def fields_validation(value):
    if date_validation(value, '%d.%m.%Y') or date_validation(value, '%Y-%m-%d'):
        return "DATE"
    if re.fullmatch(r'\+7\s[0-9]{3}\s[0-9]{3}\s[0-9]{2}\s[0-9]{2}', value):
        return 'PHONE'
    elif re.fullmatch(r'[-\w\.]+@([-\w]+\.)+[-\w]{2,4}', value):
        return 'EMAIL'
    else:
        return 'TEXT'


def date_validation(value, format):
    try:
        valid_date = time.strptime(value, format)
        return True
    except ValueError:
        return False


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('localhost', 8000)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


class SimpleHttpHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        data = json.loads(body)
        validation_result = {}
        for name, value in data.items():
            validation_result[name] = fields_validation(value)

        keys = list(data.keys())
        db = TinyDB('db.json')
        t_form = Query()
        forms = db.search((t_form.field_name_1.one_of(keys)) & (t_form.field_name_2.one_of(keys)))
        if forms:
            form = forms[0]
            if ((form['field_type_1'] == validation_result[form['field_name_1']]) and
                    (form['field_type_2'] == validation_result[form['field_name_2']])):
                result = form['name']
            else:
                result = str(validation_result)
        else:
            result = str(validation_result)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        response = BytesIO()
        response.write(bytes(result, 'UTF-8'))
        self.wfile.write(response.getvalue())


create_template_form_db()
run(handler_class=SimpleHttpHandler)
