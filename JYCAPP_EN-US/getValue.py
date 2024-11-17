from typing import  List, Any
import re
class getValue:
    def __init__(self, key_path):
        self.keyPath = key_path
        # Dictionary Operations
        self.DictOperations = ['init', 'BasicPath_find', 'recursive_find']
        # List Operations
        self.ListOperations = [ 'index_access', 'wildcard_access', 'conditional_filter', 'recursive_find', 'sort', 'aggregation']
        # Operation matching regular expression
        self.patterns = {
            'index_access': r'\[\d+\]|\[\d+:\d+\]|\[\d+:\]|\[:\d+\]',
            'wildcard_access': r'\[\*\]',                    
            'conditional_filter': r'\[\?(?:\\@|[^@\]])+\]',
            'recursive_find': r'\.\.[a-zA-Z0-9]+',                       
            'BasicPath_find': r'(?<!\.)\.[a-zA-Z0-9]+',                        
            'field_access': r'(?<!\\)\@\.',                 
            'aggregation': r'(?<!\\)\@(sum|avg|count|max|min)',     #Aggregation Operations
            'sort': r'(?<!\\)\@sort\((.*?)\)',              # Sorting Operations
        }
        self.SETADDKEY = '' # Add Key
        self.SETADDVAL = '' # Modify the added value
        self.GETARR = [] # Output List
        self.GETNUM = 1 # The default output is 1
        self.AGGREGATON = ()
        # Modify
        self.set = False
        # Add
        self.add = False
        # Delete
        self.delete = False
        # get
        self.get = False
        self.SETADD = True # Add modification successfully
        self.arr = self.parse_query(key_path) # List of all operations
        if len(self.arr) > 0 :
            initStr = key_path[:self.arr[0][0]]
            if initStr:
                self.arr.insert(0, (0, 0, 'init', initStr))
        else:
            self.arr = [(0,0,'init', key_path)]
        self.arrNum = len(self.arr)
        self.num = 0
        
        
        for index in range(len(self.arr)):
            
            if (self.arr[index][2] == 'aggregation' and index < len(self.arr)-1)  or (self.arr[index][2] == 'sort' and index < len(self.arr)-1):
                #print("聚合操作只能在结束时使用")
                exit()

                
        if self.arr[len(self.arr)-1][2] == 'aggregation' or self.arr[len(self.arr)-1][2] == 'sort':
            self.AGGREGATON = self.arr[len(self.arr)-1]
            self.arr.pop(-1)
            self.arrNum -= 1
            
        
         
        
        
    def parse_query(self, query: str) -> List[tuple]:
        """Parse the query string into a sequence of operations"""
        operations = []
        for op_name, pattern in self.patterns.items():
            for match in re.finditer(pattern, query):
                operations.append((match.start(), match.end(), op_name, match.group()))
        return sorted(operations)    

    def _resolve_base_path_Dict(self, name, key) :
        """Object operation methods"""
        if name == 'init':
            return key
        if name == 'BasicPath_find' or name == 'recursive_find': # Recursive or normal path
            return key.lstrip('.')
        
    def _resolve_base_path_List(self, data, name, key):
        """Array operation methods"""
        def _index_access(data: Any, index_op: str) -> Any:
            """Handling array index access"""
            if not isinstance(data, list):
                return []
                
            index_str = index_op.strip('[]')
            if ':' in index_str:
                start, end = map(lambda x: int(x) if x else None, index_str.split(':'))
                
                if start is None and end is None:
                    return []
                
                if start is None:
                    start = 0
                    return list(range(start, end + 1))
                    
                if end is None:
                    return list(range(start, len(data)))
                    
                if start == end:
                    return [start]
                    
                return list(range(start, end))

            try:
                return [int(index_str)]
            except:
                return []
            
        def _conditional_filter(data, filter_op):
            """Filter data according to conditions and return a list of subscripts that meet the conditions"""
            if not isinstance(data, list):
                return None

            # Remove brackets and question marks
            condition = filter_op.strip('[]?')
            
            # Regular expression matching
            if '~=' in condition:
                field, _, regex_pattern = condition.partition('~=')
                field = field.strip()
                # Remove possible quotes
                regex_pattern = regex_pattern.strip().strip('"\'')
                regex = re.compile(regex_pattern)
                
                # Use search instead of match and make sure to convert to a string
                return [index for index, item in enumerate(data)
                        if isinstance(item, dict) 
                        and field in item 
                        and regex.search(str(item[field]))]

            # Other comparison operators, add '!=' to the list
            for op in ['>=', '<=', '>', '<', '==', '!=']:  # add '!='
                if op in condition:
                    field, _, value = condition.partition(op)
                    field = field.strip()
                    value = value.strip()

                    # Convert value to the appropriate type
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    elif value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'

                    # Perform comparison based on the operator and add inequality handling
                    if op == '==':
                        return [index for index, item in enumerate(data) if isinstance(item, dict) and item.get(field) == value]
                    elif op == '!=':
                        return [index for index, item in enumerate(data) if isinstance(item, dict) and item.get(field) != value]
                    elif op == '>':
                        return [index for index, item in enumerate(data) if isinstance(item, dict) and item.get(field) > value]
                    elif op == '<':
                        return [index for index, item in enumerate(data) if isinstance(item, dict) and item.get(field) < value]
                    elif op == '>=':
                        return [index for index, item in enumerate(data) if isinstance(item, dict) and item.get(field) >= value]
                    elif op == '<=':
                        return [index for index, item in enumerate(data) if isinstance(item, dict) and item.get(field) <= value]

            return []

        def _sort_operation( data, op_expr):
            """Processing sort operations"""
            # Extract sort parameters from expressions
            match = re.match(r'@sort\((.*?)\)', op_expr)
            if not match:
                return data
            
            sort_expr = match.group(1)
            
            if not isinstance(data, list):
                return data
            
            # Parsing sort expressions
            sort_fields = []
            for field_expr in sort_expr.split(','):
                field_expr = field_expr.strip()
                if ':' in field_expr:
                    field, direction = field_expr.split(':')
                    reverse = direction.lower() == 'desc'
                else:
                    if field_expr.startswith('-'):
                        field = field_expr[1:]
                        reverse = True
                    else:
                        field = field_expr
                        reverse = False
                sort_fields.append((field.strip(), reverse))
            
            # Multiple sorting
            for field, reverse in reversed(sort_fields):
                data.sort(
                    key=lambda x: (x.get(field) if isinstance(x, dict) else x) if x is not None else '',
                    reverse=reverse
                )
            
            return data    

        def _aggregation_operation(data, op_expr):
            """Handling Aggregation Operations"""
            # Extract operation type from expression (sum, avg, count, max, min)
            match = re.match(r'@(sum|avg|count|max|min)', op_expr)
            if not match:
                return data
            
            operation = match.group(1)
            
            if not isinstance(data, list):
                return None
            
            if operation == 'count':
                return len(data)
            
            # Make sure the data is a numeric type
            numbers = [float(item) for item in data if isinstance(item, (int, float))]
            
            if not numbers:
                return None
            
            if operation == 'sum':
                return sum(numbers)
            elif operation == 'avg':
                return sum(numbers) / len(numbers)
            elif operation == 'max':
                return max(numbers)
            elif operation == 'min':
                return min(numbers)
            
            return None


        if name == 'wildcard_access' or name == 'recursive_find':
            return list(range(len(data)))
        elif name == 'index_access':
            return _index_access(data, key) if isinstance(_index_access(data, key), list) else [_index_access(data, key)]
        elif name == 'conditional_filter':
            return _conditional_filter(data, key) if isinstance(_conditional_filter(data, key), list) else [_conditional_filter(data, key)]
        
        elif name == 'sort':
            _sort_operation(data, key)
            return _sort_operation(data, key)
        elif name == 'aggregation':
            return _aggregation_operation(data, key)
        else:
            pass
        
    def operations(self, data, key):
        """Final CRUD operation"""
        if self.get :
            self.GETARR.append(data[key])
            if len(self.GETARR) == self.GETNUM:
                self.GETARR.reverse()
                if len(self.GETARR) == 1:
                    self.GETARR = self.GETARR[0]
                if self.AGGREGATON:
                    n, k = self.AGGREGATON[-2:]
                    self.GETARR = self._resolve_base_path_List(self.GETARR, n,k)

            
                    
                    
        if self.set:
            data[key] = self.SETADDVAL  
        if self.delete:
            del data[key]
        if self.add:
            if isinstance(data[key], dict):
                data[key][self.SETADDKEY] = self.SETADDVAL    
            elif isinstance(data[key], list):
                try:
                    if int(self.SETADDKEY) < 0 :
                        self.SETADDKEY = 0
                    data[key].insert(int(self.SETADDKEY),self.SETADDVAL)    
                except:
                    data[key].append(self.SETADDVAL)

                
    
    def search(self, num, data=False, keyArr=False,):
        
        if num >= self.arrNum:
            return
        num += 1
        #print(f"{num}、{data}")
        """
            Recursively search and modify data
            :param data: data structure to be searched
            :param keyArr: path array
            :param value: new value to be set
        """
        if isinstance(data, dict) and keyArr[0][2] in self.DictOperations:
            for k, v in data.items():
                if self._resolve_base_path_Dict(keyArr[0][2], keyArr[0][3]) == k:
                    newKeyArr = keyArr[1:]
                    if len(newKeyArr) > 0:
                        self.search(num, v, newKeyArr )
                    else:
                        self.operations(data, k)
                else: 
                    if keyArr[0][2] == 'recursive_find': # How to do recursion
                        if isinstance(v, dict) or isinstance(v, list):
                            self.search(num-1, v, keyArr)
                    
        elif isinstance(data, list) and keyArr[0][2] in self.ListOperations:
            newKeyArr = keyArr[1:]
            indexList = self._resolve_base_path_List(data, keyArr[0][2], keyArr[0][3])
            
            indexList.sort(reverse=True)
            self.GETNUM = len(indexList)
            for i in indexList:
                try:
                    if keyArr[0][2] == 'recursive_find':
                        newKeyArr = keyArr
                        num -= 1
                    if num == self.arrNum:
                        self.operations(data, i)
                    else:
                        # Checks if the index is within the valid range of the list
                        if i < len(data):
                            self.search(num, data[i], newKeyArr)  # Passing a copy of the array
                        else:
                            print(f"index {i} Exceeded the range of data list.")
                            self.SETADD = False
                
                except IndexError as e:
                    self.GETNUM -= 1
                except Exception as e:
                    self.GETNUM -= 1
        
        else:
            
            print(f"{keyArr[0][3]} The operator cannot be matched to the corresponding operation value, and the operation has been terminated....")
            print(f"Current match type: {type(data)}, Operators {keyArr[0][3]} Does not exist in this operation...")
            self.SETADD = False
            return


    def valueGet(self, data):
        self.search(self.num, data, self.arr)