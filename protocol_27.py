#!/usr/local/bin/python
# coding: utf-8

import codecs
import array

protocol_msg_default = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
protocol_msg_test = b'\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01'

sb_shift = 16
teststand_typ = b'\xff'
tt_shift = 120
teststand_uniqueID = b'\x00'
tu_shift = 112
teststand_prio = b'\x00'
tp_shift = 104
datalength = b'\x00\x00'
dl_shift = 0

gesamtMsgBytes = 16

# statusdefaultwert
status_default = b'\x00' * 11

# Allgemeine Status 2 byte
allgemeine_status_shift = 88
_1_allgemein_default = b'\x00\x00'
_1_testsystemfehler = b'\x00\x01'
_1_roboterfehler = b'\x00\x02'
_1_verbindungsabbruch = b'\x00\x04'
_1_verbindungsfehler = b'\x00\x08'
_1_testprogrammLOAD = b'\x00\x10'

# Testsystem Status 6 byte
testsystem_status_shift = 40
_2_testsystem_default = b'\x00\x00\x00\x00\x00\x00'
_2_testsystem_start = b'\x10\x00\x00\x00\x00\x00'
_2_dut_eingelegt = b'\x00\x00\x00\x00\x00\x01'
_2_barcode_benoetigt = b'\x00\x00\x00\x00\x00\x02'
_2_barcode_valide = b'\x00\x00\x00\x00\x00\x04'
_2_deckel_zu = b'\x00\x00\x00\x00\x00\x08'
_2_test_fertig = b'\x00\x00\x00\x00\x00\x10'
_2_testprogramm_bug = b'\x00\x00\x00\x00\x00\x20'
_2_test_gut = b'\x00\x00\x00\x00\x00\x40'
_2_test_schlecht = b'\x00\x00\x00\x00\x00\x80'
# test = b'\xdd\xff\xff\x00\xff\x22'

# Reserve 3 Byte
reserve_shift = 16
_3_reserve_default = b'\x00\x00\x00'
_3_reserve_bit_01 = b'\x00\x00\x01'
_3_reserve_bit_02 = b'\x00\x00\x02'
_3_reserve_bit_03 = b'\x00\x00\x04'
_3_reserve_bit_04 = b'\x00\x00\x08'
_3_reserve_bit_05 = b'\x00\x00\x10'
_3_reserve_bit_06 = b'\x00\x00\x20'
_3_reserve_bit_07 = b'\x00\x00\x40'
_3_reserve_bit_08 = b'\x00\x00\x80'


# -----------------------------------------------------------------------
def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(codecs.encode(b,'hex'), 16)
    return result

def int_to_bytes(value, length):
    result = []
    for i in range(0, length):
        result.append(value>>(i*8)& 0xff)
    result.reverse()
    res = array.array('B', result).tostring()
    return res

