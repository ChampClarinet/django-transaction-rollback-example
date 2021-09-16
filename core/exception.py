from typing import Any


class TransactionException(Exception):
  
  payload: Any = None
  
  def __init__(self, payload) -> None:
    self.payload = payload