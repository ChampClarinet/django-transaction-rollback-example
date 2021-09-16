from rest_framework.decorators import api_view
from django.db import transaction
from bank.models import Customer
from rest_framework.views import Response


# Create your views here.
@api_view(["POST"])
def process_payment(request):
  if request.method == 'POST':
    payor_name = request.data.get('payor', None)
    payee_name = request.data.get('payee', None)
    amount = request.data.get('amount', None)

    try:
      with transaction.atomic():
        #? if any error thrown, auto rollback else commit after this block finished
        payor: Customer = Customer.objects.get(name=payor_name)
        payor.balance -= amount
        payor.save()

        payee: Customer = Customer.objects.get(name=payee_name)
        payee.balance += amount
        payee.save()
    except Customer.DoesNotExist:
      return Response(
        data={
          "message": "payor or payee does not exists."
        }, 
        status=404,
      )

    return Response(status=200)