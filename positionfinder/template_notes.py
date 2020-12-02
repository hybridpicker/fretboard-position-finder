NOTES = [
    'c', 'db', 'd',
    'eb', 'e', 'f',
    'gb', 'g', 'ab',
    'a', 'bb', 'b'
    ]
# adding sharp notes
NOTES_SHARP = [
    'c', 'cs', 'd',
    'ds', 'e', 'f',
    'fs', 'g', 'gs',
    'a', 'as', 'b'
    ]
# Defines Range of OCTAVES
OCTAVES = [
    -1, 0, 1,
    2, 3, 4
    ]
# Defines Range of Sharp Notes
SHARP_NOTES = [
    7, 2, 9,
    4, 11, 19,
    14, 21, 16,
    23
    ]

ALL_NOTES_POSITION = [
    1, 2, 3, 4,
    5, 6, 7, 8,
    9, 10, 11, 12,
    13, 14, 15, 16, 17
    ]

TENSIONS = [
    'R', 'b9', '9',
    'b3', '3', '11',
    '#11', '5', 'b13',
    '13', 'b7', '7'
    ]

TENSIONS_OPTIONAL = [
    'R', 'b9', 'bb3',
    'b3', 'b11', '11',
    'b5', '5', 'b13',
    'bb7', 'b7', '7'
    ]

NOTE_NAMES = [
    'C', 'Db', 'D',
    'Eb', 'E', 'F',
    'Gb', 'G', 'Ab',
    'A', 'Bb', 'B'
    ]

NOTE_NAMES_OPTION = [
    'Dbb', 'Db', 'Ebb',
    'Eb', 'Fb', 'Gbb',
    'Gb', 'Abb', 'Ab',
    'Bbb', 'Bb', 'Cb'
    ]

''' adding sharp notes '''
NOTE_NAMES_SHARP = [
    'C', 'C#', 'D',
    'D#', 'E', 'F',
    'F#', 'G', 'G#',
    'A', 'A#', 'B'
    ]

NOTE_NAMES_SHARP_OPTION = [
    'B#', 'C#', 'C##',
    'D#', 'D##', 'E#',
    'F#', 'F##', 'G#',
    'G##', 'A#', 'A##'
    ]

INVERSIONS = [
     'Basic Position',
     'First Inversion',
     'Second Inversion',
     'Third Inversion',
     'Fourth Inversion',
     'Fifth Inversion',
     'Sixth Inversion',
     ]

