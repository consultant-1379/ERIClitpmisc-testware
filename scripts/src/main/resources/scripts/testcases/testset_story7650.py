#!/usr/bin/env python

'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     January 2015
@author:    Maria Varley. Maurizio Senno refactored Oct 2015
@summary:   LITPCDS-7650
            As a LITP user, I want to be able to monitor the health of
            my OCF resource agents so that I know if they are healthy
'''

from litp_generic_test import GenericTest, attr
from rest_utils import RestUtils
import test_constants
import time


class Story7650(GenericTest):
    """
    Description:
        LITPCDS-7650
        As a LITP user, I want to be able to monitor the health of
        my OCF resource agents so that I know if they are healthy

    Definitions:
        OCF        : Open Cluster Framework
        vmmonitord : The OCF Resource Agent deamon
    """

    def setUp(self):
        super(Story7650, self).setUp()
        self.service_name = "vmmonitord"
        self.ms1 = self.get_management_node_filename()
        self.test_nodes = self.get_managed_node_filenames()
        self.mn1 = self.test_nodes[0]
        self.mn2 = self.test_nodes[1]
        self.all_nodes = [self.ms1, self.mn1, self.mn2]
        self.ms_ip_address = self.get_node_att(self.ms1, 'ipv4')
        self.n1_ip_address = self.get_node_att(self.mn1, 'ipv4')
        self.restutils = RestUtils(self.ms_ip_address)
        self.ocf = "/usr/lib/ocf"
        self.ocf_resources_dir = "/usr/lib/ocf/resource.d"
        self.port = '12987'
        self.netstat_cmd = '/bin/netstat -tln | grep {0}'.format(self.port)
        self.exec_seq_file = "/tmp/ocf_log/exec_sequence.txt"

    def tearDown(self):
        """
        Description:
            Runs after every single test
        """
        super(Story7650, self).tearDown()

    def _send_request(self,
            hostname, req_type='GET', proto='http', port=None, resource=''):
        """
        Description
            Send OCF request
        Args:
            req_type (str): The type of HTTP request
            proto    (str): Specify the protocol to use (ex. HTTP/ HTTPS)
            hostname (str): The target server
            port     (str): Port
            resource (str): Specifies the OCF resource folder path
        Returns:
            cmd (str)           : The actual curl command string used
            rc  (int)           : The code returned by the HTTP request
            exec_sequence (list): The list of scripts run
        """
        if port == None:
            port = self.port

        self.log('info', 'Remove "execution sequence" file if present')
        self.assertTrue(
            self.remove_item(self.mn1, self.exec_seq_file, su_root=True),
            'Failed to remove file "{0}"'.format(self.exec_seq_file))

        self.log('info', 'Logging content of OCF "resource.d" folder')

        cmd = (
            "/usr/bin/curl -X {0} -s -S -k -w \'%{{http_code}}\\n' "
            "{1}://{2}:{3}{4}"
            .format(req_type, proto, hostname, port, resource))

        self.log('info', 'Send OCF request')
        start_time = int(time.time())

        out, _, rc = self.run_command(self.ms1, cmd, su_root=True)
        elapsed_time = int(time.time()) - start_time
        self.log('info',
            'HTTP request completed in {0}s'.format(elapsed_time))
        if len(out) > 0:
            rc = out[0]
        else:
            self.log('info', 'The HTTP request timed out')
            rc = None

        self.log('info', 'Determine scripts execution sequence')
        if self.remote_path_exists(self.mn1, self.exec_seq_file):
            exec_sequence = self.get_file_contents(
                                self.mn1, self.exec_seq_file, su_root=True)
            # Removing forward slashes added (by ssh?) while transferring
            # data from MS to gateway server
            exec_sequence = [x.replace('///', '/') for x in exec_sequence]
        else:
            exec_sequence = []
        return cmd, rc, exec_sequence

    def _install_vmmonitor_package(self, node):
        """
        Description
            Install vmmonitor rpm onto specified node
        Args
            node (str): Node on which to install the package
        """
        local_vmmonitor_rpm_path = \
            self.g_util.get_item_from_nexus('com.ericsson.nms.litp',
                'ERIClitpvmmonitord_CXP9031644')
        self.assertNotEqual(None, local_vmmonitor_rpm_path,
                            "Nexus path not found")
        self.log('info', 'Install "vmmonitor" package')
        self.assertTrue(
                self.copy_and_install_rpms(node, [local_vmmonitor_rpm_path],
                    rpm_repo_path='/tmp/'),
                "Installation of vmmonitord was unsuccessful")

    def _get_vmmonitord_status(self, node):
        """
        Description
            Query "vmmonitor" service to determine its status
        Args:
            node (str): The node where to perform the query
        Returns:
            The status of the "vmmonitor" service
        """
        cmd = self.rhc.get_systemctl_cmd(
                args="show -p SubState vmmonitord") + " | sed 's/SubState=//g'"

        out, _, _ = self.run_command(node, cmd, default_asserts=True)

        if self.is_text_in_list('running', out):
            return 'running'
        elif self.is_text_in_list('stopped', out):
            return 'stopped'
        else:
            return None

    def _is_vmmonitord_running(self, node):
        """
        Description
            determine if "vmmonitor" service is running
        Args:
            node (str): The node where to perform the query
        Returns:
            True if "vmmonitor" is running else False
        """
        if self._get_vmmonitord_status(node) == 'running':
            return True
        return False

    def _assert_vmmonitor_is_listening_on_socket(self, node):
        """
        Description:
            Perform a sanity check to determine if the vmmonitord process
            is running and listening on port "12987"
        Args:
            node    (str): The node to check status of vmmonitord on
        """

        self.log('info',
        'Check that "vmmonitord" service is running')
        self.assertTrue(self._is_vmmonitord_running(node),
                        '"Service "vmmonitord" not running on node {0}'
                        .format(node))

        self.log('info',
        'Check that the vmonitord service is listening on port {0} '
        .format(self.port))
        stdout, _, _ = self.run_command(node, self.netstat_cmd, su_root=True,
            default_asserts=True)
        text = 'LISTEN'
        self.assertTrue(stdout != [] and self.is_text_in_list(text, stdout),
                        'No service listening on port {0} found on node {1}'
                        .format(self.port, node))

    def _create_ocf_files_and_assert_sequence(self):
        """
        Description:
            Create OCF files under OCF directory.
            Send PUT, POST and DELETE requests and assert return codes
            and sequence
        """
        n1_path = self.get_node_url_from_filename(self.ms1, self.mn1)
        n1_hostname = self.get_props_from_url(self.ms1, n1_path, "hostname")
        self.log('info',
        'Create a directory structure under the "resource.d" '
              'directory')
        folder1 = '{0}/folder1'.format(self.ocf_resources_dir)
        folder2 = '{0}/folder2'.format(self.ocf_resources_dir)

        self.create_dir_on_node(self.mn1, folder1, su_root=True)
        self.create_dir_on_node(self.mn1, folder2, su_root=True)
        self.create_dir_on_node(self.mn1, '/tmp/ocf_log', su_root=True)
        self.create_dir_on_node(self.mn2, '/tmp/ocf_log', su_root=True)

        self.log('info',
        'Create executable files onto "OCF" folder')

        expected_seq = [
            '/usr/lib/ocf/resource.d/a_script.sh SLEEPTIME=0 RC=0',
            '/usr/lib/ocf/resource.d/b_script.sh SLEEPTIME=0 RC=0',
            '/usr/lib/ocf/resource.d/c_script.sh SLEEPTIME=0 RC=0',
            '/usr/lib/ocf/resource.d/z_script.sh SLEEPTIME=0 RC=0',
            '/usr/lib/ocf/resource.d/folder1/a_script.sh SLEEPTIME=0 RC=0',
            '/usr/lib/ocf/resource.d/folder2/a_script.sh SLEEPTIME=0 RC=0', ]

        for script in expected_seq:
            path = script.split()[0]
            self._create_ocf_file_on_node(self.mn1, path)

        self.log('info',
        'Send GET request and check return code and execution sequence')
        expected_rc = '200'
        _, rc, sequence = self._send_request(n1_hostname)
        self.assertEqual(expected_rc, rc,
                         "Return code was {0} and not the expected {1}"\
                             .format(rc, expected_rc))
        self.assertEqual(expected_seq, sequence, "Sequence not as expected")

        self.log('info',
        'Verify that disallowed request types cause a return code of '
            '"501" and that no scripts are executed')
        expected_rc = '501'
        expected_seq = []
        for req_type in ['PUT', 'POST', 'DELETE']:
            self.log('info',
                     'Verify "{0}" request'.format(req_type, expected_rc))
            _, rc, seq = self._send_request(n1_hostname, req_type=req_type)
            self.assertEqual(expected_rc, rc,
                             "Return code was {0} and not the expected {1}"\
                                 .format(rc, expected_rc))

            self.assertEqual(expected_seq, seq, "Sequence not as expected")

    def _create_ocf_file_on_node(self, node, path, exec_file=True, rc=0,
            sleep_time=0):
        """
        Description
            Create an OCF file given spacified data
        Args:
            node (str)        : Node on which file is to be created
            script_data (dict): Data required to create the file
            exec_file (bool): Specify if the file must be executable

        Example of script_data:
        script_data = {
            'path': '/path_to_OCF_dir/file_name'
            'sleep_time': 30
            'rc': 0
        }
        """
        if exec_file == True:
            contents = self._get_executable_script_content(
                                sleep_time, rc)
        else:
            contents = ['empty script']

        if self.remote_path_exists(node, path):
            self.remove_item(node, path, su_root=True)

        self.create_file_on_node(self.mn1,
                                 filepath=path,
                                 file_contents_ls=contents,
                                 su_root=True)

    @staticmethod
    def _get_executable_script_content(sleep_time=0, rc=0,
                                log_to='/tmp/ocf_log/exec_sequence.txt'):
        """
        Description:
            Create content of an executable script
        Args:
            sleep_time (int): Time to sleep in seconds
            rc         (int): The code to be returned by the script
            log_to     (str): The file where stdout is redirected
        """
        content = [
            '#!/bin/bash',
            'RC={0}'.format(rc),
            'SLEEPTIME={0}'.format(sleep_time),
            'LOGTO={0}'.format(log_to),
            'echo "$(pwd)/$0 SLEEPTIME=$SLEEPTIME RC=$RC" 1>>$LOGTO',
            'sleep $SLEEPTIME',
            'exit $RC']
        return content

    def _install_vmmonitor_if_not_yet_installed(self):
        """
        If the vmmonitor is not yet installed on the node, installs it. Also
        verifies that vmmonitor is running
        """
        for node in self.all_nodes:
            self.log('info',
            'Check if "vmmonitord" service is running on node "{0}'
            .format(node))
            if not self._is_vmmonitord_running(node):
                self.log('info',
                'Install "vmmonitor" package')
                self._install_vmmonitor_package(node)
            self._assert_vmmonitor_is_listening_on_socket(node)

    @attr('all', 'revert', 'story7650', 'story7650_tc01')
    def test_01_p_vmmonitord_service_started_after_install(self):
        """
        @tms_id: litpcds_7650_tc01
        @tms_requirements_id: LITPCDS-7650
        @tms_title: vmmonitord_service_started_after_install
        @tms_description:
            Verify that vmmonitord is started automatically when
            the vmmonitor package is installed in a node
        @tms_test_steps:
            @step: Install vmmonitord on every node (if not already installed)
            @result: vmmonitord is installed
            @step: Verify that vmmonitord starts automatically after install
            @result: vmmonitord is running
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        for node in self.all_nodes:
            if not self._is_vmmonitord_running(node):
                self.log('info',
                     '1. Install "vmmonitor" on node "{0}"'.format(node))
                self._install_vmmonitor_package(node)

            self.log('info',
            '2. Check that "vmmonitord" is running and listening on node "{0}"'
            .format(node))
            self._assert_vmmonitor_is_listening_on_socket(node)

    @attr('all', 'revert', 'story7650', 'story7650_tc02')
    def test_02_n_vmmonitord_service_started_after_reboot(self):
        """
        @tms_id: litpcds_7650_tc02
        @tms_requirements_id: LITPCDS-7650
        @tms_title: Check the vmmonitor service after reboot
        @tms_description:
            Verify that vmmonitord is started automatically when
            the node is rebooted and that it is LSB compliant
        @tms_test_steps:
            @step: Install vmmonitord on every node (if not already installed)
            @result: vmmonitord is installed and running
            @step: Reboot node1 and verify that vmmonitord is running
            @result: vmmonitord is started after reboot
            @step: Verify that "vmmonitord" service is LSB compliant
            @result: vmmonitord can be stopped, started and restarted
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log('info',
        '1. Make sure that "vmmonitord" service is running on peer nodes,'
        ' install if not running')
        self._install_vmmonitor_if_not_yet_installed()

        self.log('info',
                 '2. Reboot node 1 and check that vmmonitord is running ')

        cmd = "(sleep 1; {0} -r now) &".format(test_constants.SHUTDOWN_PATH)
        self.run_command(self.mn1, 'cmd', su_root=True)
        self.wait_for_ping(self.get_node_att(self.mn1,
            test_constants.NODE_ATT_IPV4), ping_success=False)
        self.wait_for_node_up(self.mn1)
        self._assert_vmmonitor_is_listening_on_socket(self.mn1)

        self.log('info',
        '4. Check that "vmmonitord" service is LSB compliant')
        self.run_command(
            self.mn1, self.rhc.get_service_stop_cmd(self.service_name),
            su_root=True, default_asserts=True)
        self.assertFalse(self._is_vmmonitord_running(self.mn1),
            '"vmmonitord" found on state not equal to "stopped"')

        self.run_command(
            self.mn1, self.rhc.get_service_start_cmd(self.service_name),
            su_root=True, default_asserts=True)
        self.assertTrue(self._is_vmmonitord_running(self.mn1),
            '"vmmonitord" found on state not equal to "running"')

        self.run_command(
            self.mn1, self.rhc.get_service_restart_cmd(self.service_name),
            su_root=True, default_asserts=True)
        self._assert_vmmonitor_is_listening_on_socket(self.mn1)

    @attr('all', 'revert', 'story7650', 'story7650_tc04')
    def test_04_p_vmmonitord_hostname_not_resolved(self):
        """
        @tms_id: litpcds_7650_tc04
        @tms_requirements_id: LITPCDS-7650
        @tms_title: VMmonitor valid agents
        @tms_description:
            Verifies valid OCF agents are executed in lexical order and
            a 200 OK is returned to the http client.
        @tms_test_steps:
            @step: Install vmmonitord on every node (if not already installed)
            @result: vmmonitord is installed and running
            @step: Create ocf/resource.d directory on peer node1
            @result: Directory and files are created
            @step: Verify that no agent script is executed after sending
                   PUT, POST and DELETE requests
            @result: Return codes are as expected
                     and no agent scripts were executed
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log('info',
        '1. Make sure that "vmmonitord" service is running on peer nodes, '
        'install if not running')
        self._install_vmmonitor_if_not_yet_installed()

        self.log('info',
        '2. Create ocf directory and files on node1 '
        'and verify that no agent script is executed when sending requests')

        self.assertTrue(
            self.create_dir_on_node(self.mn1, self.ocf, su_root=True),
            'Failed to create folder "{0}" on "{1}"'
            .format(self.ocf, self.mn1))

        self.assertTrue(
            self.create_dir_on_node(
                            self.mn1, self.ocf_resources_dir, su_root=True),
            'Failed to create folder "{0}" on "{1}"'
            .format(self.ocf_resources_dir, self.mn1))
