class InvalidTransition(Exception):
    pass


class Order:
    _TRANSITIONS = {
        ("CREATED", "pay"): "PAID",
        ("CREATED", "cancel"): "CANCELLED",
        ("PAID", "ship"): "SHIPPED",
        ("PAID", "cancel"): "CANCELLED",
        ("SHIPPED", "deliver"): "DELIVERED",
    }

    def __init__(self):
        self.state = "CREATED"
        self.refunded = False

    def _apply(self, event):
        key = (self.state, event)
        if key not in self._TRANSITIONS:
            raise InvalidTransition(f"cannot {event} an order that is {self.state}")
        if key == ("PAID", "cancel"):
            self.refunded = True
        self.state = self._TRANSITIONS[key]

    def pay(self):     self._apply("pay")
    def ship(self):    self._apply("ship")
    def deliver(self): self._apply("deliver")
    def cancel(self):  self._apply("cancel")
