from pipeline import action

@action
def dummy_action(self, source):
    return 'dummy'

@action(call_count=0)
def increment_call_count(self, source):
    self.call_count += 1