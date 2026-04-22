import importlib.util
import os
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        'src',
        'addons',
        'send2ue',
        'dependencies'
    )
)
from rpc.factory import RPCFactory


class TestRPCFactory(unittest.TestCase):
    def _load_module(self, source):
        temp_dir = tempfile.TemporaryDirectory()
        module_path = os.path.join(temp_dir.name, 'temp_rpc_module.py')
        with open(module_path, 'w', encoding='utf-8') as handle:
            handle.write(textwrap.dedent(source))

        spec = importlib.util.spec_from_file_location('temp_rpc_module', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, temp_dir

    def test_get_code_strips_indented_triple_double_quote_docstring(self):
        module, temp_dir = self._load_module('''
            def sample_function():
                """
                Checks to see if a directory exist in unreal.
                """
                return 42
        ''')
        self.addCleanup(temp_dir.cleanup)

        factory = RPCFactory(rpc_client=mock.MagicMock())
        with mock.patch.object(RPCFactory, '_get_callstack_references', return_value=''):
            code = factory._get_code(module.sample_function)

        joined = '\n'.join(code)
        self.assertNotIn('Checks to see if a directory exist in unreal.', joined)
        self.assertNotIn('"""', joined)
        self.assertIn('return 42', joined)

    def test_get_code_strips_indented_triple_single_quote_docstring(self):
        module, temp_dir = self._load_module("""
            def sample_function():
                '''
                Single quoted docstring.
                '''
                return 7
        """)
        self.addCleanup(temp_dir.cleanup)

        factory = RPCFactory(rpc_client=mock.MagicMock())
        with mock.patch.object(RPCFactory, '_get_callstack_references', return_value=''):
            code = factory._get_code(module.sample_function)

        joined = '\n'.join(code)
        self.assertNotIn('Single quoted docstring.', joined)
        self.assertNotIn("'''", joined)
        self.assertIn('return 7', joined)


if __name__ == '__main__':
    unittest.main()
