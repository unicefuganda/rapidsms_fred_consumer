class MockUrlLibResponse(object):
    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'application/json; charset=utf-8'}

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code