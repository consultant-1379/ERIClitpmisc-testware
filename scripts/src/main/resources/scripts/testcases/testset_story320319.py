"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Jan 2019
@author:    Gordon Leary
@summary:   TORF-320319
            As a LITP engineer, I need an automated procedure to configure the
            expiry date of LITP software certificates by 50 years during
            initial install
"""

from litp_generic_test import GenericTest, attr
from dateutil.relativedelta import relativedelta
import datetime
import re
import test_constants


class Story320319(GenericTest):

    """
        As a LITP engineer, I need an automated procedure to configure the
        expiry date of LITP software certificates by 50 years during
        initial install
    """

    def setUp(self):
        """Setup variables for every test"""
        super(Story320319, self).setUp()
        self.ms1 = self.get_management_node_filename()

        self.log("info", "Get current date and date 50 years in the future.")
        self.install_date = datetime.datetime.now()
        self.log("info", "Current date: {0}".format(self.install_date))
        self.fifty_years_after_install_date = self.install_date \
                                              + relativedelta(years=50)
        self.fifty_years_after_install_year = \
            self.fifty_years_after_install_date.year

        self.openssl_command = '/usr/bin/openssl x509 -enddate -noout -in'

        self.cert_expiry_commands_dict = {
            "puppet": "{0} cert print {1} | {2} After".format(
                test_constants.PUPPET_PATH, self.ms1,
                test_constants.GREP_PATH),
            "puppetdb": "{0} /etc/puppetdb/ssl/ca.pem".format(
                self.openssl_command),
            "rabbitmq": "{0} /etc/rabbitmq/ssl/ca.pem".format(
                self.openssl_command),
            "mcollective": "{0} /etc/mcollective/ca.pem".format(
                self.openssl_command),
            "ericsson": "{0} /opt/ericsson/nms/litp/etc/ssl/litp_server"
                        ".cert".format(self.openssl_command)
        }

    def tearDown(self):
        """Runs for every test"""
        super(Story320319, self).tearDown()

    @attr('all', 'revert', 'story320319', 'story320319_tc01')
    def test_p_01_verify_50_year_cert_expiration(self):
        """
        @tms_id: torf_320319_tc01
        @tms_requirements_id: TORF-320319
        @tms_title: 50 Year Cert for LITP vApp initial install (Positive)
        @tms_description:
            When a LITP ISO is installed on LITP vApp, verify that the
            certificate expiry date is set to 50 years in the future for;
            Puppet, PuppetDB, RabbitMQ, Mcollective, Cherrypy
        @tms_test_steps:
         @step: On MS - execute show expiration date command for the following
          services: Puppet, PuppetDB, Mcollective, Cherrypy, RabbitMQ
         @result: Certificate expiry date is configured to become 50 years
         from the initial install date on the MS and all peer nodes on the
         following services: Puppet, PuppetDB, Mcollective, Cherrypy, RabbitMQ
         @step: Confirm install date + 50 years equals certificate expiry
         date returned from running command on MS
         @result: Certificate date is as expected
        @tms_test_precondition: LITP ISO is installed on LITP vApp
        @tms_execution_type: Automated
        """
        for service, command in self.cert_expiry_commands_dict.items():
            self.log("info", "#1 Execute cmd on MS: {0}".format(command))

            return_from_ms_command, _, _ = self.run_command(
                self.ms1, command, su_root=True, default_asserts=True)

            self.assertTrue(return_from_ms_command,
                            "Running command {0} on node {1} did not "
                            "return anything".format(command, self.ms1))

            year_match = re.match(r'.*([1-3][0-9]{3})',
                                  return_from_ms_command[0])

            self.assertTrue(year_match,
                            "no year found in return after running"
                            " command {0} on node {1}"
                            .format(command, self.ms1))

            date_returned_from_cmd = int(year_match.group(1))

            self.log("info","#2 Confirming that service {0} on node {1} has "
                            "expiry date set to 50 years from LITP install "
                            "date: {2}.".format(
                service, self.ms1, self.fifty_years_after_install_year))

            self.assertEqual(self.fifty_years_after_install_year,
                             date_returned_from_cmd,
                             "{2} is reporting expiry of {1}. Expected {0}.".format(
                                 self.fifty_years_after_install_year,
                                 date_returned_from_cmd, service))
