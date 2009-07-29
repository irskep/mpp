#include includeme.s

#define some_macro
    li $a0 %1
    # I'm in a macro!
#end

@var = 12

some_macro @var

{
    loop:
        #do nothing
}

{
    loop:
        #also do nothing
}