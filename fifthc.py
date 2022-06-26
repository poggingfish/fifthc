#!/usr/bin/env python
import os, time, sys
out = open("out.c", "w")
preprocessor_vars = {}
preprocessor_str_const = {}
preprocessor_env = []
macros = {}
words = {}
imports = [sys.argv[1]]
preprocessed = []
stringmode = False
strbuffer = ""
comment = False
loops = 0
current_loop = 0
index = -1
procs = []
proc = False
def preprocess(program, main=True):
    global preprocessed
    program = program.split("\n")
    index = -1
    for x in program:
        if not x.startswith("#"):
            index += len(x.split(" "))
            continue
        x = x.replace("#", "")
        x = x.split(" ")
        if x[0] == "CONST":
            preprocessor_vars[x[1]] = int(x[2])
        elif x[0] == "SCONST":
            preprocessor_str_const[x[1]] = " ".join(x[2:])
        elif x[0] == "MACRO":
            macros[x[1]] = x[2:]
        elif x[0] == "WORD":
            words[x[1]] = x[2:]
        elif x[0] == "process":
            if x[1] not in imports:
                if os.path.exists("./"+x[1]):                        
                    print("processing: " + x[1])
                    imports.append(x[1])
                    preprocess(open(x[1],"r").read(), False)
                elif os.path.exists("/opt/fifthc/"+x[1]):
                    print("processing: " + x[1])
                    imports.append(x[1])
                    preprocess(open("/opt/fifthc/"+x[1],"r").read(), False)
        elif x[0] == "include":
            old_preprocessed = preprocessed
            preprocessed = []
            if x[1] not in imports:
                if os.path.exists("./"+x[1]):                        
                    print("compiling: " + x[1])
                    imports.append(x[1])
                    preprocess(open(x[1],"r").read())
                    compile(open(x[1],"r").read().replace("\n"," ").replace("\t","").split(" "))
                elif os.path.exists("/opt/fifthc/"+x[1]):
                    print("compiling: " + x[1])
                    imports.append(x[1])
                    preprocess(open("/opt/fifthc/"+x[1],"r").read())
                    compile(open("/opt/fifthc/"+x[1],"r").read().replace("\n"," ").replace("\t","").split(" "))
            else:
                print("[INFO] Skipped "+x[1] + " because its already compiled")
            preprocessed = old_preprocessed
        if main:
            for _ in range(len(x)+1):
                preprocessed.append(index+_)
            index+=len(x)
def pop(var):
    out.write(var + " = stack[--stack_ptr];\n")
def push(value):
    out.write("stack[stack_ptr++] = " + str(value) + ";\n")
def adds():
    pop("x")
    pop("y")
    out.write("x = x + y;\n")
    push("x")
def subs():
    pop("x")
    pop("y")
    out.write("x = x - y;\n")
    push("x")
def muls():
    pop("x")
    pop("y")
    out.write("x = x * y;\n")
    push("x")
def divs():
    pop("x")
    pop("y")
    out.write("x = x / y;\n")
    push("x")
