def foo(arg1,*tupleArg,**dictArg):
    print "arg1=",arg1 
    print type(tupleArg)
    print "tupleArg=",tupleArg 
    print "dictArg=",dictArg  

a = "1"
b = [1, 2, 3]
c = {"a": "b"}
print foo("1", *b, **c)
