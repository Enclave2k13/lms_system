import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course):
    """Создаёт продукт в Stripe по названию курса."""
    product = stripe.Product.create(name=course.name)
    return product.id


def create_stripe_price(product_id, amount):
    """Создаёт цену в Stripe. amount — в рублях, передаётся в копейках."""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency='rub',
    )
    return price.id


def create_checkout_session(price_id, success_url, cancel_url):
    """Создаёт сессию для оплаты и возвращает ссылку."""
    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session
