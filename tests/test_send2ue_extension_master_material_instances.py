from utils.base_test_case import BaseSend2ueTestCaseCore, SkipSend2UeTests


class TestSend2UeExtensionMasterMaterialInstances(SkipSend2UeTests, BaseSend2ueTestCaseCore):
    def test_extension(self):
        """
        Checks that the master material instances extension loaded properly.
        """
        self.run_extension_tests({
            'default': {
                'master_material_instances': {
                    'tasks': [
                        'post_import'
                    ]
                }
            }
        })
