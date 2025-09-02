def simple_calculator(a, b, operation):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        return "Invalid operation"



print(simple_calculator(10, 5, "add"))        
print(simple_calculator(10, 5, "subtract"))   
print(simple_calculator(10, 5, "multiply"))   
print(simple_calculator(10, 5, "divide"))     
print(simple_calculator(10, 5, "invalid"))    