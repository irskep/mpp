    
    ###includeme.s###
    # Check it out, I'm included!
    
    ###end includeme.s###
    
    
    
    #@var = $s0
    
    ################ start some_macro ################
    li $a0 $s0    # I'm in a macro!
    ################# end some_macro #################
    li $s0 # ::-> li @var
    
    loop__u0:
    #do nothing
    
    loop__u1:
    #also do nothing