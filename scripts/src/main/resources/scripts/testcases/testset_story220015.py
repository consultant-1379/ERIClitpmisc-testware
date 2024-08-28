"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Nov 2017
@author:    Laura Forbes
@summary:   TORF-220015
            As a LITP user I want stricter security on the PostgreSQL DB
            on the MS so that only the necessary users can connect to
            their respective databases (DTAG Item 40)
@summary:   TORF-222550
            As a LITP user I want passwords configured for all users of the
            PostgreSQL DB on the MS (DTAG Item 14)
"""

from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
import test_constants as const


class Story220015(GenericTest):
    """
        As a LITP user I want stricter security on the PostgreSQL DB
            on the MS so that only the necessary users can connect to
                their respective databases (DTAG Item 40)'
        TORF-222550
        As a LITP user I want passwords configured for all users of the
            PostgreSQL DB on the MS (DTAG Item 14)
    """

    def setUp(self):
        """ Runs before every single test """
        super(Story220015, self).setUp()

        self.rhel = RHCmdUtils()
        self.ms_node = self.get_management_node_filename()
        self.ms_ip = self.get_node_att(self.ms_node, 'ipv4')
        self.node1 = self.get_managed_node_filenames()[0]
        self.pgsql_data_dir = const.PSQL_9_6_DATA_DIR
        self.pg_hba_conf = '{0}pg_hba.conf'.format(self.pgsql_data_dir)
        self.pg_ident_conf = '{0}pg_ident.conf'.format(self.pgsql_data_dir)
        self.listen_address = "127.0.0.1"
        self.port = "5432"

    def tearDown(self):
        """ Runs after every single test """
        super(Story220015, self).tearDown()

    def _check_pg_db_login(self, user, db_name, table,
                           root_user=True, expect_access=True,
                           tcp_ip_address=False):
        """
        Description:
            Checks if the stated Postgres user can log into the specified
            Postgres database from the MS as user root and show the given table
        Args:
            user (str): PostgreSQL user.
            db_name (str): Database to attempt to login to.
            table (str): Table in database to assert user can access.
        Kwargs:
            root_user (bool): Whether to run command
                as root user. Default is True.
            expect_access (bool): Whether the login attempt is
                expected to be successful. Default is True.
            tcp_ip_address (bool): True if login attempt includes connection
                                   from tcp ip address. Default is false.
        """
        postgres_cmd = "{0} -U {1} -d {2} -c".format(const.PSQL_PATH, user,
                                                     db_name)

        # If user is postgres, need to su to
        # postgres user before checking access
        if user == "postgres":
            cmd = "{0} - postgres -c \"{1} ".format(const.SU_PATH,
                                                    postgres_cmd)
            if table is not None:
                cmd += "'SELECT * FROM {0}'\"".format(table)
            else:
                # Used when databases have no tables. Simply test access
                cmd += r"'\l'" + '"'
        else:
            cmd = "{0} 'SELECT * FROM {1}'".format(postgres_cmd, table)

        std_out, std_err, rc = self.run_command(
            self.ms_node, cmd, su_root=root_user)

        if expect_access:
            self.assertEqual(0, rc)
            self.assertNotEqual([], std_out)
        else:
            self.assertNotEqual(0, rc)
            if root_user:
                if tcp_ip_address:
                    fatal_error = "psql: FATAL:  pg_hba.conf rejects " \
                                  "connection for host"
                else:
                    fatal_error = "psql: FATAL:  no pg_hba.conf entry for host"

                self.assertTrue(fatal_error in std_out[0],
                                "Expected error message not "
                                "returned: {0}".format(fatal_error))
            else:
                fatal_error = "psql: FATAL:  no pg_hba.conf entry for host"
                # fatal_error = \
                #     "psql: FATAL:  Peer authentication failed for user"
                self.assertTrue(fatal_error in std_err[0],
                                "Expected error message not "
                                "returned: {0}".format(fatal_error))

    @attr('all', 'revert', 'story220015', 'story220015_tc10')
    def test_10_p_postgresql_security_checks(self):
        """
            @tms_id: torf_220015_tc10
            @tms_requirements_id: TORF-220015
            @tms_title: PostgreSQL Security Checks
            @tms_description: PostgreSQL security is implemented correctly
            @tms_test_steps:
                @step: Check pg_hba.conf contents
                @result: Contents are as expected
                @step: Check values in postgresql.conf
                @result: Values are correct
                @step: Assert databases can be accessed by verified users on MS
                @result: Verified users can access databases
                @step: Assert databases cannot be accessed
                    by non-verified users on MS
                @result: Non-verified users do not have access to databases
                @step: Assert LITP databases cannot be
                    accessed from somewhere other than MS
                @result: LITP databases not accessible from outside MS
            @tms_test_precondition: None
            @tms_execution_type: Automated
        """
        # TEST CASE 1
        self.log("info", "1. Check that {0} has expected "
                         "contents.".format(self.pg_hba_conf))
        # Expected contents of pg_hba.conf file with whitespace (tabs) removed
        pga_hba_contents = [
            'hostssllitplitp{0}/32certclientcert=1'.format(self.listen_address),
            'hostssllitpcelerylitp{0}/32certclientcert=1'.format(self.listen_address),
            'hostsslpostgreslitp{0}/32certclientcert=1'.format(self.listen_address),
            'hostsslallpostgres{0}/32certclientcert=1'.format(self.listen_address),
            'hostpuppetdbpuppetdb{0}/32md5'.format(self.listen_address),
            'localpostgrespostgresident',
            'hostallall0.0.0.0/0reject',
            'hostallall::/0reject']

        # Extract all uncommented lines from file
        cmd = "{1} -v '^#' {0} | {1} -v '^$'".format(self.pg_hba_conf,
                                                     const.GREP_PATH)
        std_out, _, _ = self.run_command(self.ms_node, cmd, su_root=True)
        # Remove all tabs for easy comparison with expected content
        actual_hba = [x.replace("\t", "") for x in std_out]
        self.assertEqual(pga_hba_contents, actual_hba)

        # TEST CASE 2
        self.log("info", "2.1 Assert that {0} has the expected values for "
                         "'log_destination', 'log_disconnections', "
                         "'log_connections', 'log_hostname', 'listen_address'"
                         " & 'port'.".format(const.PSQL_9_6_CONF_FILE))
        # STEP 1
        pg_conf = ["listen_addresses = '{0}'".format(self.listen_address),
                   "port = {0}".format(self.port),
                   "log_disconnections = off",
                   "log_destination = syslog",
                   "log_connections = off",
                   "log_hostname = on"]
        # Grep lines from
        # '/var/opt/rh/rh-postgresql96/lib/pgsql/data/postgresql.conf'
        # excluding blank and lines beginning with hash.
        cmd = "{0} -vxE '[[:blank:]]*([#;].*)?' {1} ".format(
            const.GREP_PATH, const.PSQL_9_6_CONF_FILE)
        std_out, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                                         default_asserts=True)
        # Remove hashed comments from any partially hashed lines.
        postgres_conf_list = []
        for line in std_out:
            new_line = line.split("#")[0]
            postgres_conf_list.extend([new_line])
        # Assert that the desired settings are in the conf file.
        for setting in pg_conf:
            self.assertTrue(setting in postgres_conf_list)

        # STEP 2
        self.log("info", "2.2 Assert that the MS uses the expected values for"
                         " 'listen_address' and 'port'.")
        cmd = '{0} -ntlp | {1} postgres'.format(const.NETSTAT_PATH,
                                                const.GREP_PATH)
        std_out, _, rc = self.run_command(self.ms_node, cmd, su_root=True)
        self.assertEqual(0, rc)
        # Only 1 line should be returned
        self.assertEqual(1, len(std_out))
        address_port = "{0}:{1}".format(self.listen_address, self.port)
        self.assertTrue(address_port in std_out[0],
                        "Expected postgres address:port "
                        "{0} not returned.".format(address_port))

        # STEP 3
        cmd = "{0} -elf | {1} /opt/rh/rh-postgresql96/root/usr/bin/".format(
            const.PS_PATH, const.GREP_PATH)
        std_out, _, rc = self.run_command(self.ms_node, cmd, su_root=True)
        self.assertEqual(0, rc)

        postgres_pid = [x for x in std_out if "grep" not in \
                        x][0].split()[3]
        cmd = "{0} -nlp | {1} {2}".format(const.NETSTAT_PATH,
                                          const.GREP_PATH, postgres_pid)
        std_out, _, rc = self.run_command(self.ms_node, cmd, su_root=True)
        self.assertEqual(0, rc)
        # Only 3 lines should be returned
        self.assertEqual(3, len(std_out))
        self.assertTrue(all(self.port in s for s in std_out),
                        "Test to see if postgres is listening on a port "
                        "other than {0} failed.".format(self.port))

        # TEST 3
        self.log("info", "3. Assert that databases can be "
                         "accessed by verified users on the MS.")
        cmd = "{0} -v '^#' {1} | {0} -v '^$'".format(const.GREP_PATH,
                                                     self.pg_ident_conf)
        std_out, _, rc = self.run_command(self.ms_node, cmd, su_root=True)
        #self.assertEqual(0, rc)
        self.assertEqual(0, len(std_out))

        """
        # Create lists for expected output & actual output
        expected_output_list = []
        output_list = [std_out[0].replace("\t", ""),
                       std_out[1].replace("\t", "")]

        # Check if expected_output_list contains all elements of output_list
        # using all()
        result = all(elem in output_list for elem in expected_output_list)
        self.assertTrue(result, 'Not all the expected items were in '
                                'the pg_ident.conf file'
                        .format(expected_output_list))
                        """

        # Test databases can be accessed by verified users on MS
        self._check_pg_db_login("litp", "litp -h ms1", "plan_tasks")
        self._check_pg_db_login("litp", "litpcelery -h ms1", "celery_tasksetmeta")
        self._check_pg_db_login("postgres", "litp -h ms1", "plan_tasks")
        self._check_pg_db_login("postgres", "litpcelery -h ms1", "celery_tasksetmeta")
        self._check_pg_db_login("postgres", "postgres -h ms1", None)
        self._check_pg_db_login("postgres", "puppetdb -h ms1", "catalogs")
        self._check_pg_db_login("postgres", "template1 -h ms1", None)

        # Specify port: -p 5432
        cmd = "{0} -U litp -p 5432 litp -h ms1 -c ".format(const.PSQL_PATH)
        cmd += "'SELECT * FROM plan_tasks'"
        std_out, _, rc = self.run_command(self.ms_node, cmd, su_root=True)
        self.assertEqual(0, rc)
        self.assertNotEqual([], std_out)

        # TEST 4
        self.log("info", "4. Assert that databases cannot be "
                         "accessed by non-verified users on MS.")
        self._check_pg_db_login(
            "litp", "puppetdb", "whatever", expect_access=False)
        self._check_pg_db_login(
            "litp", "template1", "whatever", expect_access=False)
        # self._check_pg_db_login(
        #     "litp", "litp -h 127.0.0.1", "whatever", expect_access=False,
        #     tcp_ip_address=True)
        self._check_pg_db_login(
            "puppetdb", "litp", "whatever", expect_access=False)
        self._check_pg_db_login(
            "puppetdb", "litpcelery", "whatever", expect_access=False)
        self._check_pg_db_login(
            "puppetdb", "postgres", "whatever", expect_access=False)
        self._check_pg_db_login(
            "puppetdb", "template1", "whatever", expect_access=False)

        # Ensure that attempts to access the databases as litp-admin user fails
        self._check_pg_db_login(
            "litp", "litp", "whatever", root_user=False, expect_access=False)
        self._check_pg_db_login("litp", "litpcelery", "whatever",
                                root_user=False, expect_access=False)

        # TEST 5
        self.log("info", "5. Assert that LITP databases cannot be "
                         "accessed from somewhere other than MS.")
        pg_packages = ["rh-postgresql96-postgresql-9.6.10-1.el7.x86_64",
                       "rh-postgresql96-postgresql-server-9.6.10-1.el7.x86_64",
                       "rh-postgresql96-postgresql-libs-9.6.10-1.el7.x86_64",
                       "rh-postgresql96-postgresql-syspaths-9.6.10-1.el7."
                       "x86_64",
                       "rh-postgresql96-postgresql-server-syspaths-9.6.10-1."
                       "el7.x86_64"]

        # Install postgresql package on node1
        if not self.check_pkgs_installed(self.node1, pg_packages):
            for pg_package in pg_packages:
                self.log("info", "Installing package '{0}' on {1} "
                                 "for test.".format(pg_package, self.node1))

                self.assertTrue(self.install_rpm_on_node(self.node1,
                                                         pg_package))

        databases = ['litp', 'litpcelery']
        for db_name in databases:
            cmd = "{0} -h {1} -U litp -d {2}".format(const.PSQL_PATH,
                                                     self.ms_ip, db_name)
            std_out, _, rc = self.run_command(self.node1, cmd,
                                              su_timeout_secs=180, su_root=True)
            self.assertNotEqual(0, rc)
            expected_error = "could not connect to server"
            self.assertTrue(any(expected_error in s for s in std_out))

    @attr('all', 'revert', 'story222550', 'story222550_tc03')
    def test_03_p_postgresql_password_hash_checks(self):
        """
            @tms_id: torf_222550_tc03
            @tms_requirements_id: TORF-222550
            @tms_title: Verify "pg_shadow" table contents
            @tms_description: Verify the contents of pg_shadow table
                in postgres DB on the Management Server
            @tms_test_steps:
                @step: Verify 'pg_shadow' table contents
                @result: Contents are as expected
            @tms_test_precondition: None
            @tms_execution_type: Automated
        """
        # TEST CASE 3
        self.log("info", "3. Verify 'pg_shadow' table contents ")
        db_name = 'postgres'
        db_user = 'postgres'
        table = 'pg_shadow'
        postgres_cmd = "{0} -U {1} -d {2} -c".format(const.PSQL_PATH,
                                                     db_user, db_name)

        # Check usrname and passwd from DB
        cmd = "{0} - postgres -c \"{1} ".format(const.SU_PATH,
                                                postgres_cmd)
        cmd += "'SELECT usename, passwd FROM {0}; '\" ".format(table)
        std_out, _, rc = self.run_command(
            self.ms_node, cmd, su_root=True)
        self.assertEqual(0, rc)
        self.assertNotEqual([], std_out)

        # Expected passwd hashes and their usernames
        pg_shadow_contents = ['puppetdb | md53cbf124486f5dca866b9eb0d6a3bb314',
                              'postgres | md5958e1c4182a7ba15d80dd107f211e35a',
                              'litp     | md507ee58eb387feb097a5edcdbd0928059']

        # Assert hashes are in Query replay
        for val in pg_shadow_contents:
            self.assertTrue(val in std_out)
