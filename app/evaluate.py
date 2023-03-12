from django.contrib.auth.models import User
#
from app.models import General_Ledger


def validate_price(price=None, cents=None):
    if price is None and cents is None:
        return None
    elif price is not None and cents is not None:
        return float(f"{price}.{cents}")
    elif price is not None and cents is None:
        return float(f"{price}.00")
    elif price is None and cents is not None:
        return float(f"0.{cents}")


# print(validate_price(price=None, cents=50))


def validate_ledger(ledger=None):
    try:
        gl = General_Ledger.objects.get(id=ledger)
        return gl
    except General_Ledger.DoesNotExist:
        return None


def validate_date(date):
    from datetime import datetime
    if date is not None:
        updated_date = datetime.strptime(f'{date} 10:55:31', '%Y-%m-%d %H:%M:%S')
        # print(updated_date)
        return updated_date
    else:
        return None


# print(validate_date('2023-03-16'))
def validate_allocation(user):
    if user is not None:
        user = User.objects.get(id=user)
        return user
    else:
        return None
# validate_purchase_date('2015-01-20')
