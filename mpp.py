#!/usr/bin/python
"""
MIPS Preprocessor
by Steve Johnson (srj15@case.edu) and Tim Henderson (tah35@case.edu)

==INCLUDING FILES==
#include your_file.s

==DEFINING MACROS==
#define macro_name [global]
    move %1, %2
#end

Put %n in macros to specify where parameters go.
Add 'global' to the #define line if this macro should be accessible from all other files.

==CALLING MACROS==
    macro_name a b

==USING MACROS IN MACROS==
You can use macros inside other macros as long as the first is defined above the second.

==REGISTER RENAMING==
Define an alias like this:
@my_alias = $t0
Then you can use them just like a register.

==REPETITIONS==
Put "#repeat n" above a line to repeat that line n times.

==SCOPING==
Put curly braces around your code on their own lines to make all labels and aliases valid only within that scope.
"""

import string, sys, re, os

path_prefix = ""
global_macros = {}
main_count = 0
label_count = 0
main_labels = list()
var_split = re.compile(r'\s*=\s*')
strip_comments = False

def get_file_text(f1):
    #process includes
    s = ""
    in_lines = []
    included = []
    for line in f1:
        stripped = line.strip()
        if stripped.startswith("#include"):
            linesplit = stripped.split()
            arg = ' '.join(linesplit[1:])
            if arg not in included:
                included.append(arg)
                f3 = open(os.path.join(path_prefix, arg), 'r')
                text = get_file_text(f3)
                if not strip_comments:
                    text = '\n###'+arg+'###\n' + text + '\n###end '+arg+'###\n'
                f3.close()
                in_lines.append(text)
        else:
            in_lines.append(line)
    return ''.join(in_lines)

def substitute_labels(s):
    global main_count, label_count
    line_list = s.split('\n')
    
    replacements = []
    label_test = re.compile(r'^([a-zA-Z0-9_]+):( |$)')
    label_strip = re.compile(r'__u\d+$')
    in_macro = False
    for line in line_list:
        linestrip = line.strip()
        if linestrip.startswith('#define'): in_macro = True
        if linestrip.startswith('#end'): in_macro = False
        if len(linestrip) > 0 and not in_macro:
            r =  label_test.match(linestrip)
            if r:
                label = r.groups()[0]
                if label == 'main':
                    replacements.append((
                        re.compile(r'\b'+label+r'\b'),
                        label+'_'+str(main_count)
                    ))
                    main_labels.append(label+'_'+str(main_count))
                    main_count += 1
                    if main_count >= max_user_programs:
                        raise Exception, "to many user programs added"
                else:
                    replacements.append((
                        re.compile(r'\b'+label+r'\b'),
                        label_strip.split(label)[0]+'__u'+str(label_count)
                    ))
                    label_count += 1
    for r, new in replacements:
        s = r.sub(new, s)
    return s

def rep_line(line, local_macros, varnames=[]):
    #process macros
    global global_macros
    out_lines = []
    linesplit = line.split()
    if len(linesplit) > 0:
        mtext = ""
        name = linesplit[0]
        #See if first keyword is a local or global macro, set mtext if found
        if string.lower(name) in global_macros.keys():
            mtext = global_macros[name]
        if string.lower(name) in local_macros.keys():
            mtext = local_macros[name]
            
        #if keyword is a macro...
        if mtext != "":
            #if macro has arguments...
            if len(linesplit) > 1:
                #walk comma-delimited arg list
                arg_num = len(linesplit) - 1
                arg_list_string = ' '.join(linesplit[1:])
                arg_list = [t.strip() for t in arg_list_string.split()]
                while arg_num > 0:
                    #replace expression with argument
                    mtext = mtext.replace("%"+str(arg_num), arg_list[arg_num-1])
                    if varnames:
                        for this_scope in reversed(varnames):
                            for k, v in this_scope.items():
                                this_var = re.compile(r'(\s%s[\s$])' % k)
                                mtext = this_var.sub(' %s' % v, mtext)
                    arg_num -= 1
            mtext = substitute_labels(mtext)
            #append macro text (possibly transformed) to output
            out_lines.append(process_lines(mtext, local_macros))
        else:
            out_lines.append(line)
    else:
        out_lines.append(line)
    return out_lines

def rep_names(lines, names):
    
    for i, line in enumerate(lines):
        rep = False
        for name in names.keys():
            nameloc = lines[i].find(name)
            hashsign = lines[i].find('#')
            r = re.compile(r'(\W)'+name+'(\W|$)')
            gs = r.search(lines[i])
            while gs and nameloc != -1 and (nameloc < hashsign or hashsign == -1):
                gs = gs.groups()
                if nameloc != -1 and (nameloc < hashsign or hashsign == -1):
                    rep = True
                    lines[i] = r.sub(gs[0]+names[name]+gs[1], lines[i], 1)
                nameloc = lines[i].find(name)
                hashsign = lines[i].find('#')
                gs = r.search(lines[i])
            if rep and lines[i][-1] != '>':
                line = line.lstrip().rstrip()
                hashsign = line.find('#')
                if hashsign == -1: hashsign = len(line)
                lines[i] += ' # ::-> ' + line[:hashsign] + '>'
        
    
    return lines;

