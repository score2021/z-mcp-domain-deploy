#!/usr/bin/env python3
"""Offline single-site candidate renderer; never installs, starts or contacts a host."""
import argparse
import ipaddress
from pathlib import Path
import re


def hostname(value):
    value = value.strip().lower()
    if len(value) > 253 or '.' not in value or not re.fullmatch(r'[a-z0-9.-]+', value):
        raise ValueError('Use an ASCII DNS name without URL, wildcard, port or spaces')
    labels = value.split('.')
    if any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', x) for x in labels):
        raise ValueError('Invalid DNS label')
    try:
        ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        raise ValueError('Use a DNS hostname, not an IP literal')
    if value.endswith(('.localhost', '.local', '.internal', '.invalid', '.test')):
        raise ValueError('Use a public DNS name; reserved private/test suffix is not supported')
    return value


def render(domain, port):
    domain = hostname(domain)
    if not 1024 <= port <= 65535:
        raise ValueError('Backend port must be between 1024 and 65535')
    text = Path(__file__).with_name('Caddyfile.template').read_text()
    return text.replace('__DOMAIN__', domain).replace('__PORT__', str(port))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--domain', required=True)
    parser.add_argument('--backend-port', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        text = render(args.domain, args.backend_port)
        # x rejects existing files and symlinks, including dangling ones.
        with args.out.open('x') as stream:
            stream.write(text)
    except (ValueError, OSError) as exc:
        parser.exit(2, 'Candidate not written: ' + str(exc) + '\n')
    print('Candidate created; validate it with the target Caddy version. No deployment performed.')


if __name__ == '__main__':
    main()
