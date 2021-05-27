# Thompson's-Rule

# For p1.py
## How to run
Run this command:
```bash
python p1.py '<re itself>'
```
Or just run the command:
```bash
python p1.py 
```
and then you will be prompted afterwards to input the regular expression.

## Assumptions
1- The underscore symbol '_' was used to handle the square brackets so it can't be used in the input regular expression.

2- The dot symbol '.' was used to handle the concatenation so it can't be used in the input regular expression.

3- We always start with S0 as the initial state, sort of like a naming convention.

4- We always have one final state meaning that even if there is originally more than one final state, they'll go with ε to one common final state.

5- In concatention, we don't use ε between the transition in states.


## Valid Regular Expressions:
You can use any alphabet or numeric. Also, you can use square [] and round () brackets.
You can enter any special characters. The drawing library though might not be able to handle drawing it.



# For p2.py
## How to run
1- Place the nfa.json file with the p2.py file in the same folder 

2- Run the command:
```bash
python p2.py 
```
3- The output dfa.json file will appear in the same folder

