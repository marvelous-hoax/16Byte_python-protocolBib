#!/usr/local/bin/python
# coding: utf-8

protocol_msg_default = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
protocol_msg_test = b'\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01'

sb_shift = 16
tt_shift = 120
tu_shift = 112
tp_shift = 104
dl_shift = 0

gesamtMsgBytes = 16
status_default = b'\x00' * 11

# systemstate, 2 bytes
allgemeine_status_shift = 88
_1_allgemein_default = b'\x00\x00'
_1_testsystemfehler = b'\x00\x01'
_1_roboterfehler = b'\x00\x02'
_1_verbindungsabbruch = b'\x00\x04'
_1_verbindungsfehler = b'\x00\x08'
_1_testprogrammLOAD = b'\x00\x10'
_1_controlonline = b'\x00\x7f'
_1_controloffline = b'\x00\xff'



# teststates, 6 bytes
testsystem_status_shift = 40
_2_testsystem_abort = b'\x00\x00\x00\x00\x00\x1f'
_2_testsystem_nolabel = b'\x00\x00\x00\x00\x00\x2f'
_2_testsystem_init = b'\x00\x00\x00\x00\x00\x7f'
_2_testsystem_ready = b'\x00\x00\x00\x00\x00\xff'

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
_2_test_relocateDUT = b'\x00\x00\x00\x00\x01\x00'

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


