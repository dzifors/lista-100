class Counter:
    counter: int = 0

    @classmethod
    def increment(cls):
        cls.counter += 1


visit_counter = Counter()