def compile(program):
    global out
    global preprocessed
    global preprocessor_vars
    global preprocessor_str_const
    global funcs
    global stringmode
    global strbuffer
    global proc
    global comment
    global loops
    global current_loop
    global index
    global words
    for x in program:
        index+=1
        if index in preprocessed:
            continue
        if stringmode:
            if x == "\"":
                out.write("strcpy(strings[ssp++],\"{}\");\n".format(strbuffer[0:-1]))
                stringmode = False
                strbuffer = ""
                continue
            else:
                strbuffer += x + " "
                continue
        if comment:
            if x == "//":
                comment = False
            continue
        if proc:
            out.write(x+"(){\n")
            procs.append(x)
            proc = False
            continue
        try:
            push(str(int(x)))
        except:
            if x in procs:
                out.write("proc_"+x+"();\n")
            elif x in words:
                compile(words[x])
            elif x.startswith("p!"):
                push(str(preprocessor_vars[x.replace("p!","")]))
            elif x.startswith("p$"):
                compile(macros[x.replace("p$","")])
            elif x.startswith("p@"):
                out.write("strcpy(strings[ssp++],\"{}\");\n".format(preprocessor_str_const[x.replace("p@","")]))
            elif x.startswith("'"):
                push(str(ord(x[1])))
            elif x == "+":
                adds()
            elif x == "-":
                subs()
            elif x == "*":
                muls()
            elif x == "/":
                divs()
            elif x == "exit":
                pop("x")
                out.write("exit(x);")
            elif x == "%":
                pop("x")
                pop("y")
                out.write("x = y % x;\n")
                push("x")
            elif x == ",":
                out.write("scanf(\"%d\", &x);\n")
                push("x")
            elif x == "if":
                pop("x")
                pop("y")
                out.write("if (")
            elif x == "==":
                out.write("x == y){\n")
            elif x == "!=":
                out.write("x != y){\n")
            elif x == ">":
                out.write("x > y){\n")
            elif x == "<":
                out.write("x < y){\n")
            elif x == "<=":
                out.write("x <= y){\n")
            elif x == ">=":
                out.write("x >= y){\n")
            elif x == "end":
                out.write("}\n")
            elif x == "endl":
                out.write("}\n")
                current_loop -= 1
            elif x == '"':
                stringmode = True
            elif x == "loop":
                pop("x")
                out.write("int loop_" + str(loops) + " = x;\n")
                out.write("int loop_counter_" + str(loops) + "= 0;\n")
                out.write(f"while(loop_counter_{str(loops)} < loop_{str(loops)})"+"{\n")
                out.write(f"loop_counter_"+str(loops)+"++;\n")
                loops += 1
                current_loop += 1
            elif x == "setvar":
                pop("x")
                pop("y")
                out.write("variables[x] = y;\n")
            elif x == "getvar":
                pop("x")
                out.write("y = variables[x];\n")
                push("y")
            elif x == "//":
                comment = True
            elif x == "loopf":
                out.write("while(1){")
            elif x == "break":
                out.write("break;\n")
            elif x == "sleep":
                pop(x)
                out.write("usleep(x*1000);\n")
            elif x == "fflush":
                pop(x)
                out.write("fflush(FILE_BUFFER[x]);\n")
            elif x == "cwrite":
                pop("x")
                pop("y")
                out.write("fputc((char)y,  FILE_BUFFER[x]);\n")
            elif x == "swrite":
                pop("x")
                out.write("fputs(strings[--ssp],FILE_BUFFER[x]);\n")
            elif x == "ofw": # open file write
                pop("x")
                out.write("if (x >= 10){\n")
                out.write("printf(\"File number too large!\\n\");\n")
                out.write("exit(1);\n")
                out.write("}\n")
                out.write("FILE_BUFFER[x] = fopen(strings[--ssp], \"w\");\n")
                out.write("if (FILE_BUFFER == NULL){\n")
                out.write("printf(\"File error!\\n\");")
                out.write("exit(1);\n")
                out.write("}\n")
            elif x == "close":
                pop("x")
                out.write("if (FILE_BUFFER[x] == NULL){")
                out.write("printf(\"ERROR: File never opened..\\n\");\n")
                out.write("exit(1);}\n")
                out.write("fclose(FILE_BUFFER[x]);\n")
            elif x == "continue":
                out.write("continue;\n")
            elif x == "plc":
                out.write("x = loop_counter_"+str(current_loop-1)+";\n")
                push("x")
            elif x == "its":
                pop("x")
                out.write("sprintf(strings[ssp++], \"%"+"d\", x);\n")
            elif x == "sti":
                out.write("x = atoi(strings[--ssp]);\n")
                push("x")
            elif x == "argv":
                pop("x")
                out.write("strcpy(strings[ssp++], argv[x]);\n")
            elif x == ">R":
                pop("x")
                out.write("temp[tsp++] = x;\n")
            elif x == "R>":
                out.write("x = temp[--tsp];\n")
                push("x")
            elif x == "@>R":
                pop("x")
                out.write("temp[tsp++] = x;\n")
                push("x")
            elif x == "strdup":
                out.write("strcpy(sb1,strings[--ssp]);\n")
                out.write("strcpy(strings[ssp++],sb1);\n")
                out.write("strcpy(strings[ssp++],sb1);\n")
            elif x == "strcmp":
                out.write("if(strcmp(strings[--ssp],strings[--ssp]) == 0){\n")
                push(1)
                out.write("}\n")
                out.write("else{\n")
                push(0)
                out.write("}\n")
            elif x == "proc":
                out.write("int proc_")
                proc = True
if sys.argv[1] == "install":
    os.system("cp ./fifthc.py /usr/bin/fifthc")
    print(" ./fifthc.py > /usr/bin/fifthc ")
    os.system("cp ./std.fc /opt/fifthc/std.fc")
    print(" ./std.fc > /opt/fifthc/std.fc ")
    os.system("cp ./colors.fc /opt/fifthc/colors.fc")
    print(" ./colors.fc > /opt/fifthc/colors.fc ")
    print("Installed!")
    print("Testing..")
    os.system("fifthc test.fc && ./fout")
    os.remove("fout")
    exit()
def com():
    out.write("#include <unistd.h>\n")
    out.write("#include <stdio.h>\n")
    out.write("#include <stdlib.h>\n")
    out.write("#include <string.h>\n")
    out.write("#include <math.h>\n")
    out.write("int x,y;\n")
    out.write("FILE * FILE_BUFFER[11];\n")
    out.write("char sb1[512];\n")
    out.write("char sb2[512];\n")
    out.write("int stack[1024];\n")
    out.write("int stack_ptr = 0;\n")
    out.write("int variables[512];\n")
    out.write("int temp[10];\n")
    out.write("int tsp;\n")
    out.write("char strings[20][512];\n")
    out.write("int ssp;\n")
    compile_time_start = time.perf_counter()
    preprocessor_program = open(sys.argv[1], "r").read()
    preprocess(preprocessor_program)
    program = open(sys.argv[1], "r").read().replace("\n"," ").replace("\t","").split(" ")
    compile(program)
    out.write("int main(int argc, char *argv[]){\n")
    out.write("FILE_BUFFER[10] = stdout;\n")
    out.write("proc_main();}\n")
    out.close()
    compile_time_end = time.perf_counter()
    compile_time = round((compile_time_end - compile_time_start) * 1000 * 1000) # in microseconds
    print("Transpile time: " + str(compile_time) + "μs")
    compile_time_start = time.perf_counter()
    os.system("gcc out.c -o fout")
    #os.remove("out.c")
    compile_time_end = time.perf_counter()
    compile_time = round((compile_time_end - compile_time_start) * 1000)
    print("Compile time: " + str(compile_time) + "ms")
com()