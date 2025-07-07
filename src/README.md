# LoCo Library Wrapper
The Local Company Library Wrapper

@author Lecce Marco, Mirko Perrone

## Goal 
allow developer to recall library functions 
with just a single http request in their software.

## Usage

request.post(<ip>/<func_name>, json_payload)

## Non-Idealities
### Tuples and Lists
For retrieving from this library a tuple or a list just recall the function 
and transform properly the resulting dictionary:

- Tuples: `tuple(<my_python_http_req>.values())`
- Lists: `list(<my_python_http_req>.values())`

### CORS
By now we are accepting traffic from every IP
in future only from a subset