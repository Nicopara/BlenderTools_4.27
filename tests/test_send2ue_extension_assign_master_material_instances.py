from utils.base_test_case import BaseSend2ueTestCaseCore, SkipSend2UeTests
from test_send2ue_cubes import TestSend2UeCubes


class TestSend2UeExtensionAssignMasterMaterialInstances(
    SkipSend2UeTests,
    BaseSend2ueTestCaseCore,
    TestSend2UeCubes
):
    """
    Runs extension presence checks for assign master material instances.
    """

    def test_extension(self):
        """
        Checks that the assign master material instances extension loaded properly.
        """
        self.run_extension_tests({
            'default': {
                'assign_master_material_instances': {
                    'properties': {
                        'material_instance_folder': ''
                    },
                    'tasks': [
                        'post_import'
                    ],
                    'draws': [
                        'draw_paths'
                    ]
                }
            }
        })
