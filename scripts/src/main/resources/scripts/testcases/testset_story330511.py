"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     April 2019
@author:    Sam Luby
@summary:   Integration tests for story 330511
"""

from litp_generic_test import GenericTest, attr
import test_constants as const


class Story330511(GenericTest):
    """
    TORF-330511: Uplift to Puppet 3.8.7, PuppetDB 2.3.x and migrate from
        Puppet Master to Puppet Server during import_iso of the LITP ISO.
    """
    def setUp(self):
        """Runs before every test"""
        super(Story330511, self).setUp()
        self.ms_node = self.get_management_node_filename()

    def tearDown(self):
        """Runs after every test"""
        super(Story330511, self).tearDown()

    @attr('pre-reg', 'revert', 'story330511', 'story330511_tc01')
    def test_01_p_verify_puppet_running_on_ms(self):
        """
        @tms_id:
            torf_330511_tc01
        @tms_requirements_id:
            TORF-330511
        @tms_title:
            Assert that puppetserver is running on the MS
        @tms_description:
            Assert that puppetserver is running on the MS
        @tms_test_steps:
            @step: Attempt to check the status of puppetserver on the MS.
            @result: Puppet server is running on the MS as expected.
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        service = "puppetserver"
        self.log('info', '1. Assert that puppetserver is running on the MS')
        self.get_service_status(self.ms_node, service)

    @attr('pre-reg', 'revert', 'story330511', 'story330511_tc02')
    def test_02_p_verify_puppet_certificates_synched(self):
        """
        @tms_id:
            torf_330511_tc02
        @tms_requirements_id:
            TORF-330511
        @tms_title:
            Verify puppet has synced it's certificate with each of the
                services ca.pem files (PuppetDB, RabbitMQ, MCollective)
        @tms_description:
            Verify that each service's ca.pem file matches that of the puppet
                ca.pem file.
        @tms_test_steps:
            @step: Check the value contained in:
                "/var/lib/puppet/ssl/certs/ca.pem"
            @result: Value retrieved successfully.
            @step: Check the value contained in the ca.pem files for the
                following services MCollective, PuppetDB, RabbitMQ and verify
                it matches the value retrieved from puppets ca.pem file.
            @result: All ca.pem files for each of the services match that of
                the puppet cert value.
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        service_certs = ['/etc/mcollective/ca.pem',
                        '/etc/rabbitmq/ssl/ca.pem',
                        '/etc/puppetdb/ssl/ca.pem']
        self.log('info', '1. Check the value in {0}'
                .format(const.PUPPET_CERT_PATH))
        puppet_contents = self.get_file_contents(self.ms_node,
                            const.PUPPET_CERT_PATH, su_root=True)

        self.log('info', '2. Check the value in the ca.pem files for each '
                'service')
        for cert in service_certs:
            cert_contents = self.get_file_contents(self.ms_node, cert,
                                su_root=True)
            self.assertEqual(cert_contents, puppet_contents,
                'Contents of {0} does not match puppet cert contents'
                .format(cert))
