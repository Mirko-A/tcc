PRINT "How many fibonacci numbers do you want?"
INPUT nums
PRINT ""

LET a = 0

IF a > 0 THEN
    PRINT "True"
ENDIF

LET b = 1
WHILE nums > 0 REPEAT
    PRINT a
    LET c = a + b
    LET a = b
    LET b = c
    LET nums = nums - 1
ENDWHILE