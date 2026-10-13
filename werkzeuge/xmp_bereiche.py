#!/usr/bin/env python3
"""Gesichtsrahmen als XMP (MWG Regions) in hochzeit-1924.jpg schreiben (Stand 2026-10-10).

Format laut app4webtrees/tools/markttest/uebergabe-gesichter-sammlungen-2026-10-10.md:
mwg-rs:Regions mit AppliedToDimensions in Pixeln, je Gesicht Type=Face, Name (fehlt bei „unbekannt“),
Area normiert mit x/y = MITTE des Rahmens, bei Personen im Baum sammlungen:Xref; alle Namen zusätzlich in
Iptc4xmpExt:PersonInImage. Es wird nur ein APP1-XMP-Segment eingefügt bzw. ersetzt, alle anderen Segmente bleiben.

    python3 werkzeuge/xmp_bereiche.py <bild.jpg> <gesichter.json> <falkenrath.ged> [<kopie-ohne-rahmen.jpg>]

Die optionale Kopie ist das Bild ohne XMP, zum Testen des Markierens von Hand.
"""
import json
import shutil
import struct
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402

IMG, JSN, GED = sys.argv[1:4]
XMP_ID = b'http://ns.adobe.com/xap/1.0/\x00'


def segments(data):
    """JPEG bis zum SOS in (marker, bytes) zerlegen; Rest roh."""
    assert data[:2] == b'\xff\xd8'
    pos, out = 2, []
    while True:
        marker = data[pos + 1]
        if marker == 0xDA:
            return out, data[pos:]
        length = struct.unpack('>H', data[pos + 2:pos + 4])[0]
        out.append((marker, data[pos:pos + 2 + length]))
        pos += 2 + length


def size(data):
    segs, _ = segments(data)
    for marker, seg in segs:
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', seg[5:9])
            return w, h
    raise ValueError('kein SOF')


data = open(IMG, 'rb').read()
if len(sys.argv) > 4:
    shutil.copyfile(IMG, sys.argv[4])
W, H = size(data)

root = ged.parse(open(GED, encoding='utf-8').read())
names = {r.xref.strip('@'): r.val('NAME').replace('/', '').strip()
         for r in root.children if r.tag == 'INDI'}

items, people = [], []
for b in json.load(open(JSN, encoding='utf-8')):
    name = names[b['id']] if b['id'] else b['name']
    x, y = (b['x'] + b['w'] / 2) / W, (b['y'] + b['h'] / 2) / H
    li = ['        <rdf:li rdf:parseType="Resource">', '          <mwg-rs:Type>Face</mwg-rs:Type>']
    if name:
        li.append(f'          <mwg-rs:Name>{escape(name)}</mwg-rs:Name>')
        people.append(name)
    li.append(f'          <mwg-rs:Area stArea:x="{x:.4f}" stArea:y="{y:.4f}" stArea:w="{b["w"] / W:.4f}" '
              f'stArea:h="{b["h"] / H:.4f}" stArea:unit="normalized"/>')
    if b['id']:
        li.append(f'          <sammlungen:Xref>{b["id"]}</sammlungen:Xref>')
    li.append('        </rdf:li>')
    items.extend(li)

xmp = '\n'.join([
    '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>',
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">',
    ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">',
    '  <rdf:Description rdf:about=""',
    '    xmlns:mwg-rs="http://www.metadataworkinggroup.com/schemas/regions/"',
    '    xmlns:stArea="http://ns.adobe.com/xmp/sType/Area#"',
    '    xmlns:stDim="http://ns.adobe.com/xap/1.0/sType/Dimensions#"',
    '    xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/"',
    '    xmlns:sammlungen="https://github.com/thobgg/webtrees-sammlungen/ns/1.0/">',
    '   <mwg-rs:Regions rdf:parseType="Resource">',
    f'    <mwg-rs:AppliedToDimensions stDim:w="{W}" stDim:h="{H}" stDim:unit="pixel"/>',
    '    <mwg-rs:RegionList>',
    '     <rdf:Bag>',
    *items,
    '     </rdf:Bag>',
    '    </mwg-rs:RegionList>',
    '   </mwg-rs:Regions>',
    '   <Iptc4xmpExt:PersonInImage>',
    '    <rdf:Bag>',
    *[f'     <rdf:li>{escape(p)}</rdf:li>' for p in people],
    '    </rdf:Bag>',
    '   </Iptc4xmpExt:PersonInImage>',
    '  </rdf:Description>',
    ' </rdf:RDF>',
    '</x:xmpmeta>',
    '<?xpacket end="w"?>',
]).encode('utf-8')
payload = XMP_ID + xmp
assert len(payload) + 2 < 65536
app1 = b'\xff\xe1' + struct.pack('>H', len(payload) + 2) + payload

segs, rest = segments(data)
segs = [(m, s) for m, s in segs if not (m == 0xE1 and s[4:4 + len(XMP_ID)] == XMP_ID)]
at = 1 if segs and segs[0][0] == 0xE0 else 0      # hinter JFIF-APP0
segs.insert(at, (0xE1, app1))
open(IMG, 'wb').write(b'\xff\xd8' + b''.join(s for _, s in segs) + rest)
print({'Bild': f'{W}x{H}', 'Bereiche': len(json.load(open(JSN))), 'PersonInImage': len(people)})
