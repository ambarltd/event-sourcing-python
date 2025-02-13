class AggregateDoesNotExist(RuntimeError):
    def __init__(self):
        super().__init__("Aggregate does not exist")
        self.code = 404

    def __str__(self):
        return f"[Error {self.code}]: {super().__str__()}"