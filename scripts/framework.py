import argparse
import http.server
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from framework.engine import Workflow
from framework.portal import make_handler


def main():
    parser = argparse.ArgumentParser(description='Framework local de estimación')
    parser.add_argument('--project', default='piloto')
    commands = parser.add_subparsers(dest='command', required=True)
    cmd = commands.add_parser('init'); cmd.add_argument('id')
    cmd = commands.add_parser('start'); cmd.add_argument('step', nargs='?')
    cmd = commands.add_parser('finish'); cmd.add_argument('step')
    cmd.add_argument('--context-complete', action='store_true'); cmd.add_argument('--evidence')
    cmd = commands.add_parser('approve'); cmd.add_argument('step'); cmd.add_argument('--by', required=True)
    cmd = commands.add_parser('approve-rules'); cmd.add_argument('--by', required=True)
    cmd = commands.add_parser('block'); cmd.add_argument('step'); cmd.add_argument('--reason', required=True)
    cmd = commands.add_parser('retry'); cmd.add_argument('step')
    cmd = commands.add_parser('complement'); cmd.add_argument('--reason', required=True)
    cmd = commands.add_parser('adjust'); cmd.add_argument('--reason', required=True)
    commands.add_parser('status'); commands.add_parser('board'); commands.add_parser('validate-rules')
    cmd = commands.add_parser('serve'); cmd.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    try:
        flow = Workflow(ROOT, args.id if args.command == 'init' else args.project)
        if args.command == 'init': flow.init()
        elif args.command == 'start': print(flow.start(args.step))
        elif args.command == 'finish': flow.finish(args.step, args.context_complete, args.evidence)
        elif args.command == 'approve': flow.approve(args.step, args.by)
        elif args.command == 'approve-rules': flow.approve_rules(args.by)
        elif args.command == 'block': flow.block(args.step, args.reason)
        elif args.command == 'retry': flow.retry(args.step)
        elif args.command == 'complement': print(flow.complement_a1(args.reason))
        elif args.command == 'adjust': print(flow.adjust_review(args.reason))
        elif args.command == 'validate-rules': flow.validate_rules(); print('Estructura de reglas válida.')
        elif args.command == 'status':
            state = flow.read()
            print(f'Proyecto: {flow.project}')
            for name, item in state['steps'].items(): print(f'{name}: {item["status"]}')
            flow.board(state)
        elif args.command == 'board': print(flow.board())
        elif args.command == 'serve':
            flow.board()
            handler = make_handler(ROOT)
            with http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
                print(f'Tablero: http://127.0.0.1:{args.port}', flush=True)
                try: server.serve_forever()
                except KeyboardInterrupt: pass
        return 0
    except (ValueError, OSError) as error:
        print(f'No se ejecutó la operación: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
