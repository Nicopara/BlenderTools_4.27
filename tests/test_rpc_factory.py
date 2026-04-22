import importlib.util
import os
import sys
import tempfile
import textwrap
import unittest
import warnings
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
    @staticmethod
    def _load_module(source, temp_dir):
        module_path = os.path.join(temp_dir, 'temp_rpc_module.py')
        with open(module_path, 'w', encoding='utf-8') as handle:
            handle.write(textwrap.dedent(source))

        spec = importlib.util.spec_from_file_location('temp_rpc_module', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_get_code_strips_indented_triple_double_quote_docstring(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module = self._load_module('''
                def sample_function():
                    """
                    Checks to see if a directory exists in unreal.
                    """
                    return 42
            ''', temp_dir)

            factory = RPCFactory(rpc_client=mock.MagicMock())
            with mock.patch.object(RPCFactory, '_get_callstack_references', return_value=''):
                code = factory._get_code(module.sample_function)

            joined = '\n'.join(code)
            self.assertNotIn('Checks to see if a directory exists in unreal.', joined)
            self.assertNotIn('"""', joined)
            self.assertIn('return 42', joined)

    def test_get_code_strips_indented_triple_single_quote_docstring(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module = self._load_module("""
                def sample_function():
                    '''
                    Single quoted docstring.
                    '''
                    return 7
            """, temp_dir)

            factory = RPCFactory(rpc_client=mock.MagicMock())
            with mock.patch.object(RPCFactory, '_get_callstack_references', return_value=''):
                code = factory._get_code(module.sample_function)

            joined = '\n'.join(code)
            self.assertNotIn('Single quoted docstring.', joined)
            self.assertNotIn("'''", joined)
            self.assertIn('return 7', joined)

    def test_factory_module_has_no_invalid_escape_sequence_syntax_warning(self):
        module_path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'src',
            'addons',
            'send2ue',
            'dependencies',
            'rpc',
            'factory.py'
        )

        with open(module_path, 'r', encoding='utf-8') as handle:
            source = handle.read()

        with warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile(source, module_path, 'exec')


if __name__ == '__main__':
    unittest.main()
