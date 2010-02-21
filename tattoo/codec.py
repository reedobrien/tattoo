#-*- encoding: utf-8 -*-

## Adapted from http://code.activestate.com/recipes/576435/

## From http://tools.ietf.org/html/rfc1738#section-2.2
## "Thus, only alphanumerics, the special characters "$-_.+!*'(),", and
## reserved characters used for their reserved purposes may be used
## unencoded within a URL."

## The above RFC is updated by http://tools.ietf.org/html/rfc3986#section-2.2
## But I can't make heads or tails of whether it has changed safe chars.
## The old safe chars appear to be labelled as sub-delims. The safety of 
## sub-delims appears to be relegated to "the implementation specific syntax of
## a URI scheme's specification. I don't see anything in the HTTP spec that 
## reserves the characters previously labelled safe. Some text from the RFC follows:

## START QUOTATION From section 2.2

##      reserved    = gen-delims / sub-delims

##      gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"

##      sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
##                  / "*" / "+" / "," / ";" / "="

## A subset of the reserved characters (gen-delims) is used as
## delimiters of the generic URI components described in Section 3.  A
## component's ABNF syntax rule will not use the reserved or gen-delims
## rule names directly; instead, each syntax rule lists the characters
## allowed within that component (i.e., not delimiting it), and any of
## those characters that are also in the reserved set are "reserved" for
## use as subcomponent delimiters within the component.  Only the most
## common subcomponents are defined by this specification; other
## subcomponents may be defined by a URI scheme's specification, or by
## the implementation-specific syntax of a URI's dereferencing
## algorithm, provided that such subcomponents are delimited by
## characters in the reserved set allowed within that component.

## END QUOTATION

## Obviously that means, uh, screw it I am using them.

BASE_CHARS = u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._~$+!*'(),"
## reserved "\\^`{|}"
CHARS = list(BASE_CHARS)

MAX_URL_LEN = 6

map_dict = {}
BASE = len(CHARS)

## total permutations is Base**num_of_digits
## Ex. 10 with 3 digits is 000-999
## or 1000 permutations

## For us that is BASE**MAX_URL_LEN
## With BASE == 75 safe characters that is
## 5 chars == 2,073,071,593
## 6 chars == 151,334,226,289


## This is a two way maping of
## digits <-> chars
for num in range(BASE):
    map_dict[num] = CHARS[num]
    map_dict[CHARS[num]] = num


def encode(num):
    if num == 0:
        return map_dict[0]
    base_str = []
    while num > 0:
        base_str.append(map_dict[ num % BASE ])
        num = num / BASE
    return ''.join(base_str)
        

def decode(short_url):
    L = list(short_url) 
    value = 0
    for i in range(len(L)):
        item = L[i]
        value += (map_dict[item] * pow(BASE,i))
    return value
    
