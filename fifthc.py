import os, time
def compile(program):
    out = open("out.nexus", "w")
    out.write("func int main\n")
    out.write("set int x\n")
    out.write("set int y\n")
    stringmode = False
    loops = 0
    for x in program:
        if stringmode:
            if x == "\"":
                #Remove previous space
                out.write("putchar " + str(ord("\b"))+"\n")
                stringmode = False
            else:
                for y in x:
                    out.write("putchar " + str(ord(y)) + "\n")
                # Put a space
                out.write("putchar 32\n")
                continue
        try:
            out.write("push " + str(int(x)) + "\n")
        except:
            if x == "+":
                out.write("adds\n")
            elif x == "-":
                out.write("subs\n")
            elif x == "*":
                out.write("muls\n")
            elif x == "/":
                out.write("divs\n")
            elif x == ".":
                out.write("pop x\n")
                out.write("print int x\n")
            elif x == "swap":
                out.write("swaps\n")
            elif x == "dup":
                out.write("pop x\n")
                out.write("push x\n")
                out.write("push x\n")
            elif x == "exit":
                out.write("pop x\n")
                out.write("exit x\n")
            elif x == "%":
                out.write("pop x\n")
                out.write("pop y\n")
                out.write("c_code\n")
                out.write("x = y % x;\n")
                out.write("end_c_code\n")
                out.write("push x\n")
            elif x == ",":
                out.write("c_code\n")
                out.write("scanf(\"%d\", &x);\n")
                out.write("if (x == '\\0'){\n")
                out.write("    printf(\"Error: Unexcpected input!\\n\");\n")
                out.write("    exit(1);\n")
                out.write("}\n")
                out.write("end_c_code\n")
                out.write("push x\n")
            elif x == "if":
                out.write("pop x\n")
                out.write("pop y\n")
                out.write("if ")
            elif x == "eq":
                out.write("eq x y\n")
            elif x == "ne":
                out.write("ne x y\n")
            elif x == "end":
                out.write("end\n")
            elif x == "puts":
                out.write("pop x\n")
                out.write("putchar x\n")
            elif x == "putstr":
                stringmode = True
            elif x == "loop":
                out.write("pop x\n")
                out.write("set int loop_" + str(loops) + " x\n")
                out.write("set int loop_counter_" + str(loops) + " 0\n")
                out.write("loop_until_break\n")
                out.write("add int loop_counter_" + str(loops) + " 1\n")
                out.write("if gt loop_counter_" + str(loops) + " loop_" + str(loops) + "\n")
                out.write("break\n")
                out.write("end\n")
                loops += 1
    out.write("end")
compile_time_start = time.perf_counter()
program = open("program.txt", "r").read().replace("\n"," ").split(" ")
compile(program)
compile_time_end = time.perf_counter()
compile_time = round((compile_time_end - compile_time_start) * 1000 * 1000) # in microseconds
print("Transpile time: " + str(compile_time) + "μs")
compile_time_start = time.perf_counter()
os.system("nexus out.nexus --quiet")
compile_time_end = time.perf_counter()
compile_time = round((compile_time_end - compile_time_start) * 1000)
print("Compile time: " + str(compile_time) + "ms")