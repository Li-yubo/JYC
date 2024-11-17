from typing import  List, Any
import re
class getValue:
    def __init__(self, key_path):
        self.keyPath = key_path
        # 字典操作
        self.DictOperations = ['init', 'BasicPath_find', 'recursive_find']
        # 列表操作
        self.ListOperations = [ 'index_access', 'wildcard_access', 'conditional_filter', 'recursive_find', 'sort', 'aggregation']
        # 操作匹配正则
        self.patterns = {
            'index_access': r'\[\d+\]|\[\d+:\d+\]|\[\d+:\]|\[:\d+\]',
            'wildcard_access': r'\[\*\]',                    
            'conditional_filter': r'\[\?(?:\\@|[^@\]])+\]',
            'recursive_find': r'\.\.[a-zA-Z0-9]+',                       
            'BasicPath_find': r'(?<!\.)\.[a-zA-Z0-9]+',                        
            'field_access': r'(?<!\\)\@\.',                 
            'aggregation': r'(?<!\\)\@(sum|avg|count|max|min)',     # 聚合操作
            'sort': r'(?<!\\)\@sort\((.*?)\)',              # 排序操作
        }
        self.SETADDKEY = '' # 增加键
        self.SETADDVAL = '' # 修改增加值
        self.GETARR = [] # 输出列表
        self.GETNUM = 1 # 默认输出是1
        self.AGGREGATON = ()
        # 是否修改
        self.set = False
        # 是否添加
        self.add = False
        # 是否删除
        self.delete = False
        # 是否输出
        self.get = False
        self.SETADD = True # 添加修改是否成功
        self.arr = self.parse_query(key_path) # 所有操作列表
        if len(self.arr) > 0 :
            initStr = key_path[:self.arr[0][0]]
            if initStr:
                self.arr.insert(0, (0, 0, 'init', initStr))
        else:
            self.arr = [(0,0,'init', key_path)]
        self.arrNum = len(self.arr)
        self.num = 0
        
        
        for index in range(len(self.arr)):
            #print(self.arr[index][2])
            if (self.arr[index][2] == 'aggregation' and index < len(self.arr)-1)  or (self.arr[index][2] == 'sort' and index < len(self.arr)-1):
                #print("聚合操作只能在结束时使用")
                exit()

                
        if self.arr[len(self.arr)-1][2] == 'aggregation' or self.arr[len(self.arr)-1][2] == 'sort':
            self.AGGREGATON = self.arr[len(self.arr)-1]
            self.arr.pop(-1)
            self.arrNum -= 1
            
        
         
        
        
    def parse_query(self, query: str) -> List[tuple]:
        """解析查询字符串为操作序列"""
        operations = []
        for op_name, pattern in self.patterns.items():
            for match in re.finditer(pattern, query):
                operations.append((match.start(), match.end(), op_name, match.group()))
        return sorted(operations)    

    def _resolve_base_path_Dict(self, name, key) :
        """对象操作方法"""
        if name == 'init':
            return key
        if name == 'BasicPath_find' or name == 'recursive_find': # 递归或者普通路径
            return key.lstrip('.')
        
    def _resolve_base_path_List(self, data, name, key):
        """数组操作方法"""
        def _index_access(data: Any, index_op: str) -> Any:
            """处理数组索引访问"""
            if not isinstance(data, list):
                return []
                
            index_str = index_op.strip('[]')
            if ':' in index_str:
                start, end = map(lambda x: int(x) if x else None, index_str.split(':'))
                
                # 处理 [:] 情况
                if start is None and end is None:
                    return []
                
                # 处理 [:5] 情况
                if start is None:
                    start = 0
                    return list(range(start, end + 1))
                    
                # 处理 [5:] 情况
                if end is None:
                    # 这里需要一个逻辑来决定从start到哪里结束，这里假设到10
                    return list(range(start, len(data)))
                    
                # 处理 [5:5] 情况
                if start == end:
                    return [start]
                    
                # 处理正常情况 [5:10]
                return list(range(start, end))

            try:
                return [int(index_str)]
            except:
                return []
            
        def _conditional_filter(data, filter_op):
            """过滤数据，根据条件，并返回符合条件的下标列表"""
            if not isinstance(data, list):
                return None

            # 去除括号和问号
            condition = filter_op.strip('[]?')
            
            # 正则表达式匹配
            if '~=' in condition:
                field, _, regex_pattern = condition.partition('~=')
                field = field.strip()
                # 移除可能存在的引号
                regex_pattern = regex_pattern.strip().strip('"\'')
                regex = re.compile(regex_pattern)
                
                # 使用 search 而不是 match，并确保转换为字符串
                return [index for index, item in enumerate(data)
                        if isinstance(item, dict) 
                        and field in item 
                        and regex.search(str(item[field]))]

            # 其他比较操作符，添加 '!=' 到列表中
            for op in ['>=', '<=', '>', '<', '==', '!=']:  # 添加 '!='
                if op in condition:
                    field, _, value = condition.partition(op)
                    field = field.strip()
                    value = value.strip()

                    # 转换value为合适的类型
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    elif value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'

                    # 根据操作符执行比较，添加不等于的处理
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
            """处理排序操作"""
            # 从表达式中提取排序参数
            match = re.match(r'@sort\((.*?)\)', op_expr)
            if not match:
                return data
            
            sort_expr = match.group(1)
            
            if not isinstance(data, list):
                return data
            
            # 解析排序表达式
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
            
            # 多重排序
            for field, reverse in reversed(sort_fields):
                data.sort(
                    key=lambda x: (x.get(field) if isinstance(x, dict) else x) if x is not None else '',
                    reverse=reverse
                )
            
            return data    

        def _aggregation_operation(data, op_expr):
            """处理聚合操作"""
            # 从表达式中提取操作类型（sum、avg、count、max、min）
            match = re.match(r'@(sum|avg|count|max|min)', op_expr)
            if not match:
                return data
            
            operation = match.group(1)
            
            if not isinstance(data, list):
                return None
            
            if operation == 'count':
                return len(data)
            
            # 确保数据是数值类型
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
        """最终的增删改查操作"""
        if self.get :
            #print('get === ', data[key])
            self.GETARR.append(data[key])
            if len(self.GETARR) == self.GETNUM:
                #print(self.GETARR)
                self.GETARR.reverse()
                if len(self.GETARR) == 1:
                    self.GETARR = self.GETARR[0]
                if self.AGGREGATON:
                    n, k = self.AGGREGATON[-2:]
                    #print("聚合输出", n, k)
                    self.GETARR = self._resolve_base_path_List(self.GETARR, n,k)
                #print("全部输出")
                #print(self.GETARR)

            
                    
                    
        if self.set:
            data[key] = self.SETADDVAL  # 直接修改字典中的值
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
        递归搜索并修改数据
        :param data: 要搜索的数据结构
        :param keyArr: 路径数组
        :param value: 要设置的新值
        """
        if isinstance(data, dict) and keyArr[0][2] in self.DictOperations:
            for k, v in data.items():
                if self._resolve_base_path_Dict(keyArr[0][2], keyArr[0][3]) == k:
                    # 创建路径数组的副本用于递归
                    newKeyArr = keyArr[1:]
                    if len(newKeyArr) > 0:
                        self.search(num, v, newKeyArr )
                    else:
                        self.operations(data, k)
                else: 
                    if keyArr[0][2] == 'recursive_find': # 递归该如何
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
                        # 检查索引是否在列表的有效范围内
                        if i < len(data):
                            self.search(num, data[i], newKeyArr)  # 传递数组的副本
                        else:
                            print(f"索引 {i} 超出了数据列表的范围。")
                            self.SETADD = False
                
                except IndexError as e:
                    self.GETNUM -= 1
                except Exception as e:
                    self.GETNUM -= 1
        
        else:
            
            print(f"{keyArr[0][3]} 操作符无法匹配到对应的操作值，已终止操作...")
            print(f"当前匹配类型: {type(data)}, 操作符 {keyArr[0][3]} 并不存在该操作中...")
            self.SETADD = False
            return


    def valueGet(self, data):
        self.search(self.num, data, self.arr)
        ##print(self.GETARR)