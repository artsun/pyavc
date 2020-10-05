#!/usr/bin/python3
# -*- coding: utf-8 -*-


import re
from argparse import ArgumentParser, SUPPRESS


class ParseAVC:
    _permission = re.compile("(?<=\{\s)\w+(?=\s\})")
    _tclass = re.compile('(?<=tclass\=).*?(?=\s)')
    _scontext = re.compile('(?<=scontext\=).*?(?=\s)')
    _tcontext = re.compile('(?<=tcontext\=).*?(?=\s)')
    _context = re.compile('(?<=_r:).*?(?=:s0)')
    _skeys = {'permission': _permission, 'tclass': _tclass, 'scontext': _scontext, 'tcontext': _tcontext}

    def __init__(self, data):
        self.require: str
        self.body: str
        self.tree = {}
        self._lines = data.split('\n')
        self._grow_tree()

    def _grow_tree(self):
        for num, line in enumerate(self._lines):
            self._catch(num, line)

    def _catch(self, num: int, line: str):
        temp = {}
        for key, val in self._skeys.items():
            res = val.search(line)
            if res is None:
                print(f'pattern <{key}> not found in the string (line {num}) {line} - SKIP')
                return
            temp.update({key: res.group()})
        for el in ('scontext', 'tcontext'):
            temp[el] = self._context.search(temp[el])
            if temp[el] is None:
                print(f'pattern <{el}> not found in the string (line {num}) {line} - SKIP')
                return
            temp[el] = temp[el].group()

        scon = self.tree.get(temp['scontext'])
        if scon is None:
            scon = {}
            self.tree.update({temp['scontext']: scon})

        tcon = scon.get(temp['tcontext'])
        if tcon is None:
            tcon = {}
            scon.update({temp['tcontext']: tcon})

        allows = tcon.get(temp['tclass'])
        if allows is None:
            allows = set()
            tcon.update({temp['tclass']: allows})
        allows.add(temp['permission'])

    def policy(self):
        allows = set()
        types = set()
        classes = set()
        for scon, two in self.tree.items():
            types.add(f'type {scon};')
            for tcon, three in two.items():
                types.add(f'type {tcon};')
                for cl, perms in three.items():
                    perms = ' '.join([p for p in perms])
                    classes.add(f'class {cl} {{{perms}}};')
                    allows.add(f'allow {scon} {tcon}: {cl} {{{perms}}};')
        types = '\n'.join([x for x in sorted(types, key=len)])
        classes = '\n'.join([x for x in classes])

        self.require = f"require {{\n{types}\n\n{classes}\n}}\n"
        self.body = '\n'.join([x for x in allows])

    def __repr__(self):
        res = ''
        for scon, two in self.tree.items():
            res = (f'{res}{scon}\n')
            for tcon, three in two.items():
                res = f'{res}\t-> {tcon}\n'
                for cl, perms in three.items():
                    perms = ' '.join([p for p in perms])
                    res = f'{res}\t\t\t-> {cl} {{{perms}}}\n'
        return res


if __name__ == '__main__':
    parser = ArgumentParser(description='AVC Parser', usage=SUPPRESS, add_help=False, allow_abbrev=False)
    gr = parser.add_mutually_exclusive_group()
    gr.add_argument("-h", action="help", help='Ich brauche Hilfe!')
    gr.add_argument('-f', dest='file', nargs='?', type=str, help='path to file with AVC', metavar='')

    extra = parser.add_argument_group()
    extra.add_argument('-te', dest='polfile', nargs='?', type=str, help='to policy file (name)', metavar='')
    extra.add_argument('-v', dest='verbose', action='store_true', help='show tree as json')

    args = parser.parse_args()

    if args.file:
        with open(args.file) as fl:
            avc = ParseAVC(fl.read())
            avc.policy()
    else:
        raise SystemExit('no path to AVC file, use -h')

    if args.verbose:
        print(avc)
    if args.polfile:
        with open(f'{args.polfile}.te', 'w') as fl:
            fl.write(f'policy_module({args.polfile}, 1.0.0)\n{avc.require}\n{avc.body}')
    else:
        print(avc.require)
        print(avc.body)
