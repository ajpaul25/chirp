#!/usr/bin/python

import os
import libxml2

from chirp import chirp_common, errors, xml_ll

def validate_doc(doc):
    ctx = libxml2.schemaNewParserCtxt("chirp.xsd")
    schema = ctx.schemaParse()
    del ctx

    def err(msg, arg=None):
        print "ERROR: %s" % msg

    def wrn(msg, arg=None):
        print "WARNING: %s" % msg

    validCtx = schema.schemaNewValidCtxt()
    validCtx.setValidityErrorHandler(err, wrn)
    err = validCtx.schemaValidateDoc(doc)
    if err:
        print "---DOC---\n%s\n------" % doc.serialize(format=1)
        raise errors.RadioError("Schema error")

#!/usr/bin/python
#
# Copyright 2008 Dan Smith <dsmith@danplanet.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class XMLRadio(chirp_common.IcomFileBackedRadio):
    def __init__(self, pipe):
        chirp_common.IcomFileBackedRadio.__init__(self, None)
        self._filename = pipe
        if self._filename and os.path.exists(self._filename):
            self.doc = libxml2.parseFile(self._filename)
            validate_doc(self.doc)
        else:
            self.doc = libxml2.newDoc("1.0")
            self.doc.newChild(None, "radio", None)

    def load(self, filename=None):
        if not self._filename and not filename:
            raise errors.RadioError("Need a location to load from")

        if filename:
            self._filename = filename

        self.doc = libxml2.parseFile(self._filename)
        validate_doc(self.doc)

    def save(self, filename=None):
        if not self._filename and not filename:
            raise errors.RadioError("Need a location to save to")

        if filename:
            self._filename = filename

        f = file(self._filename, "w")
        f.write(self.doc.serialize(format=1))
        f.close()

    def get_memories(self, lo=0, hi=999):
        mems = []
        for i in range(lo, hi):
            try:
                mems.append(xml_ll.get_memory(self.doc, i))
            except errors.InvalidMemoryLocation:
                pass

        return mems
    
    def get_memory(self, number):
        mem = xml_ll.get_memory(self.doc, number)

        return mem

    def set_memory(self, mem):
        xml_ll.set_memory(self.doc, mem)
        validate_doc(self.doc)

    def erase_memory(self, number):
        xml_ll.del_memory(self.doc, number)
        validate_doc(self.doc)

if __name__ == "__main__":
    r = XMLRadio("testmem.chirp")

    print r.get_memory(3)

    m = chirp_common.Memory()
    m.name = "TestMem2"
    m.freq = 123.456
    m.number = 10

    #r.set_memory(m)
    #r.erase_memory(10)
