######################################################################
STORY 11799
######################################################################
The entire testset_story11799 is obsoleted

TEST: test_01_p_flash_and_jre_are_installed

DESCRIPTION: Test to ensure that flash_plugin and jre are installed on
                 the MS and there is a symbolic link to the Java Plugin
                 in the Firefox plugins directory

REASON WHY OBSOLETED: Flash_plugin and jre1.8.0_172 are no longer installed
                          due to TORF-543215

GERRIT LINK: https://gerrit.ericsson.se/#/c/10802770/

TMS ID: litpcds_11799_tc01

######################################################################
STORY 11050
######################################################################
The entire testset_story11050 is obsoleted

TEST: test_03_p_verify_erlang_version

DESCRIPTION: Verify that the "erlang" is installed in version 17.5 on MS node

REASON WHY OBSOLETED: Test moved to testset_story1934 script as test_06_p_verify_erlang_version

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: litpcds_11050_tc03

######################################################################
STORY 2892
######################################################################
The entire testset_story2892 is obsoleted

TEST: test_04_n_verify_no_rabbitmq_on_nodes

DESCRIPTION: Verify that "rabbitmq" is not installed on managed nodes

REASON WHY OBSOLETED: Test moved to testset_story1934 script as test_02_n_verify_no_rabbitmq_on_nodes

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: litpcds_2892_tc04

######################################################################
STORY 8281
######################################################################
The entire testset_story8281 is obsoleted

TEST: test_01_p_check_rsyslog_version_on_all_nodes

DESCRIPTION: Check that on an initial install of the MS and Peer nodes
             the version of the running rsyslog on them is the major version 7
			
REASON WHY OBSOLETED: Test moved to testset_story1934 script as test_03_p_check_rsyslog_version_on_all_nodes

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: litpcds_8281_tc01

######################################################################
STORY 9630
######################################################################
The entire testset_story9630 is obsoleted

TEST: test_01_p_extrlitprsyslog8_is_available

DESCRIPTION: To ensure that the rsyslog8 package is avaiable via a yum search
             initiated on both the management server and the peer nodes.
			
REASON WHY OBSOLETED: Test moved to testset_story1934 script as test_04_p_extrlitprsyslog8_is_available

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: litpcds_9630_tc01

######################################################################
STORY 9961
######################################################################
The entire testset_story9961 is obsoleted

TEST: test_03_p_verify_rabbitmq_version

DESCRIPTION: Verify that RabbitMQ version running on the MS is 3.5.4

REASON WHY OBSOLETED: Test merged with test_04_p_verify_rabbitmq_description
           and moved to testset_story1934 script as test_05_verify_rabbitmq_version_description
		   
GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/3

TMS ID: litpcds_9961_tc03

----------------------------------------------------------------------
TEST: test_04_p_verify_rabbitmq_description

DESCRIPTION: Verify that when I check the version of EXTRlitprabbitmqserver
             using rpm -qi command then the repackaged version of
             RabbitMQ-Server is 3.5.4 in the description field
			 
REASON WHY OBSOLETED: Test merged with test_03_p_verify_rabbitmq_version and  moved to testset_story1934 script as test_05_verify_rabbitmq_version_description
			
GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: litpcds_9961_tc04

######################################################################
STORY 12224
######################################################################
The entire testset_story12224 is obsoleted

TEST: test_01_p_item_types_by_id

DESCRIPTION: Check that all item types can be retrieved by ID.

REASON WHY OBSOLETED: This test checks the docs RPM which was removed from the LITP ISO (see CIS-91540), so it is no longer valid

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: NA

----------------------------------------------------------------------
TEST: test_02_p_prop_types_by_id

DESCRIPTION: Check that all property types can be retrieved by ID.

REASON WHY OBSOLETED: This test checks the docs RPM which was removed from the LITP ISO (see CIS-91540), so it is no longer valid

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: NA

----------------------------------------------------------------------
TEST: test_03_p_extensions_by_id

DESCRIPTION: Check that all documented extensions have .conf files.

REASON WHY OBSOLETED: This test checks the docs RPM which was removed from the LITP ISO, so it is no longer valid

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: NA

----------------------------------------------------------------------
TEST: test_04_p_plugin_by_id

DESCRIPTION: Check that all documented plugins have .conf files.

REASON WHY OBSOLETED: This test checks the docs RPM which was removed from the LITP ISO, so it is no longer valid

GERRIT LINK: https://gerrit.ericsson.se/#/c/4634472/

TMS ID: NA

######################################################################
STORY LITPCDS-8281
######################################################################

TEST: test_03_p_check_rsyslog_version_on_all_nodes

DESCRIPTION: Verify that rsyslog7 is running on initial install

REASON WHY OBSOLETED: This test was needed at RHEL6 to check that a non-standard and advanced version
                      of rsyslog was installed. It is not needed at RHEL7 as the version of rsyslog
                      provided by default is 8.24.0.

GERRIT LINK: https://gerrit.ericsson.se/#/c/10031284

TMS ID: litpcds_8281_tc01