class Protocol(object):
    def __init__(self, teststand_typ=b'\x00', teststand_uniqueID=b'\x00'
                 , teststand_prio=b'\x00', datalength=b'\x00\x00'):
        """
		Constructor, if nothing else is specified, creates a default protocol
        :param teststand_typ: which kind of test stand, later important to define refpoints at the measuring station for the
        robot.

        :param teststand_uniqueID: given from server
        :param teststand_prio: testsystem/program prio
        :param datalength: length in [Bytes]
        """

        protocol_msg = int.from_bytes(teststand_typ, byteorder='big') << tt_shift \
                    | int.from_bytes(teststand_uniqueID, byteorder='big') << tu_shift \
                    | int.from_bytes(teststand_prio, byteorder='big') << tp_shift \
                    | int.from_bytes(status_default, byteorder='big') << sb_shift \
                    | int.from_bytes(datalength, byteorder='big') << dl_shift

        self.protocol_msg = protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')

    def setProtocol(self, whole_protocol):
        """
        Resets the protocol, checks the length and type (bytes), both will be the protocol_msg
        set again 
        :param whole_protocol: protocol which should be the new one
        :return:
        """
        if len(whole_protocol) >= 16 and isinstance(whole_protocol, bytes):
            self.protocol_msg = whole_protocol
        else:
            print("wrong len or type in setProtocol")
            print("protocol was: ", whole_protocol)

    def build_Statusabbild(self, allgemein_status=_1_allgemein_default, testsystem_status=_2_testsystem_default,
                           reserve=_3_reserve_default):
        """       
		Composes the overall status image and writes it to the status_bytes array
        :param allgemein_status:
        :param testsystem_status:
        :param reserve:
        :return:
        """
        self.protocol_msg = int.from_bytes(reserve, byteorder='big') << reserve_shift \
                            | int.from_bytes(testsystem_status, byteorder='big') << testsystem_status_shift \
                            | int.from_bytes(allgemein_status, byteorder='big') << allgemeine_status_shift
        self.protocol_msg = self.protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')

    def set_ID(self, system_id, data='\x00'):
        """
		sets the uniqueID in the byte [0]
        Integrate the uniqueID queried by the server into the overall image
        :type data:
        :param system_id:
        :return:
        """

        reset = b'\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'

        if len(self.protocol_msg) == 16:
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(self.protocol_msg, byteorder='big')
            if isinstance(system_id, int):
                system_id = int.to_bytes(system_id, 1, byteorder='big')
            protocol_msg = protocol_msg | int.from_bytes(system_id, byteorder='big') << tu_shift
            self.protocol_msg = protocol_msg.to_bytes(16, byteorder='big')
        elif len(data) == 16:
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(data, byteorder='big')
            if isinstance(system_id, int):
                system_id = int.to_bytes(system_id, 1, byteorder='big')
            protocol_msg = protocol_msg | int.from_bytes(system_id, byteorder='big') << tu_shift
            self.protocol_msg = protocol_msg.to_bytes(16, byteorder='big')

    def set_teststand(self, teststandtype):
        """
		Defintion what kind of test stand it is, according to the coding to prove
        :param teststandtype:
        :return:

        """

        reset = b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'

        # try:

        if len(self.protocol_msg) == 16:
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(self.protocol_msg, byteorder='big')
            if isinstance(teststandtype, int):
                teststandtype = int.to_bytes(teststandtype, 1, byteorder='big')
            protocol_msg = protocol_msg | int.from_bytes(teststandtype, byteorder='big') << tt_shift
            self.protocol_msg = protocol_msg.to_bytes(16, byteorder='big')



    def set_Reserve(self, reserve):

        reset = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\xff\xff'

        # try:

        if len(self.protocol_msg) == 16:
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(self.protocol_msg, byteorder='big')
            if isinstance(reserve, int):
                reserve = int.to_bytes(reserve, 3, byteorder='big')
            protocol_msg = protocol_msg | int.from_bytes(reserve, byteorder='big') << reserve_shift
            self.protocol_msg = protocol_msg.to_bytes(16, byteorder='big')


    def set_datalength(self, datalenght=0):
        """
        :param datalenght:
        :return:
        """
        reset = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00'

        if len(self.protocol_msg) == 16:
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(self.protocol_msg,
                                                                                   byteorder='big')
            if isinstance(datalenght, int):
                datalenght = int.to_bytes(datalenght, 2, byteorder='big')

            protocol_msg = protocol_msg | int.from_bytes(datalenght, byteorder='big')  # << dl_shift
            self.protocol_msg = protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')



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
            state = int.to_bytes(state, 3, byteorder='big')

        if settype == 'set':
            state = int.from_bytes(state, byteorder='big')

            if statetype == 1:
                protocol_msg = int.from_bytes(reset_a, byteorder='big') & int.from_bytes(self.protocol_msg,
                                                                                         byteorder='big')
                protocol_msg = protocol_msg | (state << allgemeine_status_shift)
                self.protocol_msg = protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')

            elif statetype == 2:
                protocol_msg = int.from_bytes(reset_t, byteorder='big') & int.from_bytes(self.protocol_msg,
                                                                                         byteorder='big')
                protocol_msg = protocol_msg | (state << testsystem_status_shift)
                self.protocol_msg = protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')
            else:
                print("nope")

        elif settype == 'reset':
            state = ~int.from_bytes(state, byteorder='big')

            if statetype == 1:
                self.protocol_msg = int.from_bytes(self.protocol_msg, byteorder='big') & (
                            state << allgemeine_status_shift)
                self.protocol_msg = self.protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')
            elif statetype == 2:
                self.protocol_msg = int.from_bytes(self.protocol_msg, byteorder='big') & (
                            state << testsystem_status_shift)
                self.protocol_msg = self.protocol_msg.to_bytes(gesamtMsgBytes, byteorder='big')
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
        state = int.from_bytes(state, byteorder='big')
        if statetype == 1:
            temp = int.from_bytes(self.protocol_msg, byteorder='big') & (state << allgemeine_status_shift)
            return temp
        elif statetype == 2:
            temp = int.from_bytes(self.protocol_msg, byteorder='big') & (state << testsystem_status_shift)
            return temp
        elif statetype == 3:
            temp = int.from_bytes(self.protocol_msg, byteorder='big') & (state << reserve_shift)
            return temp
        else:
            print("nope")


    def reset(self):
        self.protocol_msg = protocol_msg_default

    def reset_without_ID(self):
        reset = b'\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        if len(self.protocol_msg) == 16:
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(self.protocol_msg, byteorder='big')
        elif len(self.protocol_msg) > 16:
            a = self.protocol_msg[len(self.protocol_msg)-16:]
            protocol_msg = int.from_bytes(reset, byteorder='big') & int.from_bytes(a, byteorder='big')
        self.protocol_msg = protocol_msg.to_bytes(16, byteorder='big')

    def getMyID(self):
        return self.protocol_msg[1]
