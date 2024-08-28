"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Sept 2018
@author:    Aisling Stafford
@summary:   TORF-255505
            As a LITP user I want a DB Migration mechanism to support uplift
            from PostgreSQL 8.4.20 to PostgreSQL 9.6 on the LMS.
"""

from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
import test_constants as const


class Story255505(GenericTest):
    """
    As a LITP user I want a DB Migration mechanism to support uplift
    from PostgreSQL 8.4.20 to PostgreSQL 9.6 on the LMS.
    """

    def setUp(self):
        """ Runs before every single test. """
        super(Story255505, self).setUp()
        self.rh_utils = RHCmdUtils()

        self.ms_node = self.get_management_node_filename()
        self.ms_ip = self.get_node_att(self.ms_node, 'ipv4')
        self.peer_nodes = self.get_managed_node_filenames()
        self.all_nodes = [self.ms_node] + self.peer_nodes
        self.node_urls = self.find(self.ms_node, '/deployments', 'node')

        self.fw_rules_n1_path = self.find(self.ms_node, self.node_urls[0],
                                'collection-of-firewall-rule')[0]

        self.fw_rules_n2_path = self.find(self.ms_node, self.node_urls[1],
                                'collection-of-firewall-rule')[0]

        self.ms_rules_parent_path = self.find(self.ms_node, '/ms',
                                    'collection-of-firewall-rule')[0]

        self.fw_rules = {self.ms_node: self.ms_rules_parent_path,
                         self.peer_nodes[0]: self.fw_rules_n1_path,
                         self.peer_nodes[1]: self.fw_rules_n2_path}

        self.postgres_service_name = const.PSQL_SERVICE_NAME
        self.postgres_data_dir = const.PSQL_9_6_DATA_DIR

        self.get_psql_version_cmd = "{0} postgres -c '{1} -U postgres -c "\
                                    "\"select version();\"'".format(
                                    const.SU_PATH, const.PSQL_PATH)

        self.pg_version_file = "{0}PG_VERSION".format(
                                    self.postgres_data_dir)
        self.postgres_version_num = "9.6"
        self.old_postgres_data_dir = "/var/lib/pgsql/data"
        self.puppetdb_log_path = "/var/log/puppetdb/puppetdb.log"

        self.pos_1_syslog = self.get_file_len(
            self.ms_node, const.GEN_SYSTEM_LOG_PATH)

        self.pos_1_puppetdb_log = self.get_file_len(
            self.ms_node, self.puppetdb_log_path)

    def tearDown(self):
        """ Runs after every single test """
        super(Story255505, self).tearDown()

    def verify_psql_version(self):
        """
        Description: Logs in as a postgres user, starts a psql terminal,
                     runs 'select version();' and verifies that the
                     PostgreSQL version is 9.6.
        """
        stdout, _, _ = self.run_command(self.ms_node,
                         self.get_psql_version_cmd, su_root=True,
                         default_asserts=True)

        self.assertTrue(self.is_text_in_list("PostgreSQL {0}".format(
                        self.postgres_version_num), stdout),
                        "postgreSQL 9.6 service does not appear to be the"
                        " current PostgreSQL version: '{0}'".format(stdout))

    def check_for_log_msg(self, message, log_len,
                          file_check=const.GEN_SYSTEM_LOG_PATH,
                          wait_for_log=False):
        """
        Description: Checks passed in log file for messages
                     expected to be present.

        Args:
            message (list/str): List of messages to check. If a str is
                                passed instead of a list, the system assumes
                                there is just one message.
            log_len (int): Will look for logs starting at log length
                           stated in this variable.
        Kwargs:
            file_check (str): path to file to check for the messages.
            wait_for_log (bool): if true will wait for the message to
                                 appear in the log, if false will check
                                 if its currently there. Default is false.

        """
        if isinstance(message, str):
            logs_to_check = [message]
        else:
            logs_to_check = message

        for log_msg in logs_to_check:

            if not wait_for_log:
                self.assertTrue(self.check_for_log(self.ms_node, log_msg,
                                               file_check, log_len),
                                               '"{0}" not found in {1} '
                                               'as expected.'.format(log_msg,
                                               file_check))
            else:
                self.assertTrue(self.wait_for_log_msg(self.ms_node, log_msg,
                                               log_file=file_check,
                                               log_len=log_len),
                                               '"{0}" not found in {1} '
                                               'as expected.'.format(log_msg,
                                               file_check))


    @attr('all', 'revert', 'story255505', 'story255505_tc01')
    def test_01_p_verify_postgresql96_is_running_ms(self):
        """
        @tms_id: torf_255505_tc01
        @tms_requirements_id: TORF-255505
        @tms_title: Verify PostgreSQL 9.6 is running on the MS.
        @tms_description: Verify current running PostgreSQL version is 9.6
        @tms_test_steps:
            @step: Check the status of the PostgreSQL 9.6 Service on the MS
            @result: Postgres 9.6 service is running
            @step: Login as a Postgres user, start a psql terminal and
                   check the postgres version
            @result: Version is 9.6
            @step: Check the psql version on the MS
            @result: Version is 9.6
            @step: Check the postgreSQL 9.6 data directory is not empty
            @result: Directory is not empty
            @step: Check the PG_VERSION file in the PostgreSQL data
                   directory contains the correct PostgreSQL version
            @result: File contains the correct version
        @tms_execution_type: Automated
        """

        self.log("info", "# 1. Check the status of the postgreSQL 9.6 Service"
                 " on the MS")

        self.get_service_status(self.ms_node, self.postgres_service_name)

        self.log("info", "# 2. Login as a Postgres user, start a psql terminal"
                 " and check the postgres version.")

        self.verify_psql_version()

        self.log("info", "# 3. Check the postgres version on the MS.")

        stdout, _, _ = self.run_command(self.ms_node, "{0} --version".format(
                       const.PSQL_PATH), default_asserts=True, su_root=True)

        self.assertTrue(self.is_text_in_list("psql (PostgreSQL) {0}".format(
                        self.postgres_version_num), stdout),
                        "PostgreSQL version isn't as expected: "
                        "{0}".format(stdout))

        self.log("info", "# 4. Check the postgreSQL 9.6 data directory "
                 "'{0}' is not empty.".format(self.postgres_data_dir))

        stdout = self.list_dir_contents(self.ms_node, self.postgres_data_dir,
                                        su_root=True)

        self.assertTrue(stdout != [], "Postgresql 9.6 data directory is"
                                      "empty!")

        self.log("info", "# 5. Check the PG_VERSION file in the postgreSQL "
                 "data directory contains the correct postgreSQL version.")
        pg_version_file_contents = self.get_file_contents(self.ms_node,
                                   self.pg_version_file,
                                   assert_not_empty=True, su_root=True)

        self.assertTrue(self.postgres_version_num ==
                         pg_version_file_contents[0],
                        "The pg_version file does not contain the correct "
                        "postgreSQL Version: "
                        "{0}".format(pg_version_file_contents[0]))

    @attr('all', 'revert', 'story255505', 'story255505_tc02')
    def test_02_p_verify_postgresql84_not_installed_ms(self):
        """
        @tms_id: torf_255505_tc02
        @tms_requirements_id: TORF-255505
        @tms_title: PostgreSQL 8.4 is not installed on the MS.
        @tms_description: Verify that the PostgreSQL 8.4 is not installed
                          on the MS
        @tms_test_steps:
            @step: Verify PostgreSQL 8.4 Data Directory doesn't exist
            @result: Directory doesn't exist
            @step: Check PostgreSQL 8.4 RPMs are not installed
            @result: "postgresql-server-8.4.20-1.el6_5.x86_64",
                     "postgresql-libs-8.4.20-1.el6_5.x86_64" and
                     "postgresql-8.4.20-1.el6_5.x86_64" are not installed.
        @tms_execution_type: Automated
        """

        self.log("info", "# 1. Verify PostgreSQL 8.4 Data Directory"
                 " '{0}' doesn't exist.".format(self.old_postgres_data_dir))

        old_data_dir = self.remote_path_exists(self.ms_node,
                                               self.old_postgres_data_dir,
                                               expect_file=False)

        self.assertFalse(old_data_dir, "Old PostgreSQL data directory "
                         "'{0}' exists!".format(self.old_postgres_data_dir))

        self.log("info", "# 2. Check PostgreSQL 8.4 RPMs are not installed.")

        postgres_8_4_packages = ["postgresql-libs-8.4.20-1.el6_5.x86_64",
                                 "postgresql-server-8.4.20-1.el6_5.x86_64",
                                 "postgresql-8.4.20-1.el6_5.x86_64"]

        stdout, _, _ = self.run_command(self.ms_node,
                            self.rh_utils.check_pkg_installed(
                            postgres_8_4_packages),
                            su_root=True)

        self.assertTrue(stdout == [], "Unexpected postgresql 8.4 package(s) "
                                      "found: {0}".format(stdout))

    @attr('all', 'revert', 'story255505', 'story255505_tc03')
    def test_03_p_verify_psycopg2_using_correct_libpq(self):
        """
        @tms_id: torf_255505_tc03
        @tms_requirements_id: TORF-255505
        @tms_title: Psycopg2 rpm is using the correct c client library
                    for PostgreSQL 9.6.
        @tms_description: Verify Psycopg2 is using the correct libpq for
                          PostgreSQL 9.6
        @tms_test_steps:
            @step: Check that psycopg2 is using the correct libpq
            @result:Psycopy2 is using the correct libpq
                   "(libpq.so.rh-postgresql96-5)"
        @tms_execution_type: Automated
        """
        self.log("info", "# 1. Check that psycopg2 is using the correct "
                 "libpq.")

        cmd = "ldd /opt/ericsson/nms/litp/3pps/lib/python/psycopg2"\
              "/_psycopg.so | {0} libpq".format(const.GREP_PATH)

        stdout, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                       default_asserts=True)

        self.assertTrue("libpq.so.rh-postgresql96-5" in stdout[-1], "Psycopg2"
                        " is not using the correct libpq: {0}".format(stdout))

    @attr('all', 'revert', 'story255505', 'story255505_tc04')
    def test_04_p_verify_syspath_rpms_installed(self):
        """
        @tms_id: torf_255505_tc04
        @tms_requirements_id: TORF-255505
        @tms_title: PostgreSQL syspath RPM's are installed
        @tms_description: Verify syspath RPM's are installed and PostgreSQL
                          executables remain the same as it's previous
                          version
        @tms_test_steps:
            @step: Verify that the syspath rpms are on the MS
            @result: Both syspath rpms are both installed
            @step: Login as a postgres user and start a psql terminal
            @result: A psql terminal starts for PostgreSQL 9.6
            @step: Check the status of the PostgreSQL service
            @result: The postgreSQL 9.6 service is running
        @tms_execution_type: Automated
        """
        postgres_syspath_pkgs = ["rh-postgresql96-postgresql-server-syspaths"
                                 "-9.6.10-1.el7.x86_64",
                                 "rh-postgresql96-postgresql-syspaths-"
                                 "9.6.10-1.el7.x86_64"]

        self.log("info", "# 1. Verify that the syspath rpms are on the MS.")

        stdout, _, _ = self.run_command(self.ms_node,
                            self.rh_utils.check_pkg_installed(
                            postgres_syspath_pkgs),
                            su_root=True, default_asserts=True)

        for pkg in postgres_syspath_pkgs:
            self.assertTrue(self.is_text_in_list(pkg, stdout),
                            "syspath package '{0}' is not "
                            "installed".format(pkg))

        self.log("info", "# 2. Login as a Postgres user, start a psql "
                 "terminal")

        self.verify_psql_version()

        self.log("info", "# 3. Check the status of the PostgreSQL service")

        self.get_service_status(self.ms_node, self.postgres_service_name)

    @attr('all', 'revert', 'story255505', 'story255505_tc05')
    def test_05_p_puppetdb_functionality_tests(self):
        """
        @tms_id: torf_255505_tc05
        @tms_requirements_id: TORF-255505
        @tms_title: PuppetDB functionality legacy tests
        @tms_description: Verify puppetDB continues to behave as expected
                          after migration to PostgreSQL 9.6
        @tms_test_steps:
            @step: Create/update items to generate config tasks on the ms
                   and peer nodes, create and run a plan
            @result: Plan executes successfully
            @step: Check the puppetdb log to verify the
                   facts and catalogs for ms and peer nodes has been
                   updated
            @result: Facts and catalogs for the nodes are updated in
                     puppetDB
            @step: Login as a postgres posix user and connect to the puppetdb
                   database
            @result: Login was successful
            @step: Check the certname_facts table in puppetDB contains the
                   'unique_id' facts about the MS and peer nodes
            @result: Table contains  the 'unique_id' facts about MS and the
                     peer nodes
        @tms_execution_type: Automated
        """

        self.log("info", "# 1.  Create/update items to generate config tasks "
                 "on the ms and peer nodes, create and run a plan.")

        for node in self.all_nodes:
            self.execute_cli_create_cmd(self.ms_node,
                                        "{0}/story_255505".format(
                                        self.fw_rules[node]),
                                       'firewall-rule',
                                        props="name='133 test'")

        self.run_and_check_plan(self.ms_node, const.PLAN_COMPLETE, 10)

        self.log("info", "# 4. Login as a postgres posix user and connect to "
                 "the puppetdb database.")

        db_table = "resource_params"

        cmd = "{0} postgres -c \"{1} -U postgres -h ms1 -d puppetdb -c "\
            "'SELECT * from {2};' -P pager=off\""\
            "| grep uniqueid".format(const.SU_PATH,
            const.PSQL_PATH, db_table)

        stdout = self.run_command(self.ms_node, cmd, su_root=True,
                    default_asserts=True)[0]

        uniqueids = {self.ms_node: "007f0100",
                    self.peer_nodes[0]: "a8c02b00",
                    self.peer_nodes[1]: "a8c02c00"}

        for node, uniqueid in uniqueids.iteritems():
            self.assertTrue(self.is_text_in_list(uniqueid, stdout),
            "{0} table does not contain uniqueid for {1}: {2}"
            .format(db_table, node, uniqueid))

    @attr('all', 'revert', 'story255505', 'story255505_tc06')
    def test_06_p_verify_postgresql96_running_after_ms_reboot(self):
        """
        @tms_id: torf_255505_tc06
        @tms_requirements_id: TORF-255505
        @tms_title: Verify PostgreSQL 9.6 service is running after an MS reboot
        @tms_description: Check that after the MS is rebooted that the
                          PostgreSQL 9.6 service is still running.
        @tms_test_steps:
            @step: Check the status of the PosgreSQL 9.6 service
            @result: PostgreSQL 9.6 is running
            @step: Reboot the MS
            @result: MS is rebooted
            @step: Check the PostgreSQL 9.6 service is running
            @result: PostgreSQL 9.6 is running
        @tms_execution_type: Automated
        """

        self.log("info", "# 1. Check the status of the PosgreSQL 9.6 service")

        self.get_service_status(self.ms_node, self.postgres_service_name)

        self.log("info", "# 2. Reboot the MS")

        reboot_cmd = "(sleep 1; {0} -r now) &".format(
                                        const.SHUTDOWN_PATH)


        self.run_command(self.ms_node, reboot_cmd, su_root=True,
                         default_asserts=True)

        self.log("info", "Waiting for node to become unreachable")

        self.assertTrue(self.wait_for_ping(self.ms_ip, False, retry_count=4),
                        "Node '{0} has not gone down".format(self.ms_node))

        self.log("info", "Waiting for node to come back online")

        self.assertTrue(self.wait_for_node_up(self.ms_node,
                       wait_for_litp=True),
                        "'{0} did not come up in expected timeframe"
                                                .format(self.ms_node))

        self.log("info", "# 3. Check the PostgreSQL 9.6 service is running.")

        self.get_service_status(self.ms_node, self.postgres_service_name)

    @attr('all', 'revert', 'story255505', 'story255505_tc07')
    def test_07_p_puppet_enables_postgresql96_if_disabled(self):
        """
        @tms_id: torf_255505_tc07
        @tms_requirements_id: TORF-255505
        @tms_title: Ensure Puppet re-enables the PostgreSQL 9.6 service
                    during a puppet run if it has been disabled
        @tms_description: Verify that Puppet will re-enable the PostgreSQL 9.6
                          service if it has been disabled
        @tms_test_steps:
            @step: Disable the PostgreSQL 9.6 service using the systemctl
                   command
            @result: PostgreSQL 9.6 service is disabled
            @step: Start a puppet run
            @result: Puppet run completes successfully
            @step: Check the status of the PostgreSQL 9.6 service using
                     systemctl
            @result: The PostgreSQL 9.6 service is running
        @tms_execution_type: Automated
        """

        self.log("info", "# 1. Disable the Post greSQL 9.6 service using the"
                 " systemctl command")

	cmd = self.rh_utils.get_systemctl_disable_cmd(self.postgres_service_name)

        self.run_command(self.ms_node, cmd, su_root=True, default_asserts=True)

        is_enbld_cmd = self.rh_utils.get_systemctl_isenabled_cmd(
                                                self.postgres_service_name)
        stdout, _, _ = self.run_command(self.ms_node, is_enbld_cmd, su_root=True)
        stdout_dis_err_msg = "{0} is not disabled as expected".format(
                                self.postgres_service_name)
        self.assertEqual(stdout[0], "disabled", stdout_dis_err_msg)

        self.log("info", "# 2. Start a new puppet run")

        self.start_new_puppet_run(self.ms_node)

        msg = "enable changed 'false' to 'true'"
        self.check_for_log_msg(msg, self.pos_1_syslog, wait_for_log=True)

        self.log("info", "# 3. Check the PostgreSQL 9.6 service is re-enabled "
                 "using the systemctl command")

        stdout, _, _ = self.run_command(self.ms_node, is_enbld_cmd, su_root=True)
        stdout_en_err_msg = "{0} is not enabled as expected".format(
                                self.postgres_service_name)
        self.assertEqual(stdout[0], "enabled", stdout_en_err_msg)
