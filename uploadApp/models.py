from django.db import models


# Create your models here.
class User:
    def __init__(self, first_name, middle_name, last_name, address, city, state, zip_code, contact_number_office,
                 contact_number_mobile
                 , email, user_type_id, gender, password):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zip_code
        self.contact_number_office = contact_number_office
        self.contact_number_mobile = contact_number_mobile
        self.email = email
        self.user_type_id = user_type_id
        self.gender = gender
        self.password = password
        self.agency_id = -1
        self.id = -1