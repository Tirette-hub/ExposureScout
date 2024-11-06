# octets
It provides dynamic compression mecanism for Integer values thanks to VarInt. The mecanism is itself based on the one used by the _QUIC_ protocol.

**length (bytes)**|**values encoded**|**prefix**|**value mask**|**binary representation**
:---:|:---:|:---:|---|---
1|5 => 0 - 31|00|1F|000x xxxx
2|13 => 32 - 8,191|20|1F FF|001x xxxx xxxx xxxx
3|21 => 8,192 - 2,097,151|40|1F FF FF|010x xxxx ... xxxx xxxx
4|29 => 2,097,152 - 536,870,911|60|1F FF FF FF|011x xxxx ... xxxx xxxx
5|37 => 536,870,912 - 2^(37)-1|80|1F FF FF FF FF|100x xxxx ... xxxx xxxx
6|45 => 2^(37) - 2^(45)-1|A0|1F FF FF FF FF FF|101x xxxx ... xxxx xxxx
7|53 => 2^(45) - 2^(53)-1|C0|1F FF FF FF FF FF FF|110x xxxx ... xxxx xxxx
8|61 => 2^(53) - 2^(61)-1|E0|1F FF FF FF FF FF FF FF|111x xxxx ... xxxx xxxx

Note that the mask used to know the prefix is only 1 byte long and is _0xE0_ since we only need the first byte to know the varint length. After checking the prefix,
we know the length and therefore can get as many bytes we need to decode the value, applying the right mask.
Length increases linearly compared to the exponential used within QUIC (1, 2, 4, 8) so we can encode values on lower amount of bytes.

In practice, here we should not get values encoded on more than 32 bits, so the biggest varint length we should encounter in this project is 5 bytes long. We can accept this little increasing of one byte compared to the regular encoding for integer values since the majority of the covered integer values here are at worst encoded on 4 bytes as well.

---------------------------------------------------
## Index
* [octets](#octets)
    - [VarInt](#varint)
        - [to_bytes](#to_bytesvalue)
        - [get_len](#get_lenb_array)
        - [from_bytes](#from_bytesb_array)

---------------------------------------------------

## VarInt
### to_bytes(*__value__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Converts an interger value to a varint byte stream. (0 <--> (2\*\*61)-1)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_value_ (int): the value to convert.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A byte string.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Raises*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_ValueError_: if negative or too great value has been provided.

### get_len(*__b_array__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Get the length in bytes of the varint value a byte array begins with.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_array_ (bytes): a byte stream.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The length of the varint value the byte array begins with.

### from_bytes(*__b_array__*)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**_STATIC_** Read a byte string to extract its varint value.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Arguments*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_b_array_ (bytes): a byte stream.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Returns*:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The recovered value.