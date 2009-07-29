#'./mpp.py test/test1.s'

#include includeme.s



@var = $s0

some_macro @var
li @var

{
    loop:
        #do nothing
}

{
    loop:
        #also do nothing
}