STRING_NOTE_OPTIONS =  {
 	"eString": [{
 		"c": [{
 			"tone": ["c3"],
 			"fret": [8]
 		}],
 		"cs": [{
 			"tone": ["cs3"],
 			"fret": [9]
 		}],
 		"db": [{
 			"tone": ["db3"],
 			"fret": [9]
 		}],
 		"d": [{
 			"tone": ["d3"],
 			"fret": [10]
 		}],
 		"ds": [{
 			"tone": ["ds3"],
 			"fret": [11]
 		}],
 		"eb": [{
 			"tone": ["eb3"],
 			"fret": [11]
 		}],
 		"e": [{
 			"tone": ["e3"],
 			"fret": [12]
 		}],
 		"f": [{
 			"tone": ["f2", "f3"],
 			"fret": [1, 13]
 		}],
 		"fs": [{
 			"tone": ["fs2",
 				"fs3"
 			],
 			"fret": [2,
 				14
 			]
 		}],
 		"gb": [{
 			"tone": ["gb2",
 				"gb3"
 			],
 			"fret": [2,
 				14
 			]
 		}],
 		"g": [{
 			"tone": ["g2",
 				"g3"
 			],
 			"fret": [3,
 				15
 			]
 		}],
 		"gs": [{
 			"tone": ["gs2",
 				"gs3"
 			],
 			"fret": [4,
 				16
 			]
 		}],
 		"ab": [{
 			"tone": ["ab2",
 				"ab3"
 			],
 			"fret": [4,
 				16
 			]
 		}],
 		"a": [{
 			"tone": ["a2",
 				"a3"
 			],
 			"fret": [5,
 				17
 			]
 		}],
 		"as": [{
 			"tone": ["as2"],
 			"fret": [6]
 		}],
 		"bb": [{
 			"tone": ["bb2"],
 			"fret": [6]
 		}],
 		"b": [{
 			"tone": ["b2"],
 			"fret": [7]
 		}]
 	}],
 	"bString": [{
 		"c": [{
 			"tone": ["c2", "c3"],
 			"fret": [1, 13]
 		}],
 		"cs": [{
 			"tone": ["cs2", "cs3"],
 			"fret": [2, 14]
 		}],
 		"db": [{
 			"tone": ["db2", "db3"],
 			"fret": [2, 14]
 		}],
 		"d": [{
 			"tone": ["d2", "d3"],
 			"fret": [3, 15]
 		}],
 		"ds": [{
 			"tone": ["ds2", "ds3"],
 			"fret": [4, 16]
 		}],
 		"eb": [{
 			"tone": ["eb2", "eb3"],
 			"fret": [4, 16]
 		}],
 		"e": [{
 			"tone": ["e2", "e3"],
 			"fret": [5, 17]
 		}],
 		"f": [{
 			"tone": ["f2"],
 			"fret": [6]
 		}],
 		"fs": [{
 			"tone": ["fs2"],
 			"fret": [7]
 		}],
 		"gb": [{
 			"tone": ["gb2"],
 			"fret": [7]
 		}],
 		"g": [{
 			"tone": ["g2"],
 			"fret": [8]
 		}],
 		"gs": [{
 			"tone": ["gs2"],
 			"fret": [9]
 		}],
 		"ab": [{
 			"tone": ["ab2"],
 			"fret": [9]
 		}],
 		"a": [{
 			"tone": ["a2"],
 			"fret": [10]
 		}],
 		"as": [{
 			"tone": ["as2"],
 			"fret": [11]
 		}],
 		"bb": [{
 			"tone": ["bb2"],
 			"fret": [11]
 		}],
 		"b": [{
 			"tone": ["b2"],
 			"fret": [12]
 		}]
 	}],
 	"gString": [{
 		"c": [{
 			"tone": ["c2", "c3"],
 			"fret": [5, 17]
 		}],
 		"cs": [{
 			"tone": ["cs2"],
 			"fret": [6]
 		}],
 		"db": [{
 			"tone": ["db2"],
 			"fret": [6]
 		}],
 		"d": [{
 			"tone": ["d2"],
 			"fret": [7]
 		}],
 		"ds": [{
 			"tone": ["ds2"],
 			"fret": [8]
 		}],
 		"eb": [{
 			"tone": ["eb2"],
 			"fret": [8]
 		}],
 		"e": [{
 			"tone": ["e2"],
 			"fret": [9]
 		}],
 		"f": [{
 			"tone": ["f2"],
 			"fret": [10]
 		}],
 		"fs": [{
 			"tone": ["fs2"],
 			"fret": [11]
 		}],
 		"gb": [{
 			"tone": ["gb2"],
 			"fret": [11]
 		}],
 		"g": [{
 			"tone": ["g2"],
 			"fret": [12]
 		}],
 		"gs": [{
 			"tone": ["gs1", "gs2"],
 			"fret": [1, 13]
 		}],
 		"ab": [{
 			"tone": ["ab1", "ab2"],
 			"fret": [1, 13]
 		}],
 		"a": [{
 			"tone": ["a1", "a2"],
 			"fret": [2, 14]
 		}],
 		"as": [{
 			"tone": ["as1", "as2"],
 			"fret": [3, 15]
 		}],
 		"bb": [{
 			"tone": ["bb1", "bb2"],
 			"fret": [3, 15]
 		}],
 		"b": [{
 			"tone": ["b1", "b2"],
 			"fret": [4, 16]
 		}]
 	}],
 	"dString": [{
 		"c": [{
 			"tone": ["c2"],
 			"fret": [10]
 		}],
 		"cs": [{
 			"tone": ["cs2"],
 			"fret": [11]
 		}],
 		"db": [{
 			"tone": ["db2"],
 			"fret": [11]
 		}],
 		"d": [{
 			"tone": ["d2"],
 			"fret": [12]
 		}],
 		"ds": [{
 			"tone": ["ds1", "ds2"],
 			"fret": [1, 13]
 		}],
 		"eb": [{
 			"tone": ["eb1", "eb2"],
 			"fret": [1, 13]
 		}],
 		"e": [{
 			"tone": ["e1", "e2"],
 			"fret": [2, 14]
 		}],
 		"f": [{
 			"tone": ["f1", "f2"],
 			"fret": [3, 15]
 		}],
 		"fs": [{
 			"tone": ["fs1", "fs2"],
 			"fret": [4, 16]
 		}],
 		"gb": [{
 			"tone": ["gb1", "gb2"],
 			"fret": [4, 16]
 		}],
 		"g": [{
 			"tone": ["g1", "g2"],
 			"fret": [5, 17]
 		}],
 		"gs": [{
 			"tone": ["gs1"],
 			"fret": [6]
 		}],
 		"ab": [{
 			"tone": ["ab1"],
 			"fret": [6]
 		}],
 		"a": [{
 			"tone": ["a1"],
 			"fret": [7]
 		}],
 		"as": [{
 			"tone": ["as1"],
 			"fret": [8]
 		}],
 		"bb": [{
 			"tone": ["bb1"],
 			"fret": [8]
 		}],
 		"b": [{
 			"tone": ["b1"],
 			"fret": [9]
 		}]
 	}],
 	"AString": [{
 		"c": [{
 			"tone": ["c1", "c2"],
 			"fret": [3, 15]
 		}],
 		"cs": [{
 			"tone": ["cs1", "cs2"],
 			"fret": [4, 16]
 		}],
 		"db": [{
 			"tone": ["db1", "db2"],
 			"fret": [4, 16]
 		}],
 		"d": [{
 			"tone": ["d1", "d2"],
 			"fret": [5, 17]
 		}],
 		"ds": [{
 			"tone": ["ds1"],
 			"fret": [6]
 		}],
        "eb": [{
 			"tone": ["eb1"],
 			"fret": [6]
 		}],
 		"e": [{
 			"tone": ["e1"],
 			"fret": [7]
 		}],
 		"f": [{
 			"tone": ["f1"],
 			"fret": [8]
 		}],
 		"fs": [{
 			"tone": ["fs1"],
 			"fret": [9]
 		}],
 		"gb": [{
 			"tone": ["gb1"],
 			"fret": [9]
 		}],
 		"g": [{
 			"tone": ["g1"],
 			"fret": [10]
 		}],
 		"gs": [{
 			"tone": ["gs1"],
 			"fret": [11]
 		}],
 		"ab": [{
 			"tone": ["ab1"],
 			"fret": [11]
 		}],
 		"a": [{
 			"tone": ["a1"],
 			"fret": [12]
 		}],
 		"as": [{
 			"tone": ["as0", "as1"],
 			"fret": [1, 13]
 		}],
 		"bb": [{
 			"tone": ["bb0", "bb1"],
 			"fret": [1, 13]
 		}],
 		"b": [{
 			"tone": ["b0", "b1"],
 			"fret": [2, 14]
 		}]
 	}],
 	"ELowString": [{
 		"c": [{
 			"tone": ["c1"],
 			"fret": [8]
 		}],
 		"cs": [{
 			"tone": ["cs1"],
 			"fret": [9]
 		}],
 		"db": [{
 			"tone": ["db1"],
 			"fret": [9]
 		}],
 		"d": [{
 			"tone": ["d1"],
 			"fret": [10]
 		}],
 		"ds": [{
 			"tone": ["ds1"],
 			"fret": [11]
 		}],
 		"eb": [{
 			"tone": ["eb1"],
 			"fret": [11]
 		}],
 		"e": [{
 			"tone": ["e1"],
 			"fret": [12]
 		}],
 		"f": [{
 			"tone": ["f0", "f1"],
 			"fret": [1, 13]
 		}],
 		"fs": [{
 			"tone": ["fs0", "fs1"],
 			"fret": [2, 14]
 		}],
 		"gb": [{
 			"tone": ["gb0", "gb1"],
 			"fret": [2, 14]
 		}],
 		"g": [{
 			"tone": ["g0", "g1"],
 			"fret": [3, 15]
 		}],
 		"gs": [{
 			"tone": ["gs0", "gs1"],
 			"fret": [4, 16]
 		}],
 		"ab": [{
 			"tone": ["ab0", "ab1"],
 			"fret": [4, 16]
 		}],
 		"a": [{
 			"tone": ["a0", "a1"],
 			"fret": [5, 17]
 		}],
 		"as": [{
 			"tone": ["as0"],
 			"fret": [6]
 		}],
 		"bb": [{
 			"tone": ["bb0"],
 			"fret": [6]
 		}],
 		"b": [{
 			"tone": ["b0"],
 			"fret": [7]
 		}]
 	}]
 }
