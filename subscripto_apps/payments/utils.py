import stripe


def create_new_customer(name, email):
    new_customer = stripe.Customer.create(email=email, name=name)
    return new_customer["id"]
