# Thompson's-Rule

## How to run
Just run the command
```bash
python p1.py 
```
and you will be prompted afterwards to input the regular expression


## Assumptions
1- The underscore symbol '_' was used to handle the square brackets so it can't be used in the input regular expression

2- We always start with S0, sort of like a naming convention.

3- We always have one final state meaning that even if there is originally more than one final state, they'll go with ε to one common final state.

4- In concatention, we don't use ε between the transition in states.
