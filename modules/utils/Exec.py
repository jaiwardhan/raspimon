"""
jaiwardhan/Raspimon

@author: Jaiwardhan Swarnakar, 2021
Copyright 2021-present
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
	http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from subprocess import Popen, PIPE

class Exec:
    """Execution utilities mainly for external communication and triggers
    """

    @staticmethod
    def shell(command, get_output=False):
        """Execute a non-piped non-redirected bash command

        Args:
            command (str): Non-piped Non-redirected bash command. 
            get_output (bool, optional): Set True to get command outputs.
                Defaults to False.

        Returns:
            (output, exit code, stderr | None): Command outputs, exit code
                and stderr message if `get_output` is True
        """
        sub_process = Popen(str(command).split(" "), stdout=PIPE, stderr=PIPE)
        output, err = sub_process.communicate()
        if get_output:
            return output, sub_process.returncode, err
