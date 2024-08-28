"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     September 2015
@author:    Jose Martinez & Jenny Schulze
@summary:   LITPCDS-11106
            Integration test for story 11106: MS requires firefox browser
            installed
"""

from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
import test_constants


class Story11106(GenericTest):
    """
    MS requires firefox browser installed
    """

    def setUp(self):
        """Runs before every test"""
        super(Story11106, self).setUp()
        self.ms_node = self.get_management_node_filename()
        self.rhcmd = RHCmdUtils()

    def tearDown(self):
        """Runs after every test"""
        super(Story11106, self).tearDown()

    @attr('all', 'revert', 'story11106', 'story11106_tc01')
    def test_01_p_firefox_and_xauth_are_installed(self):
        """
        @tms_id: litpcds_11106_tc01
        @tms_requirements_id: LITPCDS-11106
        @tms_title: Ensure Firefox and xauth are installed on MS
        @tms_description: Test to ensure that firefox and xauth
                          are installed on the MS
        @tms_test_steps:
            @step: Verify that Firefox and xauth are installed
            @result: Packages are installed on MS
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        pkgs = ["firefox", "xorg-x11-xauth"]

        self.log("info", "1. Verify that packages are installed")

        self.assertTrue(self.check_pkgs_installed(self.ms_node, pkgs),
                        "Expected packages not installed")

    @attr('all', 'revert', 'story11106', 'story11106_tc02')
    def test_02_p_x11_forwarding_enabled(self):
        """
        @tms_id: litpcds_11106_tc02
        @tms_requirements_id: LITPCDS-11106
        @tms_title: Ensure x11 forwarding is enabled on MS
        @tms_description: Test to ensure that x11 forwarding is enabled on MS
        @tms_test_steps:
            @step: Verify that x11 forwarding is enabled on MS
            @result: x11 forwarding enabled on MS
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Check ssh config file "
                 "and verify that x11 forwarding is enabled")
        ssh_config_file = test_constants.SSH_CFG_FILE
        enabled_option = "^ *X11Forwarding *yes *$"

        grep_cmd = self.rhcmd.get_grep_file_cmd(ssh_config_file,
                                                enabled_option)
        self.run_command(self.ms_node, grep_cmd,
                                   su_root=True, default_asserts=True)
