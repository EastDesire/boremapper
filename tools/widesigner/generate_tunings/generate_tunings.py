#!/usr/bin/env python3

from pathlib import Path


out_dir = './tunings'
holes_range = [4, 8]
freq_range = [110, 880] # Hz


def generate_tuning_data(freq: int, holes: int):
    tuning_name = '%d Hz tuning' % (round(freq))
    tuning_comment = '%d Hz tuning with %d holes' % (round(freq), holes)
    note_name = 'root'
    
    out = '\n'.join([
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<ns2:tuning xmlns:ns2="http://www.wwidesigner.com/Tuning">',
        '    <name>' + tuning_name + '</name>',
        '    <comment>' + tuning_comment + '</comment>',
        '    <numberOfHoles>' + str(holes) + '</numberOfHoles>',
        '    <fingering>',
        '        <note>',
        '            <name>' + note_name + '</name>',
        '            <frequency>' + '{:.1f}'.format(freq) + '</frequency>',
        '        </note>',
        *(['        <openHole>false</openHole>'] * holes),
        '        <optimizationWeight>1</optimizationWeight>',
        '    </fingering>',
        '</ns2:tuning>',
    ])
    return out


def generate_files():
    Path(out_dir).mkdir(exist_ok=True)

    for holes in range(holes_range[0], holes_range[1] + 1):
        holes_dir = out_dir + '/' + ('%d-hole' % holes)
        Path(holes_dir).mkdir(exist_ok=True)

        for freq in range(freq_range[0], freq_range[1] + 1):
            data = generate_tuning_data(freq, holes)
            file = holes_dir + '/' + ('%d_Hz_%d-hole_tuning.xml' % (freq, holes))

            with open(file, 'w', encoding='utf-8') as f:
                f.write(data)


def main():
    generate_files()

if __name__ == '__main__':
    main()