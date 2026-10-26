#!/usr/bin/env python3
"""Offline tests; no DNS, provider calls or certificate issuance."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('renderer', ROOT / 'render-caddy.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RendererTests(unittest.TestCase):
    def test_candidate_has_only_explicit_routes(self):
        result = renderer.render('MCP.EXAMPLE.COM', 18140)
        self.assertIn('mcp.example.com {', result)
        self.assertIn('reverse_proxy 127.0.0.1:18140', result)
        self.assertIn('admin off', result)
        self.assertIn('disable_http_challenge', result)
        self.assertNotIn('__DOMAIN__', result)
        self.assertNotIn('18141', result)

    def test_reject_domain_config_injection_and_url(self):
        for host in ['x.example.com\n{\nfile_server', 'https://mcp.example.com',
                     '*.example.com', '127.0.0.1', 'mcp.example.com:443',
                     'bad..example.com', '-bad.example.com', 'x.internal']:
            with self.subTest(host=host), self.assertRaises(ValueError):
                renderer.render(host, 18140)

    def test_reject_invalid_ports(self):
        for port in [-1, 0, 80, 65536]:
            with self.subTest(port=port), self.assertRaises(ValueError):
                renderer.render('mcp.example.com', port)

    def test_cli_creates_candidate_without_network(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'candidate'
            result = subprocess.run([sys.executable, str(ROOT / 'render-caddy.py'),
                '--domain', 'mcp.example.com', '--backend-port', '18140',
                '--out', str(out)], capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(out.read_text(), renderer.render('mcp.example.com', 18140))

    def test_existing_file_and_symlink_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            original = Path(td) / 'original'
            original.write_text('preserve')
            link = Path(td) / 'candidate'
            link.symlink_to(original)
            for output in [original, link]:
                result = subprocess.run([sys.executable, str(ROOT / 'render-caddy.py'),
                    '--domain', 'mcp.example.com', '--backend-port', '18140',
                    '--out', str(output)], capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(original.read_text(), 'preserve')
            self.assertTrue(link.is_symlink())

    def test_install_and_reinstall_protection(self):
        with tempfile.TemporaryDirectory(prefix='skill test ') as td:
            env = {**os.environ, 'HOME': td}
            result = subprocess.run(['sh', str(ROOT / 'install.sh')], env=env,
                                    capture_output=True)
            self.assertEqual(result.returncode, 0)
            target = Path(td) / '.agents/skills/z-mcp-domain-deploy'
            for name in ['SKILL.md', 'domain-and-icp.md', 'https-and-mcp.md',
                         'sources.md', 'Caddyfile.template', 'render-caddy.py', 'LICENSE']:
                self.assertEqual((target / name).read_bytes(), (ROOT / name).read_bytes())
            result = subprocess.run(['sh', str(ROOT / 'install.sh')], env=env,
                                    capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_install_refuses_dangling_link(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td) / '.agents/skills'
            parent.mkdir(parents=True)
            target = parent / 'z-mcp-domain-deploy'
            target.symlink_to(Path(td) / 'missing')
            result = subprocess.run(['sh', str(ROOT / 'install.sh')],
                env={**os.environ, 'HOME': td}, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())


if __name__ == '__main__':
    unittest.main()
