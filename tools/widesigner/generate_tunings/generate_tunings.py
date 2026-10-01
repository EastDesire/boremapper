#!/usr/bin/env python3
from math import floor
from pathlib import Path


out_dir = './tunings'

# A4 pitches to generate
concert_pitches = [440, 432, 442, 443, 415]

# Note range to generate - number of semitones relative to concert pitch
note_range = [-48, 48]

note_namings = {
    'default': ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'],
}

# Based on NAF tunings by Edward Kort
tunings = {
    '6-hole_NAF_chromatic_tuning_ET': {
        'name': '6-hole NAF chromatic tuning, equal temperament, A={freq}',
        'note_naming': 'default',
        'fingerings': [
            # <interval from root>, <open holes>, <name>
            (0, (False, False, False, False, False, False), '{note}'),
            (3, (False, False, False, False, False, True), '{note}'),
            (4, (False, False, False, False, True, False), '{note}'),
            (5, (False, False, False, False, True, True), '{note}'),
            (6, (False, False, False, True, False, True), '{note}'),
            (7, (False, False, False, True, True, True), '{note}'),
            (8, (False, False, True, False, True, True), '{note}'),
            (9, (False, False, True, True, True, True), '{note}'),
            (10, (False, True, False, True, True, True), '{note}'),
            (11, (False, True, True, True, True, True), '{note}'),
            (12, (True, True, False, True, True, True), '{note}'),
            (13, (True, True, True, True, True, True), '{note} (open)'),
            (13, (False, True, False, False, False, False), '{note} (closed)'),
            (14, (True, True, False, False, False, False), '{note}'),
            (15, (True, True, False, False, False, True), '{note}'),
        ],
        'weightings': {
            'unweighted': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            'weighted': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0],
        },
    },
}


def note_full_name(interval: int, naming: str) -> str:
    """
    :param interval: Number of semitones relative to A4
    :param naming: Note naming variant
    """
    octave = floor((interval + 9) / 12) + 4
    return note_namings[naming][interval % 12] + str(octave)


def note_12tet_frequency(f0: float, interval: int) -> float:
    """
    Calculates a frequency of given note using the 12-tone equal temperament tuning system.
    See https://music.stackexchange.com/questions/135572/
    :param f0: Frequency (Hz) of a reference note (usually A4)
    :param interval: Number of semitones relative to the reference note
    :return: Note frequency in Hz
    """
    return f0 * pow(2, interval / 12)


def generate_tuning_data(root_interval: int, a4: int, tuning: dict, weighting: str):
    fingerings_data = []
    
    for index, fingering in enumerate(tuning['fingerings']):
        interval_in_fingering, holes_state, note_name_format = fingering
        interval = root_interval + interval_in_fingering
        note_name = note_name_format.format(note=note_full_name(interval, tuning['note_naming']))
        note_freq = note_12tet_frequency(a4, interval)
        weight = tuning['weightings'][weighting][index]
        
        fingerings_data.extend([
            '    <fingering>',
            '        <note>',
            '            <name>' + note_name + '</name>',
            '            <frequency>' + str(note_freq) + '</frequency>',
            '        </note>',
            *(['        <openHole>' + ('true' if is_open else 'false') + '</openHole>' for is_open in holes_state]),
            '        <optimizationWeight>' + str(weight) + '</optimizationWeight>',
            '    </fingering>',
        ])
        
    interval_in_fingering, holes_state, note_name_format = tuning['fingerings'][0]
    number_of_holes = len(holes_state)
    
    format_params = {
        'freq': a4,
    }
    tuning_name = tuning['name'].format(**format_params)
    tuning_comment = tuning['name'].format(**format_params)

    out = '\n'.join([
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<ns2:tuning xmlns:ns2="http://www.wwidesigner.com/Tuning">',
        '    <name>' + tuning_name + '</name>',
        '    <comment>' + tuning_comment + '</comment>',
        '    <numberOfHoles>' + str(number_of_holes) + '</numberOfHoles>',
        *fingerings_data,
        '</ns2:tuning>',
    ])
    return out


def generate_files():
    Path(out_dir).mkdir(exist_ok=True)

    for tuning_name, tuning in tunings.items():
        tuning_dir = out_dir + '/' + tuning_name + '/'
        Path(tuning_dir).mkdir(exist_ok=True)
        
        for pitch in concert_pitches:
            pitch_dir = tuning_dir + '/' + ('A%d' % pitch)
            Path(pitch_dir).mkdir(exist_ok=True)

            for weighting_name in tuning['weightings'].keys():
                weighting_dir = pitch_dir + '/' + weighting_name
                Path(weighting_dir).mkdir(exist_ok=True)

                for interval in range(note_range[0], note_range[1] + 1):
                    root_note_name = note_full_name(interval, tuning['note_naming'])
                    data = generate_tuning_data(interval, pitch, tuning, weighting_name)
                    file = weighting_dir + '/' + ('%s_%s_A%d_%s.xml' % (root_note_name, tuning_name, pitch, weighting_name))

                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(data)


def main():
    generate_files()

if __name__ == '__main__':
    main()