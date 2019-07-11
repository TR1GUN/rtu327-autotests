import os

class Log:
    def __init__(self, answer_command, test_name):
        self.answer_command = answer_command
        self.test_name = test_name

        try:
            os.mkdir('Log')
        except Exception:
            pass
        
        create_log = open(os.path.join('Log', self.answer_command + '_' + self.test_name + '.txt'), 'w')
        create_log.close()

    def write_log(self, request, answer, rqtime = '', answtime=''):        
        log = open(os.path.join('Log', self.answer_command + '_' + self.test_name + '.txt'), 'a')
        try:
            log.write(rqtime + ': REQUEST: ' + request + '\n')
        except Exception:
            log.write(rqtime + ': REQUEST: DECODING ERROR' + '\n')
        try:
            if answer.endswith('\n\n'): # For TCP connection
                log.write(answtime + ': ANSWER: ' + answer.replace('\n','') + '\n')
            else:
                log.write(answtime + ': ANSWER: ' + answer + '\n')
        except Exception:
            log.write(answtime + ': ANSWER: DECODING ERROR' + '\n')
        log.close()

    def write_log_info(self, info):        
        log = open(os.path.join('Log', self.answer_command + '_' + self.test_name + '.txt'), 'a')        
        log.write(info)        
        log.close()