def process_lines(s, local_macros=dict(), toplevel=False):
    global global_macros
    
    in_lines = s.split('\n')
    
    in_macro = False
    is_global = False
    #out_lines = list()
    
    repetitions = 1
    
    macro_name = ""
    scopes = [[]]
    varnames = [dict()]
    cm_varnames = None #current macro variable names
    for line in in_lines:
        kw = string.lower(line.strip())
        if kw.startswith('#define'):
            #start defining macro, get its name and init a list of its lines
            if in_macro: print "Macro error."
            in_macro = True
            linesplit = line.split()
            macro_name = string.lower(linesplit[1])
            is_global = False
            if strip_comments:
                start_text = ''
            else:
                start_text = ' '*4 + '#'*16 + ' start ' + macro_name + ' ' + '#'*16
            if len(linesplit) > 2 and string.lower(linesplit[2]) == 'global':
                is_global = True
            if is_global:
                global_macros[macro_name] = [start_text]
            else:
                local_macros[macro_name] = [start_text]
            cm_varnames = dict()
        elif kw.startswith('#end'):
            #concatenate the lines and stop defining the macro
            in_macro = False
            if strip_comments:
                end_text = ''
            else:
                end_text = ' '*4 + '#'*17 + ' end ' + macro_name + ' ' + '#'*17
            if macro_name in local_macros:
                local_macros[macro_name].append(end_text)
                local_macros[macro_name] = rep_names(local_macros[macro_name], cm_varnames)
                local_macros[macro_name] = "\n".join(local_macros[macro_name])
            if macro_name in global_macros:
                global_macros[macro_name].append(end_text)
                global_macros[macro_name] = rep_names(global_macros[macro_name], cm_varnames)
                global_macros[macro_name] = "\n".join(global_macros[macro_name])
            
            cm_varnames = None
        elif kw.startswith('#repeat'):
            linesplit = line.split()
            if len(linesplit) == 2:
                repetitions = int(linesplit[1])
        elif kw.startswith('{'):
            #print '{'
            scopes.append(list())
            varnames.append(dict())
        elif kw.startswith('}'):
            #print '}'
            l = scopes.pop()
            names = varnames.pop()
            #print l
            lines = substitute_labels('\n'.join(l)).split('\n')
            lines = rep_names(lines, names)
            scopes[-1].extend(lines)
        elif kw.startswith('@'): #variable name
            name = var_split.split(line.lstrip().rstrip())
            if len(name) != 2: raise Exception, 'Syntax Error in variable name line = \n' + line
            if in_macro:
                if cm_varnames.has_key(name[0]):
                    raise Exception, 'Syntax Error name "%s" already defined in current macro "%s"'%\
                                                                                (name[0], macro_name)
                if name[1] in cm_varnames.values():
                    raise Exception, 'Syntax Error reg "%s" already named in current macro "%s"'%\
                                                                                (name[1], macro_name)
                cm_varnames[name[0]] = name[1]
                if macro_name in local_macros:
                    local_macros[macro_name].append('#' + line)
                elif macro_name in global_macros:
                    global_macros[macro_name].append('#' + line)
            else:
                if varnames[-1].has_key(name[0]):
                    raise Exception, \
                    'Syntax Error name "%s" already defined in current scope\n line = "%s"'\
                                                                                   % (name[0], line)
                if name[1] in varnames[-1].values():
                    raise Exception, \
                    'Syntax Error reg "%s" already named in current scope\n line = "%s"'%\
                                                                                (name[1], line)
                varnames[-1][name[0]] = name[1]
                scopes[-1].append('#' + line)
        else:
            if in_macro:
                #check for macro-in-macro
                if macro_name in local_macros.keys():
                    local_macros[macro_name].append(line)
                    #+= rep_line(line, local_macros)
                if macro_name in global_macros.keys():
                    global_macros[macro_name].append(line)
                    #+= rep_line(line, local_macros)
            else:
                #check for regular ol' macro
                scopes[-1] += rep_line(line, local_macros, varnames) * repetitions
                repetitions = 1
    if len(scopes) == 1 and len(varnames) == 1:
        lines = rep_names(scopes[0], varnames[0])
        for i, line in enumerate(lines):
            atsign = line.find('@')
            hashsign = line.find('#')
            if toplevel and atsign != -1 and (atsign < hashsign or hashsign == -1):
                raise Warning, "Syntax error name unconverted on line = '%s'" % line
            if toplevel and line and line[-1] == '>': lines[i] = line[:-1]
            lines[i] = ' '*4 + lines[i].lstrip().rstrip()
        if strip_comments:
            return '\n'.join([l for l in lines if not l.strip().startswith('#') and l.strip() != ''])
        else:
            return '\n'.join(lines)
        
    else:
        raise Exception, "Scoping Error"

def process(path, out, cstrip=False):
    global global_macros, strip_comments, path_prefix
    strip_comments = cstrip
    
    f1 = open(path, 'r')
    path_prefix = os.path.dirname(path)
    
    s = get_file_text(f1)
    s = process_lines(s, toplevel=True)
    
    f1.close()
    #write giant string to file
    f2 = open(out, 'w')
    f2.write(s)
    f2.close()

if __name__ == "__main__":
    #if called from the cl, process with default args
    try:
        infile = sys.argv[1]
        outfile = sys.argv[2]
    except:
        raise Exception, "python mpp.py in_file out_file"
    
    process(infile, outfile)
