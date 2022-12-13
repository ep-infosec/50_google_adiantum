# Copyright 2018 Google LLC
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import re

import paths
import parsetv

class ParseSalsa20(parsetv.ParseTv):
    def _finish_tvkv(self):
        if self._tvvalue:
            m = re.fullmatch(r"stream\[(\d+)\.\.(\d+)\]", self._tvkey)
            if m:
                self._tvstreamlist.append({
                    "first": int(m.group(1)),
                    "last": int(m.group(2)),
                    "value": self._tvvalue,
                })
            else:
                self._tvdict[self._tvkey] = self._tvvalue
        self._tvkey = None
        self._tvvalue = None

    def _handle_line(self, l):
        l = l.strip()
        if len(l) == 0:
            self._finish_tv()
        elif l[0] in "*=(":
            self._finish_tv()
        elif l.startswith("Test vectors -- set"):
            self._start_tvset({
                "setintro": l,
            })
        elif l.startswith("End of test vectors"):
            self._finish_setlist()
        elif l[-1] == ":":
            self._start_tv({
                "intro": l[:-1],
            })
        elif ":" in l:
            k, v = l.split(":", 1)
            self._globalparams[k.strip()] = v.strip()
        elif "=" in l:
            vkey, vval = l.split("=", 1)
            self._start_tvkv(vkey.strip())
            self._vappend(vval.strip())
        elif re.fullmatch(r"[0-9A-F]+", l):
            self._vappend(l)
        else:
            raise Exception("Can't parse: " + repr(l))

def test_vectors():
    p = ParseSalsa20()
    p.parse_file(paths.top / "test_vectors" / "other" / "salsa20.txt")
    return p.get()