class Protocol(object):
    def __init__(self, teststand_typ=teststand_typ, teststand_uniqueID=teststand_uniqueID
                 , teststand_prio=teststand_prio, datalength=datalength):
        """
		Constructor, if nothing else is specified, creates a default protocol
        :param teststand_typ: which kind of test stand, later important to define refpoints at the measuring station for the
        robot.

        :param teststand_uniqueID: given from server
        :param teststand_prio: testsystem/program prio
        :param datalength: length in [Bytes]
        """
        protocol_msg = bytes_to_int(teststand_typ) << tt_shift \
                       | bytes_to_int(teststand_uniqueID) << tu_shift \
                       | bytes_to_int(teststand_prio) << tp_shift \
                       | bytes_to_int(status_default) << sb_shift \
                       | bytes_to_int(datalength) << dl_shift
        self.protocol_msg = int_to_bytes(protocol_msg, 16)

    def setProtocol(self, whole_protocol):
        """
        Resets the protocol, checks the length and type (bytes), both will be the protocol_msg
        set again 
        :param whole_protocol: protocol which should be the new one
        :return:
        """
        if len(whole_protocol)==16 and isinstance(whole_protocol, bytes):
            self.protocol_msg = whole_protocol
        else:
            print("wrong len or type")


    def build_Statusabbild(self, allgemein_status=_1_allgemein_default, testsystem_status=_2_testsystem_default,
                           reserve=_3_reserve_default):
        """       
		Composes the overall status image and writes it to the status_bytes array
        :param allgemein_status:
        :param testsystem_status:
        :param reserve:
        :return:
        """
        self.protocol_msg = bytes_to_int(reserve) << reserve_shift \
                            | bytes_to_int(testsystem_status) << testsystem_status_shift \
                            | bytes_to_int(allgemein_status) << allgemeine_status_shift
        self.protocol_msg = int_to_bytes(self.protocol_msg, 16)

    def set_ID(self, id, data=0):
        """
		sets the uniqueID in the byte [0]
        Integrate the uniqueID queried by the server into the overall image
        :type data:
        :param system_id:
        :return:
        """

        reset = b'\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'

        if len(self.protocol_msg) == 16:
            protocol_msg = bytes_to_int(reset) & bytes_to_int(self.protocol_msg)
            if isinstance(id, int):
                id = int_to_bytes(id, 1)
            protocol_msg = protocol_msg | bytes_to_int(id) << tu_shift
            self.protocol_msg = int_to_bytes(protocol_msg,16)
        elif len(data) == 16:
            protocol_msg = bytes_to_int(reset) & bytes_to_int(data)
            if isinstance(id, int):
                id = int_to_bytes(id, 1)
            protocol_msg = protocol_msg | bytes_to_int(id) << tu_shift
            self.protocol_msg = int_to_bytes(protocol_msg,16)

    def set_teststand(self, teststandtype):
        """
		Defintion what kind of test stand it is, according to the coding to prove
        :param teststandtype:
        :return:

        """

        reset = b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'

        # try:

        if len(self.protocol_msg) == 16:
            protocol_msg = bytes_to_int(reset) & bytes_to_int(self.protocol_msg)
            if isinstance(teststandtype, int):
                teststandtype = int_to_bytes(teststandtype, 1)
            protocol_msg = protocol_msg | bytes_to_int(teststandtype) << tt_shift
            self.protocol_msg = int_to_bytes(protocol_msg,16)



    def set_Reserve(self, reserve):

        reset = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\xff\xff'

        # try:

        if len(self.protocol_msg) == 16:
            protocol_msg = bytes_to_int(reset) & bytes_to_int(self.protocol_msg)
            if isinstance(reserve, int):
                reserve = int_to_bytes(reserve, 3)
            protocol_msg = protocol_msg | bytes_to_int(reserve) << reserve_shift
            self.protocol_msg = int_to_bytes(protocol_msg,16)


    def set_datalength(self, datalenght=0):
        """
        :param datalenght:
        :return:
        """
        reset = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00'

        if len(self.protocol_msg) == 16:
            protocol_msg = bytes_to_int(reset) & bytes_to_int(self.protocol_msg)
            if isinstance(datalenght, int):
                datalenght = int_to_bytes(datalenght, 2)

            protocol_msg = protocol_msg | bytes_to_int(datalenght)  # << dl_shift
            self.protocol_msg = int_to_bytes(protocol_msg,16)



    def setStatus(self, state, statetype, settype):
        """
		Sets the status that is transferred or resets the status
        :param state: new state
        :param statetype: Allgemein[1] Testsystem[2] Reserve[3]
        :param settype: 'set' to set the status, 'reset' to reset the status
        :return: protocol_msg
        """

        reset_a = b'\xff\xff\xff\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        reset_t = b'\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff'

        if isinstance(state, int):
            state = int_to_bytes(state, 3)

        if settype == 'set':
            state = bytes_to_int(state)

            if statetype == 1:
                protocol_msg = bytes_to_int(reset_a) & bytes_to_int(self.protocol_msg)
                protocol_msg = protocol_msg | (state << allgemeine_status_shift)
                self.protocol_msg = int_to_bytes(protocol_msg,16)

            elif statetype == 2:
                protocol_msg = bytes_to_int(reset_t) & bytes_to_int(self.protocol_msg)
                protocol_msg = protocol_msg | (state << testsystem_status_shift)
                self.protocol_msg = int_to_bytes(protocol_msg, 16)
            else:
                print("nope")

        elif settype == 'reset':
            state = ~bytes_to_int(state)

            if statetype == 1:
                self.protocol_msg = bytes_to_int(self.protocol_msg) & (state << allgemeine_status_shift)
                self.protocol_msg = int_to_bytes(self.protocol_msg, 16)
            elif statetype == 2:
                self.protocol_msg = bytes_to_int(self.protocol_msg) & (state << testsystem_status_shift)
                self.protocol_msg = int_to_bytes(self.protocol_msg, 16)
            else:
                print("nope")

        else:
            print("Big function, but didnt work")


    def isStateActive(self, state, statetype):
        """
        Check if a bit is set from the different states
        :param state: state to check
        :param statetype: Statefamily
        :return: returns a int value if bit is set, if not 0
        """
        state = bytes_to_int(state)
        if statetype == 1:
            temp = bytes_to_int(self.protocol_msg) & (state << allgemeine_status_shift)
            return temp
        elif statetype == 2:
            temp = bytes_to_int(self.protocol_msg) & (state << testsystem_status_shift)
            return temp
        elif statetype == 3:
            temp = bytes_to_int(self.protocol_msg) & (state << reserve_shift)
            return temp
        else:
            print("nope")


    def reset(self):
        self.protocol_msg = protocol_msg_default


    def getMyID(self):
        return self.protocol_msg[1]

#ClientG5_ID_02 = Protocol(b'\xaa', b'\x02', b'\x01', b'\xff\xff')
#print bytes_to_int(ClientG5_ID_02.getMyID())
