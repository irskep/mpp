==============
= Disclaimer =
==============

mpp was written during the development of a project for a class, so its internal design is suboptimal. Some errors result in an opaque Python stack trace. Some corner cases are not handled.

If you come across one of these nasty errors, feel free to email one of us (srj15@case.edu, tim.tadh@gmail.com) or send us a message on Github (irskep, timtadh).

=========
= Usage =
=========

==Invoking from the command line==

./mpp.py inputfile [outputfile]

==Including files==

#include myfile

MPP does not check to see if a file has already been included.

==Macros==

Since some MIPS simulators don't support macros, MPP includes its own macro engine.

#define mymacro
    li $a0 %1
    othermacro %1 12
#end

Parameters are referenced within macros with %1, %2, etc, which represent the positional arguments. Macros can be called recursively.

To make a macro visible outside of the file it is included from, add 'global' to the #define line.

==Aliases==

To increase readability and maintainability, aliases can be defined for registers or numbers:

@input = $s0
mymacro @input

==Scope==

When writing programs of nontrivial complexity, it can be a pain to keep coming up with new names for labels. To solive this problem, MPP introduces label and alias scoping. If a label or alias is defined within a scope block, it cannot be accessed outside of that block, much like a local variable.

{ 
    @loopvar = $t9 
    li @loopvar 20 
    loop: 
        addi @loopvar @loopvar -1 
        bgtz @loopvar loop 
} 
{ 
    @loopvar = $s0 
    li @loopvar 19 
    loop: 
    addi @loopvar @loopvar -1 
    bgez @loopvar loop
}

=====================
= Style suggestions =
=====================

Macros should be documented by putting at least a line comment describing the paramaters immediately above the definition.

# mymacro some_number
# This macro does something clever.
#define mymacro
    ...
#end

If you have a function call convention, you can scope functions to keep aliases and labels local. Functions should be documented like macros.

# foo arg1 arg2
# This function causes the world to be destroyed
foo:
{
    @bar = $a0
}

