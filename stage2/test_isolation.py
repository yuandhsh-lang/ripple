"""Launch guards reject shared historical state before starting any process."""
import importlib.util, json, socket, unittest, uuid
from pathlib import Path
from unittest.mock import patch

WORK = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('isolation_verify', WORK/'stage1/verify.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

class Isolation(unittest.TestCase):
    def setUp(self):
        self.root = WORK/'stage2/runtime/runs'/('guard-'+uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.core = self.root/'kernel-core'
        (self.root/'isolation.json').write_text(json.dumps({'runtime_root':str(self.root.resolve()),
            'core_dir':str(self.core.resolve()), 'provider_profile_only':True}), encoding='utf-8')
        self.r = patch.object(v,'R',self.root); self.r.start(); self.addCleanup(self.r.stop)
        self.c = patch.object(v,'CORE',self.core); self.c.start(); self.addCleanup(self.c.stop)

    def test_owned_run_accepted(self):
        v.check_test_isolation()

    def test_legacy_root_cannot_launch(self):
        with patch.object(v,'R',WORK/'stage1/runtime'), patch.object(v.subprocess,'Popen') as launch:
            with self.assertRaises(RuntimeError): v.start('must-not-start',reuse=True,revision='v2-')
            launch.assert_not_called()

    def test_external_core_cannot_launch(self):
        with patch.object(v,'CORE',WORK/'phase1/runtime/kernel-core'), patch.object(v.subprocess,'Popen') as launch:
            with self.assertRaises(RuntimeError): v.start('must-not-start')
            launch.assert_not_called()

    def test_missing_marker_cannot_launch(self):
        child=self.root/'uninitialized';child.mkdir()
        with patch.object(v,'R',child),patch.object(v,'CORE',child/'kernel-core'),patch.object(v.subprocess,'Popen') as launch:
            with self.assertRaises(FileNotFoundError): v.start('must-not-start')
            launch.assert_not_called()

    def test_traversal_cannot_launch(self):
        with patch.object(v.subprocess,'Popen') as launch:
            with self.assertRaises(RuntimeError): v.start('must-not-start',revision='../../../../outside-')
            launch.assert_not_called()

    def test_occupied_control_port_cannot_launch(self):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as occupied:
            occupied.bind(('127.0.0.1',0));occupied.listen()
            with patch.object(v,'PORT',occupied.getsockname()[1]),patch.object(v.subprocess,'Popen') as launch:
                with self.assertRaisesRegex(RuntimeError,'occupied'): v.start('must-not-start')
                launch.assert_not_called()

    def control_failure(self, response=None):
        evidence=self.root/'evidence';evidence.mkdir()
        (evidence/'mirror-receipt.json').write_text(json.dumps({'mirror':str(self.root/'mirror'),'anchor_public_hex':'test-fixture'}),encoding='utf-8')
        with patch.object(v,'E',evidence),patch.object(v,'check_remote_available'),patch.object(v,'sha',return_value='FIXTURE'),patch.object(v,'save'),patch.object(v.time,'sleep'),patch.object(v.subprocess,'Popen') as launch,patch.object(v,'request') as request:
            process=launch.return_value;process.pid=12345;process.poll.return_value=None
            if response is None:request.side_effect=OSError('fixture unavailable API')
            else:request.return_value=response
            with self.assertRaisesRegex(RuntimeError,'another PID' if response else 'not ready'):v.start('fixture-control-failure')
            process.terminate.assert_called_once()

    def test_mismatched_pid_stops_only_spawned_host(self):
        self.control_failure(b'{"pid":99999}')

    def test_missing_control_api_never_claims_ready(self):
        self.control_failure()

if __name__ == '__main__': unittest.main()
