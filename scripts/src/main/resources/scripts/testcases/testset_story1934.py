"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     January 2019
@author:    Padraic, Marcin Spoczynski,  Marco Gibboni, Philip Daly,
            Boyan Mihovski, Jose Martinez, Jenny Schulze, Monika Penkova
@summary:   LITPCDS-1934
                As a system architect I want Cobbler to be upgraded to v2.4
                so that I have a supported version.
            LITPCDS-2892
                As an application designer I want MCollective to
                use SSL so that broadcasting to nodes is more secure.
            LITPCDS-8281
                 As a LITP installer I want to have rsyslog7
                 instead of rsyslog used in my deployment
                 so I can benifit from its additional features.
            LITPCDS-9630
                As an ENM user I want a FOSS rsyslog 8.4.1 (or later)
                installed so I use elasticsearch in my 15B deployment.
            LITPCDS-9961
                Upgrade RabbitMQ to latest stable release3
            LITPCDS-11050
                As I LITP Architect I want LITP to upgrade to a repackaged
                version of Erlang that will enable MCollective to use SSL
"""
from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
import test_constants


class Story1934(GenericTest):
    """
    As a system architect I want Cobbler to be upgraded to v2.4 so that I have
    a supported version.
    """
    def setUp(self):
        """
        Runs before every single test.
        """
        super(Story1934, self).setUp()
        self.rhcmd = RHCmdUtils()
        self.ms_node = self.get_management_node_filename()
        self.mn_nodes = self.get_managed_node_filenames()
        self.all_nodes = [self.ms_node] + self.mn_nodes
        self.rsyslog8_pkg_name = 'EXTRlitprsyslog_CXP9032140'
        self.rhcmd = RHCmdUtils()

    def tearDown(self):
        """
        Runs after each test
        """
        super(Story1934, self).tearDown()

    @attr('all', 'revert', 'story1934', 'story1934_tc01')
    def test_01_p_verify_cobbler_version(self):
        """
        @tms_id: litpcds_1934_tc01
        @tms_requirements_id: LITPCDS-1934
        @tms_title: Check Cobbler version
        @tms_description: Verify that the version of cobbler
                          is the supported version 2.4.2
        @tms_test_steps:
            @step: Verify the version of cobbler running on MS
            @result: Version of Cobbler on MS verified to be 2.4
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Verify the version of cobbler running on MS")
        expect_ver = test_constants.COBBLER_EXP_VERSION

        cmd = "cobbler --version"
        stdout, _, _ = self.run_command(self.ms_node, cmd,
                                                 su_root=True,
                                                 default_asserts=True)

        self.assertTrue(self.is_text_in_list(expect_ver, stdout),
                "Cobbler is not the expected version {0}".format(expect_ver))

    @attr('all', 'revert', 'story2892', 'story2892_tc04')
    def test_02_n_verify_no_rabbitmq_on_nodes(self):
        """
        @tms_id: litpcds_2892_tc04
        @tms_requirements_id: LITPCDS-2892
        @tms_title:
            Verify that "rabbitmq" is not installed on managed nodes.
        @tms_description:
            Verify that "rabbitmq" is not installed on managed nodes.
        @tms_test_steps:
            @step: On each peer node, query "rpm" to check if "rabbitmq-server"
                   package is installed
            @result: Package not found
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info",
                 "1. Check that RabbitMQ is not installed on peer nodes")
        for node in self.mn_nodes:
            rabbitmq_on_nodes = self.check_pkgs_installed(node,
                                                          ["rabbitmq-server"])
            self.assertFalse(rabbitmq_on_nodes,
                             "rabbitmq-server installed on {0}".format(node))

    #attr('all', 'revert', 'story8281', 'story8281_tc01')
    def obsolete_03_p_check_rsyslog_version_on_all_nodes(self):
        """
        #tms_id: litpcds_8281_tc01
        #tms_requirements_id: LITPCDS-8281
        #tms_title: Verify that rsyslog7 is running on initial install
        #tms_description: Check that on an initial install of the MS and Peer
                          nodes the version of the running rsyslog
                          on them is the major version 7
        #tms_test_steps:
            #step: Check rsyslog version on all nodes
            #result: Installed version on all nodes is rsyslog7
        #tms_test_precondition: NA
        #tms_execution_type: Automated
        """
        pass

    @attr('all', 'revert', 'story9630', 'story9630_tc01')
    def test_04_p_extrlitprsyslog8_is_available(self):
        """
        @tms_id: litpcds_9630_tc01
        @tms_requirements_id: LITPCDS-9630
        @tms_title: Ensure that rsyslog8 is available
        @tms_description: Ensure that the rsyslog8 package is avaiable
                          via a yum search initiated on both the management
                          server and the peer nodes.
        @tms_test_steps:
            @step: Issue a yum search for the rsyslog8 package
                   on ms and peer nodes
            @result: rsyslog8 package available on all nodes
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Search for rsyslog8")
        yum_search_cmd = self.rhcmd.get_yum_cmd("search {0}".format
                                            (self.rsyslog8_pkg_name))
        for node in self.all_nodes:
            stdout, _, _ = self.run_command(node, yum_search_cmd,
                                            su_root=True,
                                            default_asserts=True)

            self.assertFalse(self.is_text_in_list(
                                              "Warning: No matches found for:",
                                              stdout),
                             "rsyslog8 not found on {0}".format(node))

    @attr('all', 'revert', 'story9961', 'story9961_tc03', 'story9961_tc04')
    def test_05_p_verify_rabbitmq_version_description(self):
        """
        @tms_id: litpcds_9961_tc03, litpcds_9961_tc04
        @tms_requirements_id: LITPCDS-9961
        @tms_title: Verify RabbitMQ version
        @tms_description: Verify that RabbitMQ version
                          running on the MS is 3.8.9
        @tms_test_steps:
            @step: Check version of RabbitMQ
            @result: RabbitMQ version running on the MS is 3.8.9
            @step: Check description of RabbitMQ RPM
            @result: Version of RabbitMQ is 3.8.9 in description
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Check version")
        expected_outputs = ["{rabbit,\"RabbitMQ\",\"3.5.4\"}",
                            "RabbitMQ 3.5.4"]

        cmd = "/usr/sbin/rabbitmqctl status"

        out, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                                        default_asserts=True)
        self.assertTrue(self.is_text_in_list(expected_outputs[0], out),
                    "{0} not the version found".format(expected_outputs[1]))

        self.log("info", "2. Check description")
        cmd = "/bin/rpm -q --queryformat \"%{DESCRIPTION}\n\" "\
              "EXTRlitprabbitmqserver_CXP9031043"

        out, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                                        default_asserts=True)
        self.assertTrue(self.is_text_in_list(expected_outputs[1], out),
                    "{0} not the version found".format(expected_outputs[1]))

    @attr('all', 'revert', 'story11050', 'story11050_tc03')
    def test_06_p_verify_erlang_version(self):
        """
        @tms_id: litpcds_11050_tc03
        @tms_requirements_id: LITPCDS-11050
        @tms_title: Verify that the "erlang" is installed in version 17.5
                    on MS node
        @tms_description: Verify that the "erlang" is installed in version 17.5
                          on MS node
        @tms_test_steps:
            @step: Read content of file
                   "/usr/lib64/erlang/releases/17/OTP_VERSION"
            @result: "erlang" version is 17.5
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        otp_version_contents = self.get_file_contents(self.ms_node,
                "/usr/lib64/erlang/releases/17/OTP_VERSION")

        expected_version = test_constants.EXPECTED_ERLANG_VERSION

        self.log("info", "Expecting erlang version {0}".
                          format(expected_version))

        self.assertTrue(expected_version in otp_version_contents,
            'ERLANG version is incorrect: expected "{0}", actual "{1}"'.
            format(expected_version, otp_version_contents))
