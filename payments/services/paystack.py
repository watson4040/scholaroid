import requests
from django.conf import settings



class PaystackService:


    BASE_URL = "https://api.paystack.co"



    @staticmethod
    def headers():

        return {

            "Authorization":
            f"Bearer {settings.PAYSTACK_SECRET_KEY}",

            "Content-Type":
            "application/json"

        }



    @classmethod
    def initialize_payment(
        cls,
        email,
        amount,
        reference,
        school
    ):


        url = (
            f"{cls.BASE_URL}"
            "/transaction/initialize"
        )


        payload = {

            "email": email,

            "amount": int(amount * 100),

            "reference": reference,


            # Supports:
            # MTN
            # Airtel
            # Visa
            "channels": [

                "card",

                "mobile_money"

            ],


            # School receives money
            "subaccount":
            school.paystack_subaccount_code,


            # Paystack splits automatically
            "bearer":
            "subaccount"

        }


        response = requests.post(

            url,

            json=payload,

            headers=cls.headers()

        )


        return response.json()