
from subprocess import Popen, PIPE

class Exec:

    @staticmethod
    def shell(command, get_output=False):
        sub_process = Popen(str(command).split(" "), stdout=PIPE, stderr=PIPE)
        output, err = sub_process.communicate()
        if get_output:
            return output, sub_process.returncode, err
