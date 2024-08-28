"""
COPYRIGHT Ericsson 2022
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Dec 2022
@author:    Eoin Hughes
@summary:   TORF-625825
            As
"""
from litp_generic_test import GenericTest, attr


class Story625825(GenericTest):
    """
    TORF-625825
        Verify functionality of EXTRlitpsentinellicensemanager
    """

    def setUp(self):
        """Run before every test"""
        super(Story625825, self).setUp()
        self.ms_node = self.get_management_node_filename()
        self.lslic = "/opt/SentinelRMSSDK/bin/lslic"
        self.list_licenses_cmd = "/opt/SentinelRMSSDK/bin/lsmon localhost"
        self.test_license = {
            "key": ("14 FAT1023070 Ni LONG NORMAL NETWORK EXCL 1000000"
                " INFINITE_KEYS 9 AUG 2022 1 FEB 2023 NO_SHR SLM_CODE 1 NON_CO"
                "MMUTER NO_GRACE NO_OVERDRAFT DEMO NON_REDUNDANT Ni NO_HLD 20 "
                "Radio_Network_Base_Package_numberOf_5MHzSC 5g4xre0hiWeMV041cf"
                "oJf:t5jPuWxd,Yu5DHwa,j15VpRwM5zLlM6vNXA3jarLxNVLVb0ibe,BcHqrs"
                "t1vQJm9VPqw,JswtvOpuXzXitJPC0VReeIcpTXPqK6b829yXtmXfX"),
            "hash": "BD843312CFE13203",
            "version": "",
            "name": "FAT1023070",
        }

    def tearDown(self):
        """Run after every test"""
        super(Story625825, self).tearDown()

    def _check_sentinel_license(self, license_key):
        """
        Description
            Checks if a license is listed in Sentinel
        Returns:
            True if the license is listed, False if not
        Actions:
            1. Lists the avabile license
            2. Checks that the listed license is in the output
        """
        stdout, _, retcode = self.run_command(self.ms_node,
            "{0}".format(self.list_licenses_cmd))
        self.assertTrue(retcode in (0, 1),
            "{0} returned code: {1}".format(self.list_licenses_cmd, retcode))
        found = False
        for line in stdout:
            if license_key in line:
                found = True
                break
        return found

    def _add_sentinel_license(self, license_key):
        """
        Description
            Adds a license to Sentinel
        Actions:
            1. Creates a temporary file containing the license key
            2. Calls lslic to add the file
            3. Deletes the temporary file
        """
        tmpfile = "/tmp/625825_tc01.txt"
        self.run_command(self.ms_node, "echo '{0}' > {1}".format(license_key,
            tmpfile), default_asserts=True)

        _, _, sentinel_rc = self.run_command(self.ms_node,
            "{0} -F {1}".format(self.lslic, tmpfile))
        self.assertEquals(sentinel_rc, 0,
            "'{0} -F {1}' returned {2}".format(self.lslic, tmpfile,
                sentinel_rc))

        self.run_command(self.ms_node, "rm {0}".format(tmpfile),
            default_asserts=True)

    def _delete_sentinel_license(self, license_name, license_version,
                                    license_hash):
        """
        Description
            Deletes a license from Sentinel
        Actions:
            1. Uses lslic to remove a license
        """
        _, _, retcode = self.run_command(self.ms_node,
            "echo 'y' | {0} -DL '{1}' '{2}' '{3}'".format(self.lslic,
                license_name, license_version, license_hash))
        self.assertEquals(retcode, 0,
            "Failed to remove license from Sentinel service")

    @attr('revert', 'story625825', 'story625825_tc01')
    def test_add_remove_license(self):
        """
        @tms_id: torf_625825_tc01
        @tms_requirements_id: TORF-625825
        @tms_title: Add and remove license from sentinel service
        @tms_description: Test ensures we can add/remove a license on Sentinel
        @tms_test_steps:
            @step: Add a license to Sentinel
            @result: License is listed in Sentinel
            @step: Remove a license from Sentinel
            @result: Licnse is not listed in Sentinel
        @tms_test_precondition:NA
        @tms_execution_type: Automated
        """
        # Precondition: Check license is not present
        self.assertFalse(self._check_sentinel_license(
            self.test_license["name"]),
            "License is already present in Sentinel")

        # Step: Add license
        self._add_sentinel_license(self.test_license["key"])

        # Test: Check for license
        self.assertTrue(self._check_sentinel_license(
            self.test_license["name"]),
            "License is not found on server after it has been added")

        # Delete license
        self._delete_sentinel_license(self.test_license["name"],
            self.test_license["version"], self.test_license["hash"])

        # Test: Check license is absent
        self.assertFalse(self._check_sentinel_license(
            self.test_license["name"]),
            "License is still present on server after deletion")
