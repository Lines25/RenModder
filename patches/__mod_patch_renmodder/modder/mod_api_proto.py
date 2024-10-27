from struct import pack, unpack

CONNECT_CHECK       = 0x00
REGISTER            = 0x01
EVENT_SUBSCRIBE     = 0x02
GET_LOADED_MODS     = 0x03
ACTION_RESULT_FAIL  = 0xFF  # Error code
