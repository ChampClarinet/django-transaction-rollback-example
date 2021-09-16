from typing import Union
from rest_framework.decorators import api_view
from django.db import transaction
from bank.models import Customer
from rest_framework.views import Response
from core.exception import TransactionException


# Create your views here.
@api_view(["POST"])
def process_payment(request):
  if request.method == 'POST':
    payor_name: Union[None, str] = request.data.get('payor', None)
    payee_name: Union[None, str] = request.data.get('payee', None)
    amount: Union[None, float] = request.data.get('amount', None)

    try:
      with transaction.atomic():
        #? if any error thrown, auto rollback else commit after this block finished
        try:
          payor: Customer = Customer.objects.get(name=payor_name)
        except Customer.DoesNotExist:
          raise TransactionException({
            "status": 404,
            "payload": { "message": "payor does not exist." },
          })
        if payor.balance < amount:
          raise TransactionException({
            "status": 400,
            "payload": { "message": "insufficient funds." },
          })
        payor.balance -= amount
        payor.save()

        try:
          payee: Customer = Customer.objects.get(name=payee_name)
        except Customer.DoesNotExist:
          raise TransactionException({
            "status": 400,
            "payload": { "message": "payee does not exist." },
          })
        payee.balance += amount
        payee.save()

    except TransactionException as e:
      payload = e.payload
      status = payload.get('status', 500)
      data = payload.get('payload', None)
      return Response(data=data, status=status)

    return Response(status=200)