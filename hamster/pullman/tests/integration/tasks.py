from pipeline import action

@action
def dummy_action(self, source):
    return 'dummy